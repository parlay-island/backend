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
4. Run `pipenv run python3 manage.py runserver` (to run tests, run `pipenv run python3 manage.py test`)

You can turn off the database after developing locally using the docker dashboard or `docker stop {container-id}`. You
can find the container-id by running `./start_db.sh` which will tell you that it cannot start another container because:

```
The container name "/parlay-island-db" is already in use by container "{container-id}"
```

### Deployment configuration

In the instances of each deployment, the variables defined in `.env.local` must be defined in the deployment 
environment.
