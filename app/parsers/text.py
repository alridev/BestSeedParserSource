# -*- coding: utf-8 -*-

import re
from mnemonic import Mnemonic
from app import *
from bs4 import BeautifulSoup
from string import punctuation

def html_to_text(data):
    try:
        data = data.strip()
        new_data = BeautifulSoup(data, "lxml")

        new_data = BeautifulSoup(new_data.prettify(), "lxml").get_text()

        if new_data:
            return new_data
        else:
            return data
    except:
        return data


def is_mnemonic(data):
    try:
        data = data.strip()
        language = Mnemonic.detect_language(data)

        mnemo = Mnemonic(language)
        if mnemo.check(data):
            return True
        else:
            return False
    except:
        return False


def is_mnemonic_word(data, from_seed=False):
    try:
        data = data.strip()
        if from_seed.strip():
            language = Mnemonic.detect_language(from_seed.strip())
        else:
            language = Mnemonic.detect_language(data)
        mnemo = Mnemonic(language)
        if data in mnemo.wordlist:
            return True
        else:
            return False
    except:
        return False

punctuation = '\\'.join(list(punctuation))
def is_mnemonic_no_words(data):
    try:
        data = data.strip()
        split = len(data.split(" "))
        if (split > 11) and (split < 25) and (len(list(re.finditer(f'[\d{punctuation}]', data, re.MULTILINE))) == 0):
            return True
    except:
        return False


def is_mnemonic_word_no_words(data, from_seed=False):
    return True


async def parsing_crypto_from_srting(main_data: str, config):
    # TODO: FIX PARSING 10 mart
    seeds_ret = []
    wifs_ret = []
    hexs_ret = []
    main_data = html_to_text(main_data)
    main_data = main_data.lower()
    if config["парсить_сидки"]:
        if config["проверять_сидки_по_словарю"]:
            is_mnemonic = is_mnemonic
            is_mnemonic_word = is_mnemonic_word
        else:
            is_mnemonic = is_mnemonic_no_words
            is_mnemonic_word = is_mnemonic_word_no_words

        temp_1 = []
        main_data_split = (main_data + "\n").split("\n")

        for data_old in main_data_split:
            data_old = data_old.strip().replace("\n", " ").replace(",", " ")
            if not data_old:
                continue
            data_new = []
            for splitter in [":", ";", "-", " - ", "\t"]:
                try:
                    s = data_old.strip().split(splitter)
                    if s and data_old:
                        data_new.extend(s)

                except:
                    pass

            for data in data_new:
                data = data.strip().replace("\n", " ").replace(",", " ")
                if len(data.split(" ")) > 11:
                    if data:
                        if is_mnemonic(data) and data not in seeds_ret:
                            seeds_ret.append(data)

                if config["детальный_парсинг"]:
                    if len(temp_1) > 11:
                        temp_1_join = " ".join(temp_1)
                        if is_mnemonic(temp_1_join) and temp_1_join not in seeds_ret:
                            seeds_ret.append(temp_1_join)
                            temp_1.clear()

                    if len((main_data + "\n").split("\n")) > 11:
                        temp_1_join = " ".join(temp_1)
                        line_normal = re.sub(r"[^\w\s]+|[\d]+", "", data).strip()
                        if is_mnemonic_word(line_normal, temp_1_join) and line_normal not in temp_1:
                            temp_1.append(line_normal)

                    if len(temp_1) > 24:
                        temp_1.clear()

    if config["парсить_виф_ключи"]:
        try:
            data = main_data.replace(" ", "").replace("\n", "")
            regex_wif = r"^5[HJK][1-9A-Za-z][^OIl]{48}$"
            wifs = re.findall(regex_wif, data)
            for wif in wifs:
                if wif not in wifs_ret:
                    wifs_ret.append(wif)
        except:
            pass
    if config["парсить_хекс_ключи"]:
        try:
            data = main_data.replace(" ", "").replace("\n", "")
            regex_hex = r"[a-f0-9]{64}"
            hexs = re.findall(regex_hex, data)
            for hex in hexs:
                if hex not in hexs_ret:
                    hexs_ret.append(hex)
        except:
            pass

    return seeds_ret, wifs_ret, hexs_ret
