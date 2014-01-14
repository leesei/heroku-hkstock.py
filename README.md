Heroku app: heroku-hkstock (python)
=================

Service that parse stock quotes from website to JSON.

This app is *DEPRECATED* by the [Node.js version](https://github.com/leesei/heroku-hkstock).  
It now serves as a scraper reference for the various websites.

## Usage

```bash
git clone https://github.com/leesei/heroku-hkstock.py.git
heroku apps:create NAME
git push heroku master
heroku addons:add rediscloud
heroku addons:add newrelic:stark
heroku config:set NEW_RELIC_APP_NAME="NAME"
heroku config:set TZ="heroku"
```

## Endpoints

* /  
  Test Redis usage and timezone
* /debug  
  List scrapers
* /rtq?symbol=_symbol_[&src=_scraper_]  
  Quote service

## Local server

Prerequisite (do these once only):

```bash
virtualenv env
. env/bin/activate
pip install -r requirements.txt  # rerun if updated
```

> lxml cannot be compiled on my machine

Run local server:

```bash
. env/bin/activate
source .env.source
foreman start web -f Procfile.local
```

## TODO

- Worker is not finished (Worker act as backend to scrape and push results to redis)
- multiple request handlers (using `unicorn`?)
- console app
