# Parlay Island Backend

The Parlay Island backend provides a web API to access and manipulate question
and student data.

Written in Django.

## Setup

### Install dependencies

1. `python3 -m pip install pipenv`
2. `pipenv install`
3. Install docker

### Local development

#### Run locally

1. Run `./start_db.sh` (this command will start a local database )
2. Run `pipenv install`
3. Move `.env.local` to `.env`
4. Run `pipenv run python3 manage.py runserver`
