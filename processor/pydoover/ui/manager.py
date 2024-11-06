import copy
import enum
import inspect
import logging
import time
from datetime import datetime

from typing import Union, Any, Optional, TypeVar, TYPE_CHECKING

from .element import Element
from .interaction import SlimCommand, Interaction, NotSet
from .submodule import Container
from .variable import Variable

from ..cloud.api import Client

if TYPE_CHECKING:
    from ..docker.device_agent.device_agent import device_agent_iface


log = logging.getLogger(__name__)
ElementT = TypeVar("ElementT", bound=Element)
InteractionT = TypeVar("InteractionT", bound=Interaction)


class ShouldPushUpdate(enum.Enum):
    push_and_log = 1
    push_only = 2
    do_nothing = 3


class UIManager:
    def __init__(
        self,
        agent_id: str = None,
        client: Union[Client, "device_agent_iface"] = None,
        auto_start: bool = False,
        min_ui_update_period: int = 600,
        min_observed_update_period: int = 4,
    ):
        self.client = client
        # to determine whether we can use event-based logic
        self._has_persistent_connection = hasattr(client, "dda_uri")
        self._subscriptions_ready = False

        self.agent_id = agent_id

        self.last_ui_state = dict()  # A python dictionary of the full state from the cloud
        self.last_ui_state_update = None

        self.last_ui_state_wss_connections = dict()
        self.last_ui_state_wss_connections_update = None

        self.last_ui_cmds = dict()
        self.last_ui_cmds_update = None

        self._base_container = Container(name=None, display_name=None)
        self._interactions: dict[str, Interaction] = dict()

        self._has_critical_interaction_pending: bool = False
        # self._has_critical_ui_state_pending: bool = False
        self._critical_values = dict()  # legacy

        self.min_ui_update_period = min_ui_update_period
        self.min_observed_update_period = min_observed_update_period
        self._last_pushed_time = None

        # legacy, list of subscriptions to call when we have a command update.
        self._cmds_subscriptions = []

        if auto_start:
            self.start_comms()

    def start_comms(self):
        self._setup_subscriptions()

    def _is_conn_ready(self, setup: bool = False) -> bool:
        if not self._has_persistent_connection:
            return self.client is not None

        if self._subscriptions_ready:
            return True
        elif setup:
            self._setup_subscriptions()
            return self._is_conn_ready(setup=False)  # don't setup for a second time
        else:
            log.error("Attempted use of dda_iface in ui_manager without dda_iface being ready")
            return False

    def is_connected(self) -> bool:
        if not self._has_persistent_connection:
            return self._is_conn_ready()

        if not self._is_conn_ready():
            return False

        return self.client.get_is_dda_online()

    get_is_connected = is_connected

    def is_being_observed(self):
        if not self.last_ui_state_wss_connections:
            return False

        try:
            connections = self.last_ui_state_wss_connections["connections"]
            # The following isn't working currently as agent_id is None
            # for k in connections.keys():
            #     if k != self.agent_id and connections[k] is True:
            #         return True

            # if there is more than one connection, then we are being observed
            return len(connections.keys()) > 1
        except KeyError:
            return False

    def has_been_connected(self):
        if self._has_persistent_connection and self.client is not None:
            return self.client.get_has_dda_been_online()
        return self.last_ui_state is not None

    get_has_been_connected = has_been_connected

    def _setup_subscriptions(self):
        if not self._has_persistent_connection:
            log.error("Attempted to setup subscriptions without valid connection client.")
            return

        if self.client is None:
            log.warning("Attempted to setup subscriptions without client being set")
            return

        log.info("Setting up dda subscriptions")
        self.client.add_subscription("ui_state", self.on_state_update)
        self.client.add_subscription("ui_state@wss_connections", self.on_state_wss_update)
        self.client.add_subscription("ui_cmds", self.on_command_update)

        self._subscriptions_ready = True

    def on_state_update(self, _, aggregate: dict[str, Any]):
        self._set_new_ui_state(aggregate)

    def on_state_wss_update(self, _, aggregate: dict[str, Any]):
        self.last_ui_state_wss_connections = aggregate
        self.last_ui_state_wss_connections_update = time.time()

    def on_command_update(self, _, aggregate: dict[str, Any]):
        prev_agg = copy.deepcopy(self.last_ui_cmds)
        aggregate = self._set_new_ui_cmds(aggregate)

        # call all subscribed to cmds updates
        for c in self._cmds_subscriptions:
            c()

        # add commands that don't currently exist
        to_add = {k: v for k, v in aggregate.items() if k not in self._interactions}
        for name, current_value in to_add.items():
            self._interactions[name] = SlimCommand(name, current_value)

        # work out command diff and call individual commands
        changed = {c: v for c, v in aggregate.items() if v != prev_agg.get(c)}
        for command_name, new_value in changed.items():
            command = self.get_command(command_name)
            if command is not None:
                command._handle_new_value(new_value)

    def _set_new_ui_cmds(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            payload = {}

        try:
            payload = payload["cmds"]
        except KeyError:
            pass

        self.last_ui_cmds = payload
        self.last_ui_cmds_update = time.time()
        return payload

    def _set_new_ui_state(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            payload = {}

        try:
            payload = payload["state"]
        except KeyError:
            pass

        self.last_ui_state = payload
        self.last_ui_state_update = time.time()
        return payload

    def _add_interaction(self, interaction: Interaction):
        self._interactions[interaction.name] = interaction
        interaction._manager = self

    def _remove_interaction(self, interaction_name: str) -> None:
        try:
            del self._interactions[interaction_name]
        except KeyError:
            return

    def add_interaction(self, interaction: InteractionT):
        if not isinstance(interaction, Interaction) and hasattr(interaction, "_ui_type"):
            interaction = self._register_interaction(interaction, interaction.__self__)

        self._add_interaction(interaction)
        self._base_container.add_children(interaction)

    @staticmethod
    def _register_interaction(func, parent) -> InteractionT:
        item = func._ui_type(**func._ui_kwargs)
        item.callback = func

        try:
            setattr(parent, func.__name__, item)
        except AttributeError:
            pass  # maybe they've initialised the function w/o a class

        return item

    def register_interactions(self, obj_to_search):
        for name, func in inspect.getmembers(
            obj_to_search, predicate=lambda f: inspect.ismethod(f) and hasattr(f, "_ui_type")
        ):
            self._register_interaction(func, obj_to_search)

    def get_interaction(self, name: str) -> Optional[Interaction]:
        try:
            return self._interactions[name]
        except KeyError:
            return None

    add_command = add_interaction
    get_command = get_interaction

    def coerce_command(self, command_name: str, value: Any, critical: bool = False) -> None:
        command = self.get_command(command_name)
        if command is None:
            log.info(f"Tried to coerce command {command_name} that doesn't exist.")
            return

        command.coerce(value, critical=critical)

    def get_element(self, element_name: str) -> Optional[ElementT]:
        return self._base_container.get_element(element_name)

    def update_variable(self, variable_name: str, value: Any, critical: bool = False) -> bool:
        element = self._base_container.get_element(variable_name)
        if not (element and isinstance(element, Variable)):
            return False

        if critical is True and element.current_value != value:
            self._has_critical_interaction_pending = True

        element.current_value = value
        return True

    def add_cmds_update_subscription(self, callback):
        # fixme: create alias or something
        self._cmds_subscriptions.append(callback)

    def get_all_interactions(self) -> list[Interaction]:
        return list(self._interactions.values())

    def get_all_interaction_names(self) -> list[str]:
        return list(self._interactions.keys())

    get_available_commands = get_all_interaction_names

    def record_critical_value(self, name, value):
        log.warning("this function is deprecated. use the critical=True parameter of another appropriate function.")
        if self._critical_values.get(name) == value:
            return

        self._critical_values[name] = value
        self._has_critical_interaction_pending = True
        # self._has_critical_ui_state_pending = True

    def _should_push_update(self) -> ShouldPushUpdate:
        if self._has_critical_interaction_pending:
            return ShouldPushUpdate.push_and_log
        if self._last_pushed_time is None:
            return ShouldPushUpdate.push_and_log

        since_last_push = time.time() - self._last_pushed_time
        if since_last_push > self.min_ui_update_period:
            return ShouldPushUpdate.push_and_log
        elif self.is_being_observed() and since_last_push > self.min_observed_update_period:
            return ShouldPushUpdate.push_only

        return ShouldPushUpdate.do_nothing

    def handle_comms(self, force_log: bool = False):
        should_push = self._should_push_update()

        if force_log is False and should_push is ShouldPushUpdate.do_nothing:
            return  # don't need to push anything yet...

        self.push(record_log=force_log or should_push is ShouldPushUpdate.push_and_log)

    def _publish_to_channel(self, channel_name: str, data: dict[str, Any], record_log: bool = True, timestamp: Optional[datetime] = None, **kwargs):
        # this purely exists to provide cross-compatibility between clients (hence private method).
        if isinstance(self.client, Client):
            channel = self.client.get_channel_named(channel_name, self.agent_id)
            return channel.publish(data, save_log=record_log, timestamp=timestamp, **kwargs)
        else:
            # fixme: allow for timestamp in DDA message publishing...
            return self.client.publish_to_channel(channel_name, data, record_log=record_log, **kwargs)

    def pull(self):
        if isinstance(self.client, Client):
            ui_cmds = self.client.get_channel_named("ui_cmds", self.agent_id)
            ui_state = self.client.get_channel_named("ui_state", self.agent_id)

            ui_cmds_agg = ui_cmds.fetch_aggregate()
            ui_state_agg = ui_state.fetch_aggregate()
        else:
            ui_cmds_agg = self.client.get_channel_aggregate("ui_cmds")
            ui_state_agg = self.client.get_channel_aggregate("ui_state")

        self._set_new_ui_state(ui_state_agg)
        
        # self._set_new_ui_cmds(ui_cmds_agg)
        self.on_command_update(None, ui_cmds_agg)

    def push(self, record_log: bool = True, should_remove: bool = True, timestamp: Optional[datetime] = None, even_if_empty: bool = False) -> bool:
        # self.check_dda()
        if self._has_persistent_connection:
            if not self._is_conn_ready():
                log.warning("Attempted to push config without ready connection client.")
                return False
            elif not self.client.get_has_dda_been_online():
                # for a persistent connection, don't push if we haven't first pulled last data
                # HTTP-based connections will do a pull before pushing so that is fine.
                log.warning("Attempted to push config without DDA being online.")
                return False
            elif self.last_ui_state_update is None:
                log.warning("Waiting for UI state update to be pulled before pushing...")
                return False
            elif self.last_ui_cmds_update is None:
                log.warning("Waiting for UI commands to be pulled before pushing...")
                return False
        else:
            self.pull()  # do a pull before HTTP client pushes anything...

        print("pushing...")
        commands_update = self._get_commands_update()
        if commands_update is not None:
            ui_cmds_msg = {"cmds": commands_update}
            self._publish_to_channel("ui_cmds", ui_cmds_msg, timestamp=timestamp)

        ui_state_update = self._get_ui_state_update(should_remove=should_remove)
        if ui_state_update is not None:
            self._publish_to_channel("ui_state", ui_state_update, record_log=record_log, timestamp=timestamp)
        elif even_if_empty:
            print("pushing empty ui state")
            self._publish_to_channel("ui_state", {}, record_log=record_log, timestamp=timestamp)
        else:
            print("not pushing empty ui state")

        self._last_pushed_time = time.time()
        self._has_critical_interaction_pending = False
        return True

    def clear_ui(self):
        # this could be dangerous...
        log.info("Clearing UI")
        self._publish_to_channel("ui_state", {"state": None})

    def _get_commands_update(self) -> Optional[dict[str, Any]]:
        cloud_commands = copy.deepcopy(self.last_ui_cmds)
        local_commands = {k: v._json_safe_current_value() for k, v in self._interactions.items()}

        # don't include commands that are the same as the cloud, and values that aren't set
        result = {
            name: value for name, value in local_commands.items()
            if cloud_commands.get(name) != value and value != NotSet
        }

        log.debug("Last Commands: " + str(cloud_commands))
        log.debug("New Commands: " + str(local_commands))
        log.debug("Commands Update: " + str(result))

        # don't clean up commands that exist upstream but not locally for now.
        result.update({c: None for c in cloud_commands.keys() if c not in local_commands})

        if len(result) == 0:
            return None
        return result

    def _get_ui_state_update(self, should_remove: bool = True) -> Optional[dict[str, Any]]:
        cloud_state = self.last_ui_state or {}
        # this recursively evaluates and finds the diff on all children, rather than trying to do the diff here
        result = self._base_container.get_diff(cloud_state, remove=should_remove)

        log.debug("Last UI State: " + str(cloud_state))
        log.debug("New UI State: " + str(self._base_container.to_dict()))
        log.debug("UI State Update: " + str(result))

        if not result or len(result) == 0:
            return None

        return {"state": result}

    def _maybe_add_interaction_from_elems(self, *elements: Union[Element, Container]) -> list[Element]:
        to_return = []
        for element in elements:
            # this is a bit hacky, but it's to stop passing in an unregistered interaction (ie. created with a decorator
            # outside of a submodule and hasn't been registered yet),
            # instead we'll silently register it and proceed as-is
            if not isinstance(element, Interaction) and hasattr(element, "_ui_type"):
                element = self._register_interaction(element, element.__self__)

            if isinstance(element, Container):
                self._maybe_add_interaction_from_elems(*element.children)
            elif isinstance(element, Interaction):
                self._add_interaction(element)
            to_return.append(element)

        return to_return

    def add_children(self, *children: Element) -> None:
        if len(children) == 1 and isinstance(children[0], list):
            # for backwards compatibility, this used to accept a single list of children
            children = children[0]

        updated = self._maybe_add_interaction_from_elems(*children)
        self._base_container.add_children(*updated)

    def remove_children(self, *children: Element) -> None:
        if len(children) == 1 and isinstance(children[0], list):
            # for backwards compatibility, this used to accept a single list of children
            children = children[0]

        for elem in children:
            if not isinstance(elem, Element):
                # sometimes an unregistered function can end up here and break things...
                continue

            self._remove_interaction(elem.name)
            if elem == self._base_container:
                raise RuntimeError("You can't remove the base container!")

            # this should never be None, but in case some numpty does something weird...
            if getattr(elem, "parent", None):
                elem.parent.remove_children(elem)

    def set_children(self, children: list[Element]) -> None:
        updated = self._maybe_add_interaction_from_elems(*children)
        self._base_container.set_children(updated)
        # self._maybe_add_interaction_from_elems(*children)
        # self._base_container.set_children(children)

        # self._base_container.add_children( self.cameras )
        # if len(self.cameras) > 0:
        #     self._base_container.add_children( [ doover_ui_hidden_value(name="last_cam_snapshot") ] )

    def set_status_icon(self, icon_type: str, critical: bool = False):
        if icon_type == self._base_container.status_icon:
            return
        elif critical is True:
            # self._has_critical_ui_state_pending = True
            self._has_critical_interaction_pending = True  # fixme: work out if we ever need this in element setting

        self._base_container.status_icon = icon_type

    def set_display_name(self, name: str, critical: bool = False):
        if name == self._base_container.display_name:
            return
        elif critical is True:
            self._has_critical_interaction_pending = True

        self._base_container.display_name = name

    set_display_str = set_display_name


ui_manager = UIManager
