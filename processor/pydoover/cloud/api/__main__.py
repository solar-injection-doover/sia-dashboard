import datetime
import json
import logging

from .client import Client, AccessToken
from .channel import Channel


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # c = Client(token="token", base_url="https://my.d.doover.dev")
    c = Client("josh@span-eng.com", "password", base_url="https://my.d.doover.dev")
    # c.login("josh@span-eng.com", "password")
    # x = c.get_channel("43904b8e-306e-48bc-84f6-63c892da4a10")
    #
    a = c.get_agent("9fb5d629-ce7f-4b08-b17a-c267cbcd0427")
    # print(x)
    # # d = channel.publish("Hi")
    # m = x.fetch_messages()
    # print(len(m))
    # print([mes.fetch_payload() for mes in m])
    # print("chan", d)
    # m = channel.fetch_messages()
    # print(m)
