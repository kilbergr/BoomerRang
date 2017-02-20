# BoomerRang

BoomerRang is an API that advocacy organizations can use to connect citizens with civic and political leaders by allowing individuals to schedule automated calls. The first phase has concluded when an operational prototype has been deployed on Heroku. The second phase has concluded when we have deployed using Terraform with our own AWS resources.

![BoommerRang flow diagram](https://github.com/trussworks/BoomerRang/blob/master/boomerrang_flow_diagram.png)

## Prerequisites:

 1. [pyenv](https://github.com/yyuu/pyenv#homebrew-on-mac-os-x)
 2. [pyenv virtualenv](https://github.com/yyuu/pyenv-virtualenv#installing-with-homebrew-for-os-x-users)

## Virtualenv and Repo Setup:

 1. In your root directory, install python 3: `pyenv install 3.5.0`.
 2. Clone this repo via `git clone https://github.com/trussworks/BoomerRang`.
 3. Create a virtualenv and install requirements:
 	* `pyenv virtualenv <my_virtual_env> && pyenv activate <my_virtual_env>`
 4. Set the python version of your newly-created virtual environment to 3.5.0 with pyenv:
 		`pyenv local 3.5.0`.
 5. Install requirements: `pip install -r requirements.txt`.

## Postgres setup:

1. Install postgres: `brew install postgresql`.
2. Open psql shell via `psql`.
	* If you can't connect to your psql shell (`error: psql: FATAL:  database "username" does not exist`), use the following command in your shell to create your default db with the following command:
	`/usr/local/bin/createdb <username>`
	* Once connected, create db in psql shell: `CREATE DATABASE boomerrang_db;`

3. In psql shell, create role that corresponds to app:

	* `CREATE ROLE admin WITH LOGIN PASSWORD 'trussadmin';`
 	* You will likely also want to create a superuser role--currently have one 'truss':
	 `python manage.py createsuperuser`

## Setting Your Environment Variables

The app requires environment variables to be set with your Twilio account keys and number.

## To set environment variables locally, run:

```export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxx
export TWILIO_AUTH_TOKEN=yyyyyyyyyyyyyyyyy
export TWILIO_NUMBER=+15556667777```

TODO: @Andie: Figure out how we're going to deal with key-setting - git ignore? local_settings file? Temporary solution is to set these in your bash profile.

## Running the app:

1. To manually start the postgres server, run `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start`.
	* Note: to have postgres automatically run at login, run `ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents`.
2. To run the server, run `python manage.py runserver`
	* If you see this: `django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured. Please supply the ENGINE value. Check settings documentation for more details.`, run this in your terminal:
	`export DATABASE_URL=postgres://trussel:pwd@127.0.0.1:5432/boomerang_db`. This sets the environmental variable locally that django needs to look to the local postgres database.
3. Point your browser to: <http://127.0.0.1:8000/users> to see things.
