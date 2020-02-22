# Trader Console

Create your own strategies using [BINANCE API](https://binance-docs.github.io/apidocs/spot/en/) and receive notifications in [Telegram](https://telegram.org/)

## Quickstart

Run the following commands to bootstrap your environment
```
git clone https://github.com/reijnnn/Trader-Console.git
cd trader-console
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

Before running, change the web application parameters in the file `config.py` or create your own config file with name like `config_dev.py` or `config_prd.py`. Change config file name in `run.app`

## `manage.py` command overview

Use command `python manage.py --help` for help

By default `manage.py` use `config.py`. To set another config use `--config` flag

Put your common management tasks in this file.
Migration commands already available with `db` prefix.

By default `manage.py` has these commands:
* `reset_db` — recreate all tables in the database. Usually, you don't need to use this command since it will erase all your data, but on the empty environment can be useful in the local environment
* `add_root_user` — create root user with role `SUPER_ADMIN`
* `print_table` — display all table rows

Run the following commands to create application database tables and perform the initial migration
```
python manage.py db init
python manage.py db migrate -m "Init migration"
python manage.py db upgrade
```
Run the following command to create root user with role `SUPER_ADMIN`
```
python manage.py add_root_user --login root --password r00tPWD#
```

## How to start

To run the web application use
```
nohup gunicorn -b 0.0.0.0:8085 run:app --pid --threads 2 gunicorn.pid &
```
Open http://127.0.0.1:8085/ and login as a root user

To kill the web application use
```
kill `cat gunicorn.pid`
```

## Migrations

Whenever a database migration needs to be made – run the following commands
```
python manage.py db migrate
```
This will generate a new migration script. Then run
```
python manage.py db upgrade
```
To apply the migration.

For a full migration command reference, run `python manage.py db --help`.
