# -*- coding: utf-8 -*-
# @author: zelenka.guru/zcxw

from configparser import ConfigParser


from app import pinfo, perror, fix_path,to_format_code
import os


EXAMPLE_CONFIG = ConfigParser(default_section='ОСНОВНЫЕ')
EXAMPLE_CONFIG["ОСНОВНЫЕ"] = {
    'ТИП_РАБОТЫ': 5,
    'ПАПКА_ДАННЫХ': './data$bsp',
    'сохранять_путь_с_сидкой_при_парсе': True,
    
}

EXAMPLE_CONFIG["ЧЕК_ТЕЛЕГРАММ"] = {
    'КОПИРОВАТЬ_ВАЛИД': True,
    'СОХРАНЯТЬ_ДАННЫЕ_ТЕЛЕГРАММ': True,
    'ФОРМАТ_ДАННЫХ_ТЕЛЕГРАММ': r'@{username}: {path}',
    'ЗАМЕНЯТЬ_КОГДА_НЕТ_НИКА': r'{phone}',
    'МАКС_ВРЕМЯ_РАБОТЫ_ПОТОКА': 20,
    'МАКС_ПОТОКОВ': 50,
    'проверять_сидки_по_словарю': False,
}
EXAMPLE_CONFIG["ПАРСИНГ_ТЕЛЕГРАММ"] = {
    'МАКС_ВРЕМЯ_РАБОТЫ_ПОТОКА': 20,
    'МАКС_ПОТОКОВ': 50,
    "ПАРСИТЬ_СИДКИ": True,
    'ДЕТАЛЬНЫЙ_ПАРСИНГ': False,
    "ПАРСИТЬ_ВИФ_КЛЮЧИ": False,
    "ПАРСИТЬ_ХЕКС_КЛЮЧИ": False,
    'проверять_сидки_по_словарю': False,

}
EXAMPLE_CONFIG["ПАРСИНГ_ФАЙЛОВ"] = {
    'МАКС_ВРЕМЯ_РАБОТЫ_ПОТОКА': 20,
    'МАКС_ПОТОКОВ': 50,
    'ДЕТАЛЬНЫЙ_ПАРСИНГ': False,
    'ЧЕРНЫЙ_СПИСОК_ФАЙЛОВ': ['*.exe', '*.dll'],
    'БЕЛЫЙ_СПИСОК_ФАЙЛОВ': [],
    "ПАРСИТЬ_СИДКИ": True,
    "ПАРСИТЬ_ВИФ_КЛЮЧИ": False,
    "ПАРСИТЬ_ХЕКС_КЛЮЧИ": False,
    'проверять_сидки_по_словарю': False,
}


def get_config_path():
    try:
        
        config_path = './config.ini'
        if not os.path.exists(config_path):
            try:
                pinfo('config.ini не найден, создание...')
                EXAMPLE_CONFIG.write(
                    open(fix_path('./config.ini'), 'w', encoding='utf-8', errors='ignore'))
                config_path = fix_path('./config.ini')
            except Exception as e:
                perror(f'При создании конфига произошла ошибка: {e}')
                return False
        return config_path
    except:
        perror(f'При получении путя до конфига произошла ошибка: {e}')
        return False


def read_config(path):
    try:
        pinfo('Чтение конфига')
        config = ConfigParser(default_section='ОСНОВНЫЕ')
        config.read_file(open(path, 'r', encoding='utf-8', errors='ignore'))
        return config
    except Exception as e:
        perror(f'При чтении конфига произошла ошибка: {e}')
        return False



def check_config(config: ConfigParser):
    try:
        pinfo('Проверка значений у параметров конфига')
        valid = True
        for section in EXAMPLE_CONFIG.keys():
            for option, value in EXAMPLE_CONFIG[section].items():
                try:
                    user_value = config.get(section, option)
                    to_format = to_format_code(user_value)
                    if (str(to_format) != user_value):
                        perror(f'У значения параметра [white]`{section}/{option}`[/white] неверный тип: {type(to_format).__name__} != {type(user_value).__name__}')
                        valid = False
                except Exception as e:
                    valid = False
                    perror(f'При проверки значения у параметра [white]`{section}/{option}`[/white] произошла ошибка: {e}')
            
        return valid
    except Exception as e:
        perror(f'При проверки значений у параметров конфига произошла ошибка: {e}')
        return False

def config_to_dict(config):
    try:
        pinfo('Приведение конфига в формат программы')
        result = {}
        valid = True
        for section in EXAMPLE_CONFIG.keys():
            result[section] = {}
            for option, value in EXAMPLE_CONFIG[section].items():
                user_value = str(config.get(section, option)).strip()
                to_format = to_format_code(user_value)
                result[section][option] = to_format
        if not valid:
            result = False
        return result
    except Exception as e:
        perror(f'При приведении конфига в формат программы произошла ошибка: {e}')
        return False
        


def get_config():
    try:
        pinfo('Получение конфига')
        path = get_config_path()
        if not path:
            return False
        config = read_config(path)
        if not config:
            return False
        check = check_config(config)
        if not check:
            return False
        config_dict = config_to_dict(config)
        if not config_dict:
            return False
        pinfo('Конфиг получен без ошибок')
        return config_dict
    except Exception as e:
        perror(f'При получении конфига произошла ошибка: {e}')
        return False
    
    
