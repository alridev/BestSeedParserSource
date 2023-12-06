# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw

import ast
import datetime as dt
import logging
import os
import random
import shutil
import subprocess
import sys
import time
from secrets import token_hex

import aiofiles
import python_socks
import pytz
from fs.osfs import OSFS
from opentele.tl import TelegramClient
from requests import get
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn

from app.logger import perror, pinfo


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def run(cmd):
    try:
        s = subprocess.run(cmd, shell=True, capture_output=True, check=True, encoding="utf-8").stdout.strip()
        return s

    except:
        return None


def guid():
    if sys.platform == "darwin":
        return "BCEC5B4C-223D-11B2-A85C-D4D33CBE644F"
        # return run(
        # "ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'",
        #  )

    if sys.platform == "win32" or sys.platform == "cygwin" or sys.platform == "msys":
        return run("wmic csproduct get uuid").split("\n")[2].strip()

    if sys.platform.startswith("linux"):
        return run("cat /var/lib/dbus/machine-id").strip() or run("cat /etc/machine-id").strip()

    if sys.platform.startswith("openbsd") or sys.platform.startswith("freebsd"):
        return "ERR"  # run('cat /etc/hostid') or \
        # run('kenv -q smbios.system.uuid')


async def save_result_checker(config, checker, type: str):
    config["ОСНОВНЫЕ"]["тип_работы"]
    pinfo("Сохранение данных")
    if config["ЧЕК_ТЕЛЕГРАММ"]["копировать_валид"]:
        if type == "tdatas":
            save_path = fix_path("./tdatas.valid$bsp/")
            create_dir(save_path)

            for tdata in checker.valid_tdatas:
                try:
                    save = fix_path(save_path, f"/tdata#{token_hex(2)}$bsp/")
                    copy_dir(tdata[0], save)
                    pinfo(f"Копирование {tdata[0]}  [#ffffff]-->[/#ffffff] {save} прошло успешно")
                except Exception as e:
                    perror(f"Ошибка копирования {tdata[0]}: {e}")
        elif type == "sessions":
            save_path = fix_path("./sessions.valid$bsp/")
            create_dir(save_path)

            for session in checker.valid_sessions:
                try:
                    save = fix_path(save_path, f"/session#{token_hex(2)}$bsp.session")
                    copy_file(session[0], save)
                    pinfo(f"Копирование {session[0]}  [#ffffff]-->[/#ffffff] {save} прошло успешно")
                except Exception as e:
                    perror(f"Ошибка копирования {session[0]}: {e}")
    if config["ЧЕК_ТЕЛЕГРАММ"]["сохранять_данные_телеграмм"]:
        if type == "tdatas":
            for tdata in checker.valid_tdatas:
                try:
                    save = fix_path("./data.telegram$bsp.txt")
                    await write_file(save, tdata[1], True)
                except Exception as e:
                    perror(f"Ошибка сохранения данных телеграмм {tdata[0]}: {e}")
        elif type == "sessions":
            save_path = fix_path("./sessions.valid$bsp/")
            create_dir(save_path)
            for session in checker.valid_sessions:
                try:
                    save = fix_path("./data.telegram$bsp.txt")
                    await write_file(save, session[1], True)
                except Exception as e:
                    perror(f"Ошибка сохранения данных телеграмм {session[0]}: {e}")
    if type == "tdatas":
        valid = len(checker.valid_tdatas)
    elif type == "sessions":
        valid = len(checker.valid_sessions)
    else:
        valid = 0

    pinfo(f"Количество валида: [#ffffff]{valid}[/#ffffff]")


