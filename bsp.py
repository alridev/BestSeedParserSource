# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw
import asyncio
import logging
import sys

from rich import print

from app import clear_console, pinfo, perror, get_config, get_date, save_result_checker, save_result_parser
import getpass
from app.classes import TdataChecker, SessionsChecker, TdataParsing, SessionsParsing, FilesParser

sys.setrecursionlimit(100_000)

for name in logging.Logger.manager.loggerDict.keys():
    logging.getLogger(name).setLevel(logging.CRITICAL)

TEXT_TYPES_WORK = {
    1: "Выбран тип работы: чек тадат",
    2: "Выбран тип работы: чек .session",
    3: "Выбран тип работы: парсинг тадат",
    4: "Выбран тип работы: парсинг .session",
    5: "Выбран тип работы: парсинг файлов",
}

banner = "\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0024\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0024\u0024\u0020\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0020\u0020\u0020\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0020\u0020\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u0020\u0020\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u0020\u0020\u0020\u0024\u0024\u0020\u0020\u0020\u0020\u0020\u0020\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0024\u0024\u0024\u0024\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u000d\u000a\u005b\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0024\u0024\u005b\u002f\u0023\u0046\u0046\u0044\u0037\u0030\u0030\u005d\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u0020\u000d\u000a\u0020\u005b\u0062\u006c\u0061\u0063\u006b\u005d\u0074\u0068\u0065\u0020\u0070\u0072\u006f\u0067\u0072\u0061\u006d\u0020\u0077\u0061\u0073\u0020\u0063\u0072\u0065\u0061\u0074\u0065\u0064\u0020\u0062\u0079\u0020\u0040\u007a\u0063\u0078\u0077\u005f\u006c\u006f\u006c\u007a\u000d\u000a"
clear_console()
print(f"[red]{banner}")


def close_program():
    pinfo("Завершение работы")
    getpass.getpass("Нажмите Enter...")
    sys.exit(0)


async def main():
    try:
        pinfo("Запуск главной функции")
        config = get_config()
        if not config:
            close_program()
        TYPE_WORK = config["ОСНОВНЫЕ"]["тип_работы"]
        pinfo(TEXT_TYPES_WORK[TYPE_WORK])
        pinfo("Подтвердите запуск работы нажатием Enter... ", end="")
        getpass.getpass("")
        date_start = get_date()
        date_start_to_format = date_start.strftime("%d.%m.%Y %H:%M:%S")
        pinfo(f"Дата запуска работы: [#ffffff]{date_start_to_format}[/#ffffff]")

        if TYPE_WORK == 1:  # check tdatas
            try:
                checker = TdataChecker(config)
                result = await checker()

                if result:
                    await save_result_checker(config, checker, "tdatas")

            except Exception as e:
                pinfo(f"При запуске работы, произошла ошибка: {e}")
            finally:
                date_end = get_date()
                date_end_to_format = date_end.strftime("%d.%m.%Y %H:%M:%S")
                pinfo(f"Дата завершения работы: [#ffffff]{date_end_to_format}[/#ffffff]")

        elif TYPE_WORK == 2:  # "Checker .sessions",
            try:
                checker = SessionsChecker(config)
                result = await checker()

                if result:
                    await save_result_checker(config, checker, "sessions")

            except Exception as e:
                pinfo(f"При запуске работы, произошла ошибка: {e}")
            finally:
                date_end = get_date()
                date_end_to_format = date_end.strftime("%d.%m.%Y %H:%M:%S")
                pinfo(f"Дата завершения работы: [#ffffff]{date_end_to_format}[/#ffffff]")
        elif TYPE_WORK == 3:  # "Parser tdata's",
            try:
                parser = TdataParsing(config)
                result = await parser()

                if result:
                    await save_result_parser(config, parser)

            except Exception as e:
                pinfo(f"При запуске работы, произошла ошибка: {e}")
            finally:
                date_end = get_date()
                date_end_to_format = date_end.strftime("%d.%m.%Y %H:%M:%S")
                pinfo(f"Дата завершения работы: [#ffffff]{date_end_to_format}[/#ffffff]")
        elif TYPE_WORK == 4:  # "Parser .sessions",
            try:
                parser = SessionsParsing(config)
                result = await parser()

                if result:
                    await save_result_parser(config, parser)

            except Exception as e:
                pinfo(f"При запуске работы, произошла ошибка: {e}")
            finally:
                date_end = get_date()
                date_end_to_format = date_end.strftime("%d.%m.%Y %H:%M:%S")
                pinfo(f"Дата завершения работы: [#ffffff]{date_end_to_format}[/#ffffff]")
        elif TYPE_WORK == 5:  # "Parser files",
            try:
                parser = FilesParser(config)
                result = await parser()

                if result:
                    await save_result_parser(config, parser)

            except Exception as e:
                pinfo(f"При запуске работы, произошла ошибка: {e}")
            finally:
                date_end = get_date()
                date_end_to_format = date_end.strftime("%d.%m.%Y %H:%M:%S")
                pinfo(f"Дата завершения работы: [#ffffff]{date_end_to_format}[/#ffffff]")
        date_result = date_end - date_start
        pinfo(f"Работа выполненна за [#ffffff]{date_result}[/#ffffff]")
    except Exception as e:
        perror(f"При работе главной фунции, произошла ошибка: {e}")


if __name__ == "__main__":
    __version__ = "1.0"
    pinfo(f"Версия: {__version__} Custom")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[red]ctrl+c detect...")
    except Exception as e:
        perror(str(e))
    except SystemExit:
        pass
    except:
        print("error", sys.exc_info()[1])
