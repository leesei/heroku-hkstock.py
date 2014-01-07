#!/usr/bin/env python

from datetime import datetime
import json
import logging
import os
import pyclbr
from pprint import pprint

import webapp2
import webapp2_extras.routes

import redis
redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
redisdb = redis.from_url(redis_url)

# note: this is the global instance
from worker import worker
import quote_providers

logging.basicConfig(
    format='%(levelname)s/%(module)s:%(lineno)d: %(message)s',
    level=logging.INFO)


def main(request, *args, **kwargs):
    redisdb.set('isotime', datetime.now().isoformat())
    redisdb.set('time', datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    response = webapp2.Response()
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.out.write(redisdb.get('isotime') + '\n' + redisdb.get('time'))
    return response


def env(request):
    logging.debug(request)
    response = webapp2.Response()
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.out.write(json.dumps(os.environ.data))
    return response


def debug(request):
    response = webapp2.Response()
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.out.write(pyclbr.readmodule('quote_providers').keys())
    return response


def redis_keys(request):
    response = webapp2.Response()
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.out.write(json.dumps(redisdb.keys()))
    return response


def redis_flushdb(request):
    return webapp2.Response('Flushed')


class StaticFileHandler(webapp2.RequestHandler):
    def get(self, path):
        abs_path = os.path.abspath(os.path.join(self.app.config.get('webapp2_static.static_file_path', 'static'), path))
        if os.path.isdir(abs_path) or abs_path.find(os.getcwd()) != 0:
            self.response.set_status(403)
            return
        try:
            import mimetypes
            f = open(abs_path, 'r')
            self.response.headers['Content-Type'] = mimetypes.guess_type(abs_path)[0]
            self.response.out.write(f.read())
            f.close()
        except:
            self.response.set_status(404)


class StockQuote(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

        # first of all, test if we have symbol param in the query
        symbol = self.request.get('symbol')
        if not symbol:
            return

        provider = quote_providers.LUT.get(
            self.request.get('src', 'aamobile'),
            quote_providers.DEFAULT_PROVIDER)

        self.response.out.write(provider.quote(symbol).toJSON())
        return


class RedisStockQuote(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

        # first of all, test if we have symbol param in the query
        symbol = self.request.get('symbol')
        if not symbol:
            return

        cache = redisdb.get(symbol.toJSON())
        if cache:
            self.response.out.write(cache)
            return

        # cache miss, use Worker to get quote (blocking)
        self.response.out.write(worker.get_quote(symbol).toJSON())
        return

# main routes
routes = [
    webapp2.SimpleRoute(r'/?', handler=main),
    webapp2.SimpleRoute(r'/env/?', handler=env),
    webapp2.SimpleRoute(r'/debug/?', handler=debug),
    webapp2.SimpleRoute(r'/redisdb-keys/?', handler=redis_keys),
    webapp2.SimpleRoute(r'/redisdb-flush/?', handler=redis_flushdb),
    webapp2.SimpleRoute(r'/static/(.+)', handler=StaticFileHandler),
    webapp2_extras.routes.RedirectRoute(
        r'/favicon.ico',
        redirect_to=r'/static/favicon.ico'),
    webapp2.SimpleRoute(r'/rtq', handler=StockQuote),
    webapp2.SimpleRoute(r'/dbrtq', handler=RedisStockQuote),
]

app = webapp2.WSGIApplication(routes, debug=True)

# (manually) install hook for newrelic
if os.getenv('NEW_RELIC_APP_NAME'):
    import newrelic
    app = newrelic.agent.wsgi_application()(app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 5052))
    httpd = make_server(host='0.0.0.0', port=port, app=app)
    print 'Serving HTTP on port %d ...' % port
    # Respond to requests until process is killed
    httpd.serve_forever()
