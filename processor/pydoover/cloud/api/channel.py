import base64
import os
import shutil
import uuid
import mimetypes
import logging
import sys
import importlib
import pathlib
from datetime import datetime

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .client import Client


class Channel:

    def __init__(self, *, client, data):
        self.client: "Client" = client
        self._aggregate = None
        self._messages = None

        self._from_data(data)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def _from_data(self, data):
        self.id = data["channel"]
        self.name = data["name"]
        # from the get_agent endpoint this is `agent`, from the get_channel endpoint this is `owner`.
        self.agent_id = (data.get("owner") or data.get("agent"))
        self._agent = None

        try:
            self._aggregate = data["aggregate"]["payload"]
        except KeyError:
            self._aggregate = None

    @property
    def aggregate(self):
        return self._aggregate

    def update(self):
        res = self.client._get_channel_raw(self.id)
        self._from_data(res)

    def get_tunnel_url(self, address):
        if self.name != "tunnels":
            raise RuntimeError("Tunnels are only valid in the `tunnels` channel.")

        agg = self.fetch_aggregate()
        try:
            tunnels = agg["open"]
        except KeyError:
            return

        found = [t for t in tunnels if t["address"] == address]
        if found:
            return found[0]["url"]

    def fetch_agent(self):
        if self._agent is not None:
            return self._agent

        self._agent = self.client.get_agent(self.agent_id)
        return self._agent

    def fetch_aggregate(self):
        if self._aggregate is not None:
            return self._aggregate
    
        self.update()
        return self._aggregate

    def fetch_messages(self, num_messages: int = 10):
        if self._messages is not None:
            return self._messages

        self._messages = self.client.get_channel_messages(self.id, num_messages=num_messages)
        return self._messages

    def publish(self, data: Any, save_log: bool = True, log_aggregate: bool = False, override_aggregate: bool = False, timestamp: Optional[datetime] = None):
        return self.client.publish_to_channel(self.id, data, save_log, log_aggregate, override_aggregate, timestamp)

    @property
    def last_message(self):
        messages = self.fetch_messages(num_messages=1)
        if messages is None or len(messages) == 0:
            return None
        return messages[0]
    
    @property
    def last_update_age(self):
        last_message = self.last_message
        if last_message is None:
            return None
        return last_message.get_age()

    def update_from_file(self, file_path, mime_type=None):
        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(file_path)
            # mime_type = "application/octet-stream"

        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()

        msg = {
            "output_type": mime_type,
            "output": b64_data
        }
        self.publish(msg)


class Processor(Channel):

    def update_from_package(self, package_dir):
        fp = f"/tmp/{uuid.uuid4()}"
        shutil.make_archive(fp, 'zip', package_dir)

        with open(f"{fp}.zip", "rb") as f:
            zip_bytes = f.read()
            b64_package = base64.b64encode(zip_bytes).decode()

        self.publish(b64_package)
        os.remove(f"{fp}.zip")

    def invoke_locally(self, 
            package_dir,
            agent_id,
            access_token,
            api_endpoint="https://my.doover.dev",
            package_config={},
            msg_obj={},
            task_id=None,
            log_channel=None,
            agent_settings={},
            # *args, **kwargs
        ):
        
        logging.basicConfig(level=logging.DEBUG)
        sys.path.append(package_dir)

        ## import the loaded generator file
        spec = importlib.util.spec_from_file_location("target", "target.py")
        target_task = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_task)

        # from .target import generator
        target_task = getattr(target_task, 'target')

        #     'agent_id' : The Doover agent id invoking the task e.g. '9843b273-6580-4520-bdb0-0afb7bfec049'
        #     'access_token' : A temporary token that can be used to interact with the Doover API .e.g 'ABCDEFGHJKLMNOPQRSTUVWXYZ123456890',
        #     'api_endpoint' : The API endpoint to interact with e.g. "https://my.doover.com",
        #     'package_config' : A dictionary object with configuration for the task - as stored in the task channel in Doover,
        #     'msg_obj' : A dictionary object of the msg that has invoked this task,
        #     'task_id' : The identifier string of the task channel used to run this processor,
        #     'log_channel' : The identifier string of the channel to publish any logs to
        #     'agent_settings' : {
        #       'deployment_config' : {} # a dictionary of the deployment config for this agent
        task_obj = target_task(
            agent_id=agent_id,
            access_token=access_token,
            api_endpoint=api_endpoint,
            package_config=package_config,
            msg_obj=msg_obj,
            task_id=task_id,
            log_channel=log_channel,
            agent_settings=agent_settings,
            # *args, **kwargs,
        )

        task_obj.execute()


class Task(Channel):

    def _from_data(self, data):
        super()._from_data(data)
        self.processor_id: str = data.get("processor")
        self._processor = None

    def fetch_processor(self) -> Optional[Processor]:
        if self._processor is not None:
            return self._processor
        if self.processor_id is None:
            return

        self._processor = self.client.get_channel(self.processor_id)
        return self._processor

    def subscribe_to_channel(self, channel_id: str):
        return self.client.subscribe_to_channel(channel_id, self.id)

    def unsubscribe_from_channel(self, channel_id: str):
        return self.client.unsubscribe_from_channel(channel_id, self.id)

    def invoke_locally(self, package_dir, msg_obj, agent_settings):
        processor = self.fetch_processor()
        if processor is None:
            return
        
        agent_id = self.client.agent_id
        access_token = self.client.access_token.token
        api_endpoint = self.client.base_url
        package_config = self.fetch_aggregate()
        task_id = self.id

        log_channel = None

        processor.invoke_locally(
            package_dir,
            agent_id,
            access_token,
            api_endpoint,
            package_config,
            msg_obj,
            task_id,
            log_channel,
            agent_settings,
        )