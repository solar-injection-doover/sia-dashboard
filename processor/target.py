import logging, json, time

from pydoover.cloud import ProcessorBase
from pydoover.utils import find_object_with_key

class target(ProcessorBase):


    def setup(self):
        ## Do the setup here

        # Get the required channels
        self.ui_state_channel = self.api.create_channel("ui_state", self.agent_id)
        # self.ui_cmds_channel = self.api.create_channel("ui_cmds", self.agent_id)

    def process(self):

        message_type = self.package_config.get("message_type")

        if message_type == "DEPLOY":
            self.on_deploy()

    def on_deploy(self):

        ## Get the latest ui_state
        ui_state = self.ui_state_channel.fetch_aggregate()

        ## From the ui_state, if there is a "RemoteComponent" object, extract it
        remote_component = None
        if ui_state:
            remote_component = find_object_with_key(ui_state, "RemoteComponent")

        if remote_component is None:
            logging.error("RemoteComponent not found in ui_state")
            return
        
        if "containers" in remote_component:
            containers = remote_component["containers"]
            remote_component["children"] = containers
            remote_component.pop("containers")

        ## republish the updated ui_state
        state_update = {
            "state": {
                "children": {
                    "RemoteComponent": None,
                    "GwStoragesDashboard": remote_component
                }
            }
        }

        self.ui_state_channel.publish(state_update)
