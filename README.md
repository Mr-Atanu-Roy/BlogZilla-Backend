
# BlogZilla/Backend: Blogging Website

This is the backend for BlogZilla blogging Website.
Contains api for Blogzilla.


## Tech Stack

**Server:** Python, Django, Django Rest Framework

**Database:** SQLite (can be upgraded to MySQL/Postgress for dev)

**Authentication:** JWT auth



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file (check the `.env.sample` file)

- Django Project settings

`DEBUG = TRUE`

`SECRET_KEY = "django-insecure-jy(xzggyb5r@ctf^)^=fv_wu_yj94+kbocqsn@$)ak1cnyu+vl"`

- For sending emails

`EMAIL_HOST_USER = "email address from which email will be send"`

`EMAIL_HOST_PASSWORD = "its app password"`



## Installation

Create a folder and open terminal and install this project by
command 
```bash
git clone https://github.com/Mr-Atanu-Roy/BlogZilla-Backend

```
or simply download this project from https://github.com/Mr-Atanu-Roy/BlogZilla-Backend

In project directory Create a virtual environment of any name(say env)

```bash
  virtualenv env

```
Activate the virtual environment

For windows:
```bash
  env\Script\activate

```
Install dependencies
```bash
  pip install -r requirements.txt

```
Run migration commands
```bash
  py manage.py makemigrations
  py manage.py migrate

```

Create a super user
```bash
  py manage.py createsuperuser

```
Then add some data into database


To run the project in your localserver
```bash
  py manage.py runserver
  
```

To allow request from any end point add the origin to `CORS_ORIGIN_WHITELIST` in settings.py


## Author

- [@Atanu Roy](https://github.com/Mr-Atanu-Roy)