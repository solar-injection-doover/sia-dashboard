from .channel import Channel


class Agent:

    def __init__(self, client, data):
        self.client = client

        self.id = None
        self.type = None
        self.name = None
        self.owner_org = None
        self.deployment_config = None
        self.channels = None

        self._from_data(data)

    def _from_data(self, data):
        # {'agent': '9fb5d629-ce7f-4b08-b17a-c267cbcd0427', 'current_time': 1715662485.485132, 'type': 'doover_users | user', 'channels': [{'channel': 'd1c7e8e3-f47b-4c68-86d7-65054d9e97d3', 'name': 'josh-test', 'type': 'base', 'agent': '9fb5d629-ce7f-4b08-b17a-c267cbcd0427'}, {'channel': '1f71b8bd-9444-4f34-859f-f339875a765c', 'name': 'test-logs', 'type': 'base', 'agent': '9fb5d629-ce7f-4b08-b17a-c267cbcd0427'}, {'channel': '86c96181-425d-46f4-a4eb-b36bde2b3984', 'name': 'notifications', 'type': 'base', 'agent': '9fb5d629-ce7f-4b08-b17a-c267cbcd0427'}]}
        self.id = data["agent"]
        self.type = data["type"]

        if 'name' in data: self.name = data["name"] 
        else: self.name = None

        if 'owner_org' in data: self.owner_org = data["owner_org"]
        else: self.owner_org = None

        if 'settings' in data and 'deployment_config' in data['settings']: self.deployment_config = data["settings"]["deployment_config"]
        else: self.deployment_config = None

        self.channels = [Channel(data=c, client=self.client) for c in data["channels"]]

    @property
    def agent_id(self):
        return self.id

    def update(self):
        res = self.client._get_agent_raw(self.id)
        return self._from_data(res)
