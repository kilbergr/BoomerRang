# BoomerRang
Call back service for baby boomers on the go.

# PythonToDo:

## Setup:
 1. In your root directory, install python version 3.5.0 with `pyenv install 3.5.0`.
 2. Set the python version of your newly-created virtual environment to 3.5.0 with pyenv: `pyenv local 3.5.0`.
 3. Clone this repo via `git clone https://github.com/trussworks/BoomerRang`. (Set remotes according to: http://truss.works/blog/2014/12/31/a-lightweight-resilient-git-workflow-for-small-teams)
 4. To install requirements, run `pip install -r requirements.txt`.

## Postgres setup:

1. Install postgres: `brew install postgresql`.
2. Open psql shell via `psql`.
	* If you can't connect to your psql shell (`error: psql: FATAL:  database "username" does not exist`), use the following command in your shell to create your default db with the following command: `/usr/local/bin/createdb <username>`
	* 	Once connected, create db in psql shell: CREATE DATABASE boomerang_db;

3. In psql shell, create role that corresponds to app:
 `CREATE ROLE admin WITH LOGIN PASSWORD 'trussadmin';`  
 likely also want to create a superuser role--currently have one 'truss':
 `python manage.py createsuperuser`


## Running the app:

1. To manually start the postgres server, run `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start`.
	* Note: to have postgres automatically run at login, run `ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents`.
2. To run the server, run `python manage.py runserver`
	* If you see this: `django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured. Please supply the ENGINE value. Check settings documentation for more details.`, run this in your terminal: `export DATABASE_URL=postgres://trussel:pwd@127.0.0.1:5432/boomerang_db`. This sets the environmental variable locally that django needs to look to the local postgres database.
3. Point your browser to: http://127.0.0.1:8000/users to see things.
