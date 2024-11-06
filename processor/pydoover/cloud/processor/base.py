"""
This is the base definition for a tiny lambda function
Which is run in response to messages processed in Doover's 'Channels' system.
This base class is designed to be overridden by a user defined class

In the doover_config.json file we have defined some of these subscriptions
These are under 'processor_deployments' > 'tasks'
"""

import logging
import sys
import time

from typing import Any

from ...cloud.api import Client, Message

from ...ui import UIManager

# use the root logger since we want to pipe these logs to a channel.
log = logging.getLogger()


class LogHandler(logging.NullHandler):
    def __init__(self, *args, **kwargs):
        self.logs = []
        super().__init__(*args, **kwargs)

    def handle(self, record):
        if record.levelno < self.level:
            return

        fmt = self.format(record)
        self.logs.append(fmt)

    def emit(self, record):
        self.handle(record)

    def get_logs(self):
        return "\n".join(self.logs)


class ProcessorBase:
    def __init__(self, **kwargs):

        self.agent_id: str = kwargs["agent_id"]
        self.access_token: str = kwargs["access_token"]
        self.log_channel_id: str = kwargs["log_channel"]
        self.task_id: str = kwargs["task_id"]

        self.api: Client = Client(token=self.access_token, base_url=kwargs["api_endpoint"])
        self.ui_manager: UIManager = UIManager(self.agent_id, self.api)
        
        self._log_handler = LogHandler()
        log.addHandler(self._log_handler)
        log.setLevel(level=logging.INFO)

        self.agent_id: str = kwargs["agent_id"]
        self.log_channel_id: str = kwargs["log_channel"]
        self.task_id: str = kwargs["task_id"]

        self.deployment_config: dict[str, Any] = kwargs["agent_settings"].get("deployment_config", {})
        self.package_config: dict[str, Any] = kwargs.get("package_config", {})

        try:
            if kwargs["msg_obj"] is None:
                raise KeyError
            self.message = Message(client=self.api, data=kwargs["msg_obj"], channel_id=None)
        except KeyError:
            self.message = None

        ### kwarg
        #     'agent_id' : The Doover agent id invoking the task e.g. '9843b273-6580-4520-bdb0-0afb7bfec049'
        #     'access_token' : A temporary token that can be used to interact with the Doover API .e.g 'ABCDEFGHJKLMNOPQRSTUVWXYZ123456890',
        #     'api_endpoint' : The API endpoint to interact with e.g. "https://my.doover.com",
        #     'package_config' : A dictionary object with configuration for the task - as stored in the task channel in Doover,
        #     'msg_obj' : A dictionary object of the msg that has invoked this task,
        #     'task_id' : The identifier string of the task channel used to run this processor,
        #     'log_channel' : The identifier string of the channel to publish any logs to
        #     'agent_settings' : {
        #       'deployment_config' : {} # a dictionary of the deployment config for this agent
        #     }

    def setup(self):
        return NotImplemented

    def close(self):
        return NotImplemented

    def execute(self):
        """This function is invoked after the singleton instance is created."""
        start_time = time.time()
        log.info(f"Initialising processor task for task channel {self.task_id}")
        log.info(f"Started at {start_time}.")

        try:
            self.import_modules()
            self.setup()

            try:
                self.process()
            except Exception as e:
                log.error(f"ERROR attempting to process message: {e} ", exc_info=e)

        except Exception as e:
            log.error(f"ERROR attempting to initialise process: {e}", exc_info=e)

        try:
            self.close()
        except Exception as e:
            log.error(f"ERROR attempting to close process: {e} ", exc_info=e)

        end_time = time.time()
        log.info(f"Finished at {end_time}. Process took {end_time - start_time} seconds.")

        if self._log_handler.get_logs() and self.log_channel_id is not None:
            self.api.publish_to_channel(self.log_channel_id, self._log_handler.get_logs())

    def process(self):
        return NotImplemented
    
        ## Do some logic
    
        ## Optionally update the UI at the end
        # self.ui_manager.push()

    @staticmethod
    def import_modules():
        """Attempt to delete any loaded pydoover modules that persist across lambdas."""
        if 'pydoover' in sys.modules:
            del sys.modules['pydoover']
        try:
            del pydoover
        except:
            pass
        try:
            del pd
        except:
            pass

    def get_agent_config(self, filter_key: str = None):
        if filter_key:
            return self.deployment_config.get(filter_key)
        return self.deployment_config

    def fetch_channel(self, channel_id: str):
        return self.api.get_channel(channel_id)

    def fetch_channel_named(self, channel_name: str):
        return self.api.get_channel_named(channel_name, self.agent_id)
