import asyncio
import logging
import sys

import aiohttp


class Web_site:
    """
    Этот класс представляет один сайт. В одном сайте может находится несколько конечных точек, которые нужно проверить

    """

    def __init__(self, sem, config=None, log: logging.Logger = None):

        self.domain = config['domain']
        if 'http' in config:
            self.http = config['http']
        else:
            self.http = False

        if 'urls' not in config:
            self.endpoints = [{'uri': '/'}]
        else:
            self.endpoints = [end for end in config['urls']]

        self.sem = sem
        self.log = log
        self.isLogging = log is not None

    async def available(self):
        """
        Метод определяет доступность всех конечных точек и возвращает массив результатов их опроса
        :return:
        """

        # with await self.sem:
        errors = []

        for uri_info in self.endpoints:
            uri = uri_info['uri']
            if uri[0] != '/':
                uri = '/%s' % uri
            proto = 'https'
            if self.http:
                proto = 'http'

            url = '%s://%s%s' % (proto, self.domain, uri)

            # if self.isLogging:
            #     self.log.info({
            #         'domain': self.domain,
            #         'uri': uri,
            #         'http': self.http,
            #         'status': '200',
            #     })

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(url, verify_ssl=False, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
                }, timeout=10) as response:
                        html = await response.text()

                        if response.status != 200:
                            errors.append({
                                'domain': self.domain,
                                'uri': uri,
                                'http': self.http,
                                'status': response.status,
                                'header': response.headers,
                                'message': 'Bad site status: %s' % response.status
                            })
                            continue
                        else:
                            if 'check_text' in uri_info:
                                if uri_info['check_text'] not in html:
                                    errors.append({
                                        'domain': self.domain,
                                        'uri': uri,
                                        'http': self.http,
                                        'status': response.status,
                                        'header': response.headers,
                                        'message': 'Cant find text: "%s"' % uri_info['check_text']
                                    })
                                    continue

            except aiohttp.client_exceptions.InvalidURL as e:
                errors.append({
                    'domain': self.domain,
                    'uri': uri,
                    'http': self.http,
                    'message': 'Invalid URL' % url
                })

            except aiohttp.client_exceptions.ClientConnectorError as e:
                errors.append({
                    'domain': self.domain,
                    'uri': uri,
                    'http': self.http,
                    'message': 'Client connector error'
                })
            except Exception as e:
                exception_code = str(sys.exc_info()[0])
                errors.append({
                    'domain': self.domain,
                    'uri': uri,
                    'http': self.http,
                    'message': 'Other error [%s] - %s' % (exception_code, repr(e))
                })
        print(self.domain, 'check')
        if len(errors) > 0:
            print(errors)
            for e in errors:
                self.log.error(e)

    async def check_endpoint(self):

        while True:
            await self.available()
            await asyncio.sleep(10)
