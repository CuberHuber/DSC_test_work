#!/usr/bin/env python3
import asyncio
import os
import sys
import time

import yaml
from yaml import FullLoader

from log_factory import LogFactory
from sites_collection import Sites_collection

if __name__ == '__main__':

    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = f'{BASE_PATH}/config.yaml'
    SITES_PATH = f'{BASE_PATH}/sites.yaml'

    if not os.path.exists(CONFIG_PATH):
        print('Не найдет файл конфигации config.yaml по пути: ', CONFIG_PATH)
        exit()

    config: dict = {}
    sites: dict = {}

    with open(CONFIG_PATH, 'rt', encoding='utf8') as conf_file:
        config = yaml.load(conf_file, Loader=FullLoader)
    with open(SITES_PATH, 'rt', encoding='utf8') as sites_file:
        sites = yaml.load(sites_file, Loader=FullLoader)

    if 'logger' not in config:
        config['logger'] = {}

    log = LogFactory(config['logger'])


    if 'max_parallel_checks' not in config:
        config['max_parallel_checks'] = 3

    sem = asyncio.Semaphore(config['max_parallel_checks'])


    sites_collection = Sites_collection(sem, sites['sites'], log)

    start = time.time()
    def main():

        while True:
            loop = asyncio.get_event_loop()

            gathers = [sit.available() for sit in sites_collection.sites]

            loop.run_until_complete(asyncio.gather(*gathers))

            # loop.close()
            print("Time checking... ", time.time() - start)
            time.sleep(5)

    def main_2():

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[sit.check_endpoint() for sit in sites_collection.sites]))
        loop.close()

    try:
        main_2()
    except KeyboardInterrupt as e:
        print(e)
        sys.exit()
