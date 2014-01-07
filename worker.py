#!/usr/bin/env python

import os
from pprint import pprint
import pyclbr

import redis
redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
redisdb = redis.from_url(redis_url)

import logging
if __name__ == '__main__':
    LOG = logging.getLogger()
    logging.basicConfig(
        format='%(levelname)s/%(module)s:%(lineno)d: %(message)s',
        level=logging.INFO)
else:
    LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

import common
import quote_providers
import detail_providers


class StockWorker(object):
    """
        manages set of symbols to quote
        implememts execute() (timer handler)
        interface with Redis (read command and write quotes)
    """

    def __init__(self):
        self.symbols = set()

        klsname = os.getenv('QUOTE_PROVIDER', '').rpartition('.')[2]
        if klsname:
            LOG.info('ENV QUOTE_PROVIDER: \'%s\'', klsname)
        # create provider from env klsname, defaults to AAStockScraper
        self.__quote_provider = getattr(quote_providers, klsname, quote_providers.AAStockMScraper)()
        LOG.info('Using quote provider: \'%s\'', self.__quote_provider.__class__.__name__)

        klsname = os.getenv('DETAIL_PROVIDER', '').rpartition('.')[2]
        if klsname:
            LOG.info('ENV DETAIL_PROVIDER \'%s\'', klsname)
        # create provider from env klsname, defaults to AAStockScraper
        self.__detail_provider = getattr(detail_providers, klsname, detail_providers.AAStockScraper)()
        LOG.info('Using detail provider: \'%s\'', self.__detail_provider.__class__.__name__)

    def get_quote(self, symbol, append=True):
        if (append):
            self.append(symbol)
        return self.__get_quote(symbol)

    def __get_quote(self, symbol):
        # abstract layer to get dict for the quote
        # !! blocking call !!
        return self.__quote_provider.quote(symbol).__dict__

    # cound use better names for these two functions
    def append(self, symbol):
        self.symbols.add(symbol)

    def replace(self, *symbols):
        self.symbols = set(symbols)

    # to be run on an interval timer
    def execute(self):
        for symbol in self.symbols:
            redisdb.hmset(symbol, self.__get_quote(symbol))
        redisdb.delete('WORKER-SYMBOLS')
        redisdb.sadd('WORKER-SYMBOLS', *self.symbols)
        redisdb.hmset('WORKER-LASTEXEC',
            {
                'time': common.get_timestamp(),
                'QUOTE_PROVIDER': self.__quote_provider.__class__.__name__,
                'DETAIL_PROVIDER': self.__detail_provider.__class__.__name__,
            }
        )

LOG.info('QUOTE_PROVIDER: %s', pyclbr.readmodule('quote_providers').keys())
LOG.info('DETAIL_PROVIDER: %s', pyclbr.readmodule('detail_providers').keys())

worker = StockWorker()

if __name__ == '__main__':
    LOG.info('local get_quote()')
    symbols = ['02823', '03988']
    for symbol in symbols:
        pprint(worker.get_quote(symbol), indent=4)
    quit()

    LOG.info('worker.execute()')
    import time
    time.sleep(2)
    worker.execute()

    LOG.info('mimics client read')
    for symbol in symbols:
        pprint(redisdb.hgetall(symbol), indent=4)
    pprint(redisdb.smembers('WORKER-SYMBOLS'), indent=4)

