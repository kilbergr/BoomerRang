# BoomerRang

BoomerRang is an API that advocacy organizations can use to connect citizens with civic and political leaders by allowing individuals to schedule automated calls. The first phase has concluded when an operational prototype has been deployed on Heroku. The second phase has concluded when we have deployed using Terraform with our own AWS resources.

![BoommerRang flow diagram](https://github.com/trussworks/BoomerRang/blob/master/boomerrang_flow_diagram.png)

## Prerequisites:

 1. [pyenv](https://github.com/yyuu/pyenv#homebrew-on-mac-os-x)
 2. [pyenv virtualenv](https://github.com/yyuu/pyenv-virtualenv#installing-with-homebrew-for-os-x-users)
 3. [postgres](https://www.postgresql.org/download/macosx/): `brew install postgresq`
 4. [ngrok](https://ngrok.com/): To install version 2 of ngrok, do NOT use homebrew. Instead, follow instructions from their site. We are using version 2.1.18. Make sure to move the application from wherever you unzip it into `/usr/local/bin/ngrok`.

## Virtualenv and Repo Setup:

 1. In your root directory, install python 3: `pyenv install 3.5.0`.
 2. Clone this repo via `git clone https://github.com/trussworks/BoomerRang`.
 3. Set the python version of your newly-created virtual environment to 3.5.0 with pyenv:
	* `pyenv local 3.5.0`.
 4. Create a virtualenv and install requirements:
	* `pyenv virtualenv <my_virtual_env> && pyenv activate <my_virtual_env>`
 5. Install requirements: `pip install -r requirements.txt`.
 6. Activate [pre-commit](http://pre-commit.com/) hooks by running `pre-commit install`.

## Postgres setup:

1. Open psql shell via `psql`.
	* If you can't connect to your psql shell (`error: psql: FATAL:  database "username" does not exist`), use the following command in your shell to create your default db with the following command:
	`/usr/local/bin/createdb <username>`
	* Once connected, create db in psql shell: `CREATE DATABASE boomerrang_db;`

2. In psql shell, create role that corresponds to app:

	* `CREATE ROLE admin WITH LOGIN PASSWORD 'trussadmin';`
	* You will likely also want to create a superuser role--currently have one 'truss':
	 `python manage.py createsuperuser`

## Setting Your Environment Variables

The app requires environment variables to be set with your Twilio account keys and number.

## To set environment variables locally, create a file called `.env` here, with the following variables set with twilio test account values:

	TWILIO_ACCOUNT_SID=<TEST_ACCOUNT_SID>
	TWILIO_AUTH_TOKEN=<TEST_AUTH_TOKEN>
	TWILIO_NUMBER=<(555) 555-5555>

## Running the app:

1. To manually start the postgres server, run `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start`.
	* Note: to have postgres automatically run at login, run `ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents`.
2. To run ngrok on port 4567, run `ngrok http 4567` in one terminal tab.
    * Note: ngrok must be running on the same port as django.
3. To run the server on port 4567, run `python manage.py runserver 4567` in a separate terminal tab.
	* If you see this: `django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured. Please supply the ENGINE value. Check settings documentation for more details.`, run this in your terminal:
	`export DATABASE_URL=postgres://trussel:pwd@127.0.0.1:5432/boomerang_db`. This sets the environmental variable locally that django needs to look to the local postgres database.
4. Point your browser to: <http://127.0.0.1:4567> to see things.
