import logging

from collections import namedtuple
from datetime import datetime, timedelta
from typing import Any, Union, Callable, overload, Literal, Optional, TypeVar
from urllib.parse import quote, urlencode

import requests

from .message import Message
from .agent import Agent
from .channel import Channel, Processor, Task
from .exceptions import NotFound, Forbidden, HTTPException


log = logging.getLogger(__name__)
AccessToken = namedtuple("AccessToken", ["token", "expires_at"], defaults=(None, ))
T = TypeVar("T", bound=Channel)


class Route:
    def __init__(self, method, route, *args, **kwargs):
        self.method = method

        self.url = route
        if args:
            self.url = route.format(*[quote(a) for a in args])

        if kwargs:
            self.url = f"{self.url}?{urlencode(kwargs)}"


class Client:

    def __init__(
        self,
        username: str = None,
        password: str = None,
        token: str = None,
        token_expires: datetime = None,
        base_url: str = "https://my.doover.dev",
        agent_id: str = None,
        verify: bool = True,
        login_callback: Callable = None,
    ):
        self.access_token = AccessToken(token, token_expires)
        self.agent_id = agent_id
        self.login_callback = login_callback

        self.username = username
        self.password = password

        self.verify = verify
        self.base_url = base_url
        self.session = requests.Session()

        self.request_retries = 1
        self.request_timeout = 25

        if not ((username and password) or token):
            raise RuntimeError("Must have username and password or access token set.")
        elif token:
            self.update_headers()

    def update_headers(self):
        self.session.headers.update({"Authorization": f"Token {self.access_token.token}"})
        self.session.verify = self.verify

    def request(self, route: Route, **kwargs):
        # default is access token to not expire
        if self.access_token.expires_at and self.access_token.expires_at < datetime.utcnow():
            logging.info("Token expired, attempting to refresh token.")
            self.login()

        url = self.base_url + route.url

        attempt_counter = 0
        retries = self.request_retries if route.method == "GET" else 0

        while attempt_counter <= retries:
            attempt_counter += 1

            log.debug(f"Making {route.method} request to {url} with kwargs {kwargs}")
            resp = self.session.request(route.method, url, timeout=self.request_timeout, **kwargs)

            if resp.status_code == 200:
                ## if we get a 200, we're good to go
                break
            elif resp.status_code == 403:
                raise Forbidden("Access denied.")
            elif resp.status_code == 404:
                raise NotFound("Resource not found.")
            elif resp.status_code != 200:
                log.info(f"Failed to make request to {url}. Status code: {resp.status_code}, message: {resp.text}")
                if attempt_counter > retries:
                    raise HTTPException(resp.text)

        try:
            data = resp.json()
        except ValueError:
            data = resp.text

        log.debug(f"{url} has received {data}")
        return data

    def _get_agent_raw(self, agent_id: str) -> dict[str, Any]:
        return self.request(Route("GET", "/ch/v1/agent/{}", agent_id))

    def _get_agent_list_raw(self) -> list[dict[str, Any]]:
        return self.request(Route("GET", "/ch/v1/list_agents/"))

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        data = self._get_agent_raw(agent_id)
        return data and Agent(client=self, data=data)

    def get_agent_list(self) -> list[Agent]:
        data = self._get_agent_list_raw()
        if not "agents" in data:
            return []
        return [Agent(client=self, data=d) for d in data["agents"]]

    def _parse_channel(self, data) -> T:
        if data["name"].startswith("!"):
            return Task(client=self, data=data)
        elif data["name"].startswith("#"):
            return Processor(client=self, data=data)
        else:
            return Channel(client=self, data=data)

    def _get_channel_raw(self, channel_id: str) -> dict[str, Any]:
        return self.request(Route("GET", "/ch/v1/channel/{}", channel_id))

    def get_channel(self, channel_id: str) -> Optional[T]:
        data = self._get_channel_raw(channel_id)
        return data and self._parse_channel(data)

    def _get_channel_named_raw(self, channel_name: str, agent_id: str) -> dict[str, Any]:
        return self.request(Route("GET", "/ch/v1/agent/{}/{}", agent_id, channel_name))

    def get_channel_named(self, channel_name: str, agent_id: str) -> Optional[T]:
        data = self._get_channel_named_raw(channel_name, agent_id)
        return data and self._parse_channel(data)

    def get_channel_messages(self, channel_id: str, num_messages: Optional[int] = None) -> list[Message]:
        if num_messages:
            data = self.request(Route("GET", "/ch/v1/channel/{}/messages/{}", channel_id, str(num_messages)))
        else:
            data = self.request(Route("GET", "/ch/v1/channel/{}/messages", channel_id))

        if not data:
            return []

        return [Message(client=self, data=m, channel_id=channel_id) for m in data["messages"]]

    def _get_message_raw(self, channel_id: str, message_id: str) -> dict[str, Any]:
        return self.request(Route("GET", "/ch/v1/channel/{}/message/{}", channel_id, message_id))

    def get_message(self, channel_id: str, message_id: str) -> Optional[Message]:
        data = self._get_message_raw(channel_id, message_id)
        return data and Message(client=self, data=data, channel_id=channel_id)

    def create_channel(self, channel_name: str, agent_id: str) -> T:
        try:
            return self.get_channel_named(channel_name, agent_id)
        except NotFound:
            pass
        # all we need to do is publish to a channel with an empty payload
        self.request(Route("POST", "/ch/v1/agent/{}/{}/", agent_id, channel_name))
        # this is a bit of a wasted API call, but since this is the same method to post an aggregate to a
        # channel it can either return a new channel ID (if created), or the message ID of the posted message.
        return self.get_channel_named(channel_name, agent_id)

    def create_processor(self, processor_name: str, agent_id: str) -> Processor:
        return self.create_channel("#" + processor_name.lstrip('#'), agent_id)

    def create_task(self, task_name: str, agent_id: str, processor_id: str) -> Task:
        task = "!" + task_name.lstrip('!')
        payload = {
            "msg": {},  # this is a required field apparently
            "processor_id": processor_id
        }
        self.request(Route("POST", "/ch/v1/agent/{}/{}/", agent_id, task), json=payload)
        return self.get_channel_named(task, agent_id)

    def _maybe_subscribe_to_channel(self, channel_id: str, task_id: str, subscribe: bool):
        data = {"channel_id": channel_id, "subscribe": subscribe}
        return self.request(Route("POST", "/ch/v1/channel/{}/subscribe/", task_id), json=data)

    def subscribe_to_channel(self, channel_id: str, task_id: str) -> bool:
        return self._maybe_subscribe_to_channel(channel_id, task_id, True)

    def unsubscribe_from_channel(self, channel_id: str, task_id: str) -> bool:
        return self._maybe_subscribe_to_channel(channel_id, task_id, False)

    def publish_to_channel(self, channel_id: str, data: Any, save_log: bool = True, log_aggregate: bool = False, override_aggregate: bool = False, timestamp: Optional[datetime] = None):
        # basically we're assuming there's only 2 types of data - dict or string...
        post_data = {"msg": data}
        if save_log:
            post_data["record_log"] = save_log
        if log_aggregate:
            post_data["log_aggregate"] = True
        if override_aggregate:
            post_data["override_aggregate"] = True
        if timestamp:
            post_data["timestamp"] = int(timestamp.timestamp())

        if isinstance(post_data, dict):
            return self.request(Route("POST", "/ch/v1/channel/{}/", channel_id), json=post_data)
        else:
            return self.request(Route("POST", "/ch/v1/channel/{}/", channel_id), data=str(post_data))

    def publish_to_channel_name(self, agent_id: str, channel_name: str, data: Any, save_log: bool = True, log_aggregate: bool = False, override_aggregate: bool = False, timestamp: Optional[datetime] = None):
        post_data = {"msg": data}
        if save_log:
            post_data["record_log"] = save_log
        if log_aggregate:
            post_data["log_aggregate"] = True
        if override_aggregate:
            post_data["override_aggregate"] = True
        if timestamp:
            post_data["timestamp"] = int(timestamp.timestamp())
        
        if isinstance(post_data, dict):
            return self.request(Route("POST", "/ch/v1/agent/{}/{}/", agent_id, channel_name), json=post_data)
        else:
            return self.request(Route("POST", "/ch/v1/agent/{}/{}/", agent_id, channel_name), data=str(post_data))

    def create_tunnel_endpoints(self, agent_id: str, endpoint_type: str, amount: int):
        to_return = []
        for i in range(amount):
            res = self.request(Route("POST", "/ch/v1/agent/{}/ngrok_tunnels/{}", agent_id, endpoint_type))
            if res and res.get("url"):
                to_return.append(res["url"])
        return to_return

    def get_tunnel_endpoints(self, agent_id: str, endpoint_type: str):
        return self.request(Route("GET", "/ch/v1/agent/{}/ngrok_tunnels/{}", agent_id, endpoint_type))

    def login(self):
        if not (self.username or self.password):
            raise RuntimeError("Must have username and password set since access token has expired.")

        logging.info("Logging in...")
        session = requests.Session()

        login_url = f"{self.base_url}/accounts/login/"

        session.get(login_url)
        login_data = dict(
            login=self.username,
            password=self.password,
            csrfmiddlewaretoken=session.cookies.get('csrftoken'),
            next='/'
        )
        res = session.post(login_url, data=login_data, headers=dict(Referer=login_url))

        # bit of a hack... don't know a better way? Two-Factor is the title on the page...
        if "Two-Factor" in res.text:
            print("Your account has 2FA enabled. It is recommended to instead use `doover configure_token` "
                  "and use a long-lived token, otherwise you will have to 2FA authenticate every 20min.\n"
                  "Quit and run that command, or supply your 2FA code to authenticate now.\n")

            token = input("Please enter your 2FA token: ")
            twofa_data = dict(
                csrfmiddlewaretoken=session.cookies.get('csrftoken'),
                code=token,
            )
            twofa_url = f"{self.base_url}/accounts/2fa/authenticate/"
            res = session.post(twofa_url, data=twofa_data, headers=dict(Referer=twofa_url))
            if res.status_code != 200:
                raise RuntimeError("Failed to authenticate 2FA.")

        res = session.get(f"{self.base_url}/ch/v1/get_temp_token/")

        try:
            data = res.json()
        except requests.exceptions.JSONDecodeError:
            raise RuntimeError("Failed to get temporary token. Login failed.")

        # FIXME: can these expire in UTC?
        difference = timedelta(seconds=float(data["valid_until"]) - float(data["current_time"]))
        expires_at = datetime.utcnow() + difference
        
        self.access_token = AccessToken(token=data["token"], expires_at=expires_at)
        self.agent_id = data["agent_id"]
        self.update_headers()

        logging.info(f"Successfully logged in and set token to expire in {int(difference.total_seconds()/60)}min...")
        try:
            self.login_callback()
        except Exception as e:
            print(f"failed to call callback: {e}")
            pass
