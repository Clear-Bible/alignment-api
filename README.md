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

### Run initial migrations

```cli
poetry run ./manage.py migrate
```

### Start local server

```cli
poetry run ./manage.py runserver
```


