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

### API-Rest
API root path is [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)

#### How to use
Exists two way to API consuming:
- **Using site API**
  Login here [http://127.0.0.1:8000/api/v1/users/login](http://127.0.0.1:8000/api/v1/users/login) and navigate on [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)
- **Sending request API**
Login with send `POST` with params `username` and `password` on [http://127.0.0.1:8000/api/v1/users/login](http://127.0.0.1:8000/api/v1/)
Get `authtoken` returned and use it on request header with name `Authorization` 

To know the parameters to send, execute the request method `OPTIONS`

#### CRUD Users
| Method                         | URI          | Permission    |
|--------------------------------|--------------|---------------|
| `OPTIONS` `GET` `POST`         | `users`      | `IsAdminUser` |
| `OPTIONS` `GET` `PUT` `DELETE` | `users/{id}` | `IsAdminUser` |

### CRUD Students
| Method                         | URI             | Permission                    |
|--------------------------------|-----------------|-------------------------------|
| `OPTIONS` `GET` `POST`         | `students`      | `IsAdminUser` `IsTeacherUser` |
| `OPTIONS` `GET` `PUT` `DELETE` | `students/{id}` | `IsAdminUser` `IsTeacherUser` |

### CRUD Teachers
| Method                         | URI             | Permission                    |
|--------------------------------|-----------------|-------------------------------|
| `OPTIONS` `GET` `POST`         | `teachers`      | `IsAdminUser` `IsTeacherUser` |
| `OPTIONS` `GET` `PUT` `DELETE` | `teachers/{id}` | `IsAdminUser` `IsTeacherUser` |

### CRUD Courses
| Method          | URI            | Permission                    |
|-----------------|----------------|-------------------------------|
| `OPTIONS` `GET` | `courses`      | `ANY`                         |
| `OPTIONS` `GET` | `courses/{id}` | `ANY`                         |
| `POST`          | `courses`      | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `courses/{id}` | `IsAdminUser` `IsTeacherUser` |

### CRUD Lessons
| Method          | URI                         | Permission                    |
|-----------------|-----------------------------|-------------------------------|
| `OPTIONS` `GET` | `lessons`                   | `ANY`                         |
| `OPTIONS` `GET` | `lessons/{id}`              | `ANY`                         |
| `POST`          | `lessons`                   | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `lessons/{id}`              | `IsAdminUser` `IsTeacherUser` |
| `OPTIONS` `GET` | `courses/{id}/lessons`      | `ANY`                         |
| `OPTIONS` `GET` | `courses/{id}/lessons/{id}` | `ANY`                         |
| `POST`          | `courses/{id}/lessons`      | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `courses/{id}/lessons/{id}` | `IsAdminUser` `IsTeacherUser` |

### CRUD Questions
| Method          | URI                                        | Permission                    |
|-----------------|--------------------------------------------|-------------------------------|
| `OPTIONS` `GET` | `questions`                                | `ANY`                         |
| `OPTIONS` `GET` | `questions/{id}`                           | `ANY`                         |
| `POST`          | `questions`                                | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `questions/{id}`                           | `IsAdminUser` `IsTeacherUser` |
| `OPTIONS` `GET` | `courses/{id}/questions`                   | `ANY`                         |
| `OPTIONS` `GET` | `courses/{id}/lessons/{id}/questions/{id}` | `ANY`                         |
| `POST`          | `courses/{id}/lessons/{id}/questions`      | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `courses/{id}/lessons/{id}/questions/{id}` | `IsAdminUser` `IsTeacherUser` |

### CRUD Answers
| Method          | URI                                                     | Permission                    |
|-----------------|---------------------------------------------------------|-------------------------------|
| `OPTIONS` `GET` | `answers`                                               | `ANY`                         |
| `OPTIONS` `GET` | `answers/{id}`                                          | `ANY`                         |
| `POST`          | `answers`                                               | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `answers/{id}`                                          | `IsAdminUser` `IsTeacherUser` |
| `OPTIONS` `GET` | `courses/{id}/questions/{id}/answers`                   | `ANY`                         |
| `OPTIONS` `GET` | `courses/{id}/lessons/{id}/questions/{id}/answers/{id}` | `ANY`                         |
| `POST`          | `courses/{id}/lessons/{id}/questions/{id}/answers`      | `IsAdminUser` `IsTeacherUser` |
| `PUT` `DELETE`  | `courses/{id}/lessons/{id}/questions/{id}/answers/{id}` | `IsAdminUser` `IsTeacherUser` |

### Extra
| Method           | URI                                         | Permission      |
|------------------|---------------|-----------------------------|-----------------|
| `POST`           | `users/login`                               | `ANY`           |
| `GET`            | `users/info`                                | `ANY`           |
| `OPTIONS` `POST` | `lessons/{id}/select_answers`               | `IsStudentUser` |
| `OPTIONS` `POST` | `courses/{id}/lessons/{id}/select_answers`  | `IsStudentUser` |


## Why Django Rest framework
Because it's a powerful and flexible toolkit for building Web APIs and its community is wide, and its learning curve is fast, and its documents is just easy.