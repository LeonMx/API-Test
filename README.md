# API-Test

#### Install Python 3 and PosgreSQL

```shell
sudo apt-get update
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib
```

#### Config PosgreSQL
Log into an interactive Postgres session by typing:
```shell
sudo -u postgres psql
```

Create a database:
```posgresql
CREATE DATABASE elearning;
```

Create a user:
```posgresql
CREATE USER cleon WITH PASSWORD '123456';
```

Set a format recommend:
```posgresql
ALTER ROLE cleon SET client_encoding TO 'utf8';
ALTER ROLE cleon SET default_transaction_isolation TO 'read committed';
ALTER ROLE cleon SET timezone TO 'UTC';
```

Give our database user access rights to the database we created:
```posgresql
GRANT ALL PRIVILEGES ON DATABASE elearning TO cleon;
```

Exit postgres session:
```posgresql
\q
```

#### Create a Virtual Environment
Install virtual environment:
```shell
sudo pip3 install virtualenv
```

Create a virtual environment to store our Django project’s Python requirements by typing:
```shell
virtualenv projectapitest
```

Activate virtual enviroment created:
```shell
source projectapitest/bin/activate
```
#### Clone project
```shell
git clone https://github.com/LeonMx/API-Test.git
cd API-Test
```
#### Install libraries 
```shell
pip3 install -r requirements.txt
```
#### Run server
Execute migrate
```shell
python3 manage.py migrate
```
Create superuser
```shell
python3 manage.py createsuperuser
```
Start run server
```shell
python3 manage.py runserver
```
