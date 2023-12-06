# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw

from opentele.api import UseCurrentSession
from opentele.td import TDesktop
from app import *
from secrets import token_hex
import logging


async def telethonsFromTdata(path: str):
    try:
        tdesk = TDesktop(path)
        account = tdesk.mainAccount
        name = fix_path(path, f"/id{account.UserId}#{token_hex(2)}$bsp.session")
        remove_file(name)
        client = await account.ToTelethon(name, UseCurrentSession, timeout=3)
        return [client]
    except Exception as e:
        logging.error(str(e))
        return False
