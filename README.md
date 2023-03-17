A prototype for storing and serving alignment data.

# Local Development

## Run Frontend
In the `client/` directory...

### Install dependencies
```bash
npm install
```

### Start local server
```bash
npm run dev
```
...

## Run Backend
In the `server/` directory...

### Install dependencies
```bash
poetry install
```

### Optional: Use PostgreSQL
```bash
createdb alignmentapi
export DATABASE_URL=postgres://localhost/alignmentapi
```

### Run initial migrations

```bash
poetry run ./manage.py migrate
```

### Populate alignment database
_runtime ~20 mins_

```bash
poetry run ./manage.py shell < alignment_api/pipelines/load_alignments.py
```

### Start local server

```bash
poetry run ./manage.py runserver
```

## Deploy Backend

- Get access to the app on Heroku
- Authenticate using the [Heroku CLI](postgres://localhost/alignmentapi):
```bash
heroku login
```
- Link the site to the Heroku app:
```bash
heroku git:remote -a clear-alignment-api
```
- Deploy via Git push
```bash
git push heroku <branch-name>:main
```

## Update Data on Heroku
- Put site into maintenance mode
```bash
heroku maintenance
:on
```
- Reset the existing database
```bash
heroku pg:reset DATABASE --confirm clear-alignment-api
```
- Push local database up to Heroku
```
heroku pg:push alignmentapi DATABASE
```
- Take site out of maintenance mode
```bash
heroku maintenance:off
```
- Browse to /alignment
```
open https://clear-alignment-api.herokuapp.com/alignment/
```