async def save_result_parser(config, parser):
    pinfo("Сохранение данных")

    is_save_seed_path = config["ОСНОВНЫЕ"]["сохранять_путь_с_сидкой_при_парсе"]
    seeds = parser.seeds
    wifs = list(set(parser.wifs))
    hexs = list(set(parser.hexs))
    if is_save_seed_path:
        seeds_new = list(map(lambda x: f"{x[0]} ------ {x[1]}", seeds))
        pinfo(f"Сохранение [#ffffff]{len(seeds)}[/#ffffff] сид-фраз c путями")
        await write_file("./seeds_and_path$bsp.txt", "\n".join(seeds_new), True)
    seeds = list(map(lambda x: x[0], seeds))
    if seeds:
        pinfo(f"Сохранение [#ffffff]{len(seeds)}[/#ffffff] сид-фраз")
        await write_file("./seeds$bsp.txt", "\n".join(seeds), True)
    if wifs:
        pinfo(f"Сохранение [#ffffff]{len(wifs)}[/#ffffff] виф-ключей")
        await write_file("./wifs$bsp.txt", "\n".join(wifs), True)
    if hexs:
        pinfo(f"Сохранение [#ffffff]{len(hexs)}[/#ffffff] хекс-ключей")
        await write_file("./hexs$bsp.txt", "\n".join(hexs), True)


def clear_console():
    "Clear console"
    if sys.platform == "win32" or sys.platform == "cygwin" or sys.platform == "msys":
        os.system("clws")
    else:
        os.system("clear")


def get_unix():
    "Get timestamp"
    return int(time.time())


def get_date():
    "Get datetime"
    tz = pytz.timezone("Europe/Moscow")
    return dt.datetime.now(tz=tz)


def copy_dir(src, dist):
    "Copy folder"
    try:
        shutil.copytree(src, dist, dirs_exist_ok=True)
        return True
    except Exception:
        return False


def copy_file(src, dist):
    "Copy file"
    try:
        shutil.copyfile(src, dist)
        return True
    except Exception:
        return False


def isClass(obj, class_target):
    "Check obj is class_target"
    try:
        class_target(obj)
        return True
    except Exception:
        return False


def line_crop(line: str, max_len: int = 18, crop_type: str = "end"):
    "Crop line (add ... and crop)"
    if len(line) > max_len:
        if crop_type == "end":
            return line[: max_len - 3] + "..."
        elif crop_type == "start":
            return "..." + line[max_len - 3 :]
        else:
            return line[: max_len - 3] + "..."
    else:
        return line


def remove_dir(path: str):
    "Remove dir"
    try:
        shutil.rmtree(path, True)
        return True
    except Exception as e:
        logging.error(str(e))
        return False


def remove_file(path: str):
    "Remove file"
    try:
        shutil.rmtree(path, True)
        return True
    except Exception:
        return False


def create_dir(path: str):
    "Create dir"
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except Exception:
        return False


def get_root_path():
    "Get cwd"
    try:
        return os.getcwd()
    except Exception:
        return "./"


async def read_file(path: str, bytes: bool = False):
    "Read file"
    if bytes:
        pass
    else:
        pass
    try:
        if bytes:
            fp = await aiofiles.open(path, "rb")
        else:
            fp = await aiofiles.open(path, "r", encoding="utf-8", errors="ignore")
        return await fp.read()
    except Exception:
        if bytes:
            return b""
        else:
            return ""


async def write_file(path: str, data, append: bool = False, bytes: bool = False):
    "Wirte file"
    try:
        if bytes:
            if append:
                fp = await aiofiles.open(path, "ab+")
            else:
                fp = await aiofiles.open(path, "wb")
        else:
            if append:
                fp = await aiofiles.open(path, "a+", encoding="utf-8", errors="ignore")
                data = "\n" + data
            else:
                fp = await aiofiles.open(path, "w+", encoding="utf-8", errors="ignore")

        await fp.write(data)
        return True
    except Exception:
        return False


def to_format_code(data: str):
    try:
        data = str(data)
        js = ast.literal_eval(data)
        return js
    except Exception:
        return data


def to_json(data: str):
    try:
        data = str(data)
        js = ast.literal_eval(data)
        if type(js) != dict:
            return {}
        return js
    except Exception:
        return {}


