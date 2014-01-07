#!/usr/bin/env python

from datetime import datetime
import html2text
import json
import requests

import logging
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class StockDetails(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.valid = False

        self.nameEng = ""
        self.nameChi = ""
        # type: "stock" / "call"|"put"+" warrant" / "bull"|"bear"+" CBBC"
        self.type = None
        self.lot_size = None
        self.high52 = None
        self.low52 = None

        # derivatives only
        self.quote_ime = None
        self.strike = None  # execution price
        self.ratio = None
        self.gearing = None
        self.last_trading = None

    def __str__(self):
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self.__dict__)

    def dump(self, flags=None):
        if self.valid:
            print "[{}] {} type[{}]".format(self.symbol, self.nameEng, self.type)
        else:
            print "[{}] via {} invalid".format(self.symbol)


class StockQuote(object):
    def __init__(self, symbol):
        self.symbol = symbol
        self.valid = False

        # filled by implementation
        self.quote = None
        self.low = None
        self.high = None
        self.volume = None
        self.opening = None
        self.close_yest = None
        self.change_pct = None
        self.quote_time = None
        self.create_time = get_timestamp()
        self.complete_time = None

    def __str__(self):
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self.__dict__)

    def dump(self, flags=None):
        print
        if self.valid:
            print "[{}] quoted at {}".format(self.symbol, self.quoteTime)
        else:
            print "[{}] invalid".format(self.symbol)


def data2text(data, **kwargs):
    ''' wrapper for html2text.HTML2Text()

    Args:
        data: input data in utf-8
        kwargs: dict of parameters for html2text
                  body_width
                  ignore_links
                  ignore_images
                  ignore_emphasis
    '''
    LOG.debug('%s', str(kwargs))

    h = html2text.HTML2Text()
    h.body_width = kwargs.get('body_width', 0)
    h.ignore_links = kwargs.get('ignore_links', True)
    h.ignore_images = kwargs.get('ignore_images', True)
    h.ignore_emphasis = kwargs.get('ignore_emphasis', True)

    LOG.debug('    url[%s] body_width[%d], ignore_links[%s] ignore_images[%s] ignore_emphasis[%s]',
              h.baseurl, h.body_width, h.ignore_links, h.ignore_images, h.ignore_emphasis)

    # convert to text
    # leaves to webapp to encode to 'utf-8', saving CPU time
    # (as we've set charset in header)
    # return h.handle(data).encode('utf-8')
    return h.handle(data)


def download_webpage(url, encoding=None, noencode=False):
    # spoof User-Agent, urllib2 is blocked
    headers = {'User-Agent':
               'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17'}
    request = requests.get(url, headers=headers, timeout=10)
    if encoding:
        request.encoding = encoding
    else:
        encoding = request.encoding

    LOG.info('Fetched [%s] url <%s> (noencode[%r])', encoding, url, noencode)

    if noencode:
        return request.content
    else:
        # get text (decoding is done by requests)
        return request.text


def get_timestamp():
    """ return timestamp

        date is not useful in our applcation
    """
    return datetime.now().isoformat()
