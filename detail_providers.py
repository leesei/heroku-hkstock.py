#!/usr/bin/env python

import html2text
import common

import logging
if __name__ == '__main__':
    LOG = logging.getLogger()
    logging.basicConfig(
        format='%(levelname)s/%(module)s:%(lineno)d: %(message)s',
        level=logging.INFO)
else:
    LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

# Scrapers fetch and parse webpage
# Json readers fetch data from JSON APIs
# all get_details() functions returns common.StockDetails


class AAStockScraper(object):
    _url = 'http://www.aastocks.com/en/stock/detailquote.aspx?symbol=%s'

    @staticmethod
    def get_details(symbol, flags=None):
        details = common.StockDetails(symbol)
        return details


class AAStockMScraper(object):
    _url = 'http://www.aastocks.com/en/mobile/Quote.aspx?symbol%s'
    # http://www.aastocks.com/tc/Ajax/AjaxData.ashx?type=stockname&language=chi&symbol=%s

    @staticmethod
    def get_details(symbol, flags=None):
        details = common.StockDetails(symbol)
        return details


class JsonReader(object):
    # 52 high/low
    _money18_url = 'http://money18.on.cc/js/daily/quote/%s_d.js'
    # lot size, Chinese and English names
    _etnet_url = 'http://gateway.etnet.com.hk/WCData/snapshot.jsp?code=%s'

    @staticmethod
    def get_details(symbol, flags=None):
        details = common.StockDetails(symbol)
        return details