def to_list(data: str):
    try:
        data = str(data)
        js = ast.literal_eval(data)
        if type(js) != list:
            return []
        return js
    except Exception:
        return []


def fix_path(root: str, *paths):
    "Fix path"
    if paths:
        paths = map(fix_path, paths)
    if root.startswith("./"):
        path = os.path.normpath(root.replace("\\", "/"))
        path = os.path.normpath(get_root_path() + "//" + root)
        if paths:
            path = os.path.normpath(path + "/".join(paths))

    else:
        path = os.path.normpath(root.replace("\\", "/"))
        if paths:
            path = os.path.normpath(path + "/".join(paths))
    return path


def find_files(root: str, keywords: list = None, print_log: bool = False, black_list_files=[]):
    "Find files"
    try:
        osfs = OSFS(root)
        result = []
        if black_list_files == []:
            black_list_files = None
        if print_log:
            pinfo("Осуществляю поиск данных...")
        result = [
            file
            for file in osfs.walk.files(
                filter=keywords, exclude=black_list_files, ignore_errors=True, search="depth"
            )
        ]
        if result and print_log:
            pinfo(f"Поиск закончен: [#ffffff]{len(result)}[/#ffffff]")
        return result
    except KeyboardInterrupt:
        pinfo(f"Осуществляю поиск данных: [#ffffff]{len(result)}[/#ffffff]")
        return []
    except Exception as e:
        perror(f"При поиске данных произошла ошибка: {e}")
        return []


def proxy_format(proxies: list):
    "Proxy to standart format"
    result = []
    for proxy in proxies:
        try:
            proxy_dict = {}
            type = proxy.split("://")[0]
            data = proxy.split("://")[1]
            if type == "http":
                type = python_socks.ProxyType.HTTP
            elif type == "socks4":
                type = python_socks.ProxyType.SOCKS4
            elif type == "socks5":
                type = python_socks.ProxyType.SOCKS5
            else:
                continue
            isAuthProxy = "@" in proxy
            if isAuthProxy:
                auth = data.split("@")[0]
                con_data = data.split("@")[1]
                user, password = auth.split(":")
                addr, port = con_data.split(":")
                proxy_dict.update(type=type, user=user, password=password, addr=addr, port=int(port))
            else:
                con_data = data
                addr, port = con_data.split(":")
                proxy_dict.update(type=type, addr=addr, port=int(port))
            result.append(proxy_dict)
        except Exception:
            pass
    return result


def proxy_get(proxies: list):
    "Get proxy"
    if proxies:
        default_ip = get("https://ipinfo.io/ip").text
        proxy_dict: dict = random.choice(proxies)
        type = proxy_dict.get("type")
        if type == python_socks.ProxyType.HTTP:
            type = "http"
        elif type == python_socks.ProxyType.SOCKS4:
            type = "socks4"
        elif type == python_socks.ProxyType.SOCKS5:
            type = "socks5"
        else:
            return None
        try:
            addr, port = proxy_dict.get("addr"), proxy_dict.get("port")
            auth = proxy_dict.get("username")
            if auth:
                username, password = proxy_dict.get("username"), proxy_dict.get("password")
                auth = f"{username}{password}@"
            proxy = {"http": f"{type}://{auth}{addr}:{port}", "https": f"{type}://{auth}{addr}:{port}"}
            new_ip = get("https://ipinfo.io/ip", proxies=proxy, timeout=10).text
            if new_ip != default_ip:
                return proxy_dict
        except Exception:
            return None


async def checkValidTelegramClient(client: TelegramClient, close: bool = True):
    try:
        me = await client.get_me()
        assert me and me.phone
        return me
    except Exception:
        return False


def progress_create(all: int, text: str):
    progress = Progress(
        TextColumn("[progress.description]{task.description}"), BarColumn(), MofNCompleteColumn("/")
    )
    task = progress.add_task(text, total=all)
    return progress, task


def update_progress(task, progress: Progress, add=1):
    progress.update(task, advance=add)
