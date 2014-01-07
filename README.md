Heroku app: heroku-hkstock (python)
=================

Service that parse stock quotes from website to JSON.

This app is *OBSOLETED* for the Node.js version.  
It now serves as a scraper reference for the various websites.

## Usage

```bash
git clone https://github.com/leesei/heroku-hkstock.py.git
heroku apps:create NAME
git push heroku master
heroku addons:add newrelic:stark
heroku config:set NEW_RELIC_APP_NAME="NAME"
heroku config:set TZ="heroku"
```

## Local server

Prerequisite (do these once only):

```bash
virtualenv env
. env/bin/activate
pip install -r requirements.txt  # rerun if updated
```

Run local server:

```bash
. env/bin/activate
source .env.source
foreman start web -f Procfile.local
```

## TODO

- Worker is not finished
- console app
