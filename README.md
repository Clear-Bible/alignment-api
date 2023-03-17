A prototype for storing and serving alignment data.

# Local Development

## Run Frontend
In the `client/` directory...

### Install dependencies
```cli
npm install
```

### Start local server
```cli
npm run dev
```
...

## Run Backend
In the `server/` directory...

### Install dependencies
```cli
poetry install
```

### Optional: Use PostgreSQL
```cli
createdb alignmentapi
export DATABASE_URL=postgres://localhost/alignmentapi
```

### Run initial migrations

```cli
poetry run ./manage.py migrate
```

### Populate alignment database
_runtime ~20 mins_

```cli
poetry run ./manage.py shell < alignment_api/pipelines/load_alignments.py
```

### Start local server

```cli
poetry run ./manage.py runserver
```

## Deploy Backend

- Get access to the app on Heroku
- Authenticate using the [Heroku CLI](postgres://localhost/alignmentapi):
```cli
heroku login
```
- Link the site to the Heroku app:
```cli
heroku git:remote -a clear-alignment-api
```
- Deploy via Git push
```cli
git push heroku <branch-name>:main
```

## Update Data on Heroku
- Put site into maintenance mode
```cli
heroku maintenance
:on
```
- Reset the existing database
```cli
heroku pg:reset DATABASE --confirm clear-alignment-api
```
- Push local database up to Heroku
```
heroku pg:push alignmentapi DATABASE
```
- Take site out of maintenance mode
```cli
heroku maintenance:off
```
- Browse to /alignment
```
open https://clear-alignment-api.herokuapp.com/alignment/
```
