# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw

from opentele.tl import TelegramClient
from opentele.td import API
import random, logging

api_settings = [
    {
        'api_id': 20137158,
        'api_hash': '473aeb73e73b2da67a2b252bfb7e5277'
    },
    {
        "api_id": 2227391,
        "api_hash": "81f7429140163b499a496abdcc49db2e",

    }
]


async def telethonFromSession(path: str):
    try:
        api = random.choice(api_settings)
        return TelegramClient(path, API.TelegramDesktop(

            api_id=api['api_id'],
            api_hash=api['api_hash'],
            device_model="Desktop",
            system_version="Windows 10",
            app_version="3.4.3 x64",
            lang_code="en",
            system_lang_code="en-US",
            lang_pack="tdesktop"
        ), timeout=3)
    except Exception as e:
        logging.error(str(e))
        return False
