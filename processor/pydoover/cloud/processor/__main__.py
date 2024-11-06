import logging

from .base import ProcessorBase


class HelloWorld(ProcessorBase):
    def setup(self):
        ...

    def process(self):

        logging.info("Hello World Started...")

        logging.debug("Triggerred by: %s", self.task_id)

        hello_world_channel = self.fetch_channel_named("josh-test")
        hello_world_channel.publish('Hello World1')

        logging.info("Hello World Finished")

    def close(self):
        ...


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    inst = HelloWorld(
        agent_id="9fb5d629-ce7f-4b08-b17a-c267cbcd0427",
        access_token="e9c92fe2996390ca7ebded4af918cde701d87ac7",
        api_endpoint="https://my.d.doover.dev",
        package_config={},
        msg_obj={},
        task_id="d1c7e8e3-f47b-4c68-86d7-65054d9e97d3",
        log_channel="1f71b8bd-9444-4f34-859f-f339875a765c",
        agent_settings={
            "deployment_config": {}
        }
    )
    inst.execute()
