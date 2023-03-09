web: cd server && gunicorn alignmentapi.wsgi --threads=3 --access-logfile -
release: cd server && python manage.py migrate --noinput
