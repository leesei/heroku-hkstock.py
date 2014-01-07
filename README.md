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

## TODO

- Worker is not finished
- console app
- local server instructions
