import asyncio
import logging
from typing import List
from web_site import Web_site


class Sites_collection:
    """
    Хранилище всех сайтов, которые нужно проверять.
    """

    sites: List[Web_site]

    def __init__(self, sem: asyncio.Semaphore, config=None, log: logging.Logger=None):
        self.sites = []

        for site in config:
            self.sites.append(Web_site(sem, site, log))



