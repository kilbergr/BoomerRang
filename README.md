# BoomerRang

BoomerRang is an API that advocacy organizations can use to connect citizens with civic and political leaders by allowing individuals to schedule automated calls. The first phase has concluded when an operational prototype has been deployed on Heroku. The second phase has concluded when we have deployed using Terraform with our own AWS resources.

![BoommerRang flow diagram](https://github.com/trussworks/BoomerRang/blob/master/boomerrang_flow_diagram.png)

## Prerequisites:

 1. [pyenv](https://github.com/yyuu/pyenv#homebrew-on-mac-os-x)
 2. [pyenv virtualenv](https://github.com/yyuu/pyenv-virtualenv#installing-with-homebrew-for-os-x-users)
 3. [postgres](https://www.postgresql.org/download/macosx/): `brew install postgresql`
 4. [ngrok](https://ngrok.com/): To install version 2 of ngrok, do NOT use homebrew. Instead, follow instructions from their site. We are using version [2.1.18](https://dl.equinox.io/ngrok/ngrok/stable/archive). Make sure to move the application from wherever you unzip it into `/usr/local/bin/ngrok`.

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
	* `ALTER USER admin CREATEDB`

## Setting Your Environment Variables

The app requires environment variables to be set with your Twilio account keys and number.

## To set environment variables locally, create a file called `.env` here, with the twilio variables and the ngrok url resulting from running ngrok:

	TWILIO_ACCOUNT_SID=<TWILIO_ACCOUNT_SID>
	TWILIO_AUTH_TOKEN=<TWILIO_AUTH_TOKEN>
	TWILIO_NUMBER=<+15555555555>
	OUTBOUND_URL='http://<NGROKURL>.ngrok.io/outbound/'
	CALL_STATUS_URL='http://<NGROKURL>.ngrok.io/call-status/'

* Note: If you are running with Twilio TEST credentials, you must use the Twilio TEST phone number (+15005550006). If you run the app with real Twilio credentials, you should use a real Twilio number provisioned for this app.

## Running the app locally:

1. To manually start the postgres server, run `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start`.
	* Note: to have postgres automatically run at login, run `ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents`.
2. To run ngrok on port 4567, run `ngrok http 4567` in a terminal tab.
    * Note: ngrok must be running on the same port as django.
3. In the terminal window where you've run ngrok, you'll see a session status with information. Find the forwarding url (will look like `Forwarding http://4af77496.ngrok.io -> localhost:4567`). Take that url and save it in your .env file in the outbound and call status urls (with the appropriate path). This will end up looking something like:
`OUTBOUND_URL='http://4af77496.ngrok.io/outbound/'
CALL_STATUS_URL='http://4af77496.ngrok.io/call-status/'`.
You must do this BEFORE running the server.
4. Go to the Twilio console (under Home / Phone Numbers / Manage Numbers / Active Numbers /) in the Configure tab. Change the webhook urls under primary handler fails and call status change to match the ngrok urls in your .env file.
5. To run the server on port 4567, run `python manage.py runserver 4567` in a separate terminal tab.
	* If you see this: `django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured. Please supply the ENGINE value. Check settings documentation for more details.`, run this in your terminal:
	`export DATABASE_URL=postgres://127.0.0.1:5432/boomerang_db`. This sets the environmental variable locally that django needs to look to the local postgres database.
6. Point your browser to: <http://127.0.0.1:4567> to see BoomerRang.

## Testing:

1. To run tests, simply run `python manage.py test` from your BoomerRang env
2. To determine test coverage, run `coverage run --source boomerrang manage.py test` from your BoomerRang env. Then run either `coverage report` to see coverage in your terminal. If you'd like to see which lines are covered or view coverage in your browser, run `coverage html` then `open htmlcov/index.html`. From there you can click around to the different files to see where test coverage is lacking.
