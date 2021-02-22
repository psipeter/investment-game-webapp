# Description
Web application to play the investment game...for science!

# Installation
Clone the git repository
- ```git clone https://github.com/psipeter/investment-game-webapp.git```
- (Start a virtual environment, I use pipenv)
Install dependencies
- ```pip install django numpy scipy matplotlib seaborn mpld3```

# Create the database and an administrator
- ```python manage.py makemigrations```
- ```python manage.py migrate```
- ```python manage.py createsuperuser ```

# Run the server
- ```python manage.py runserver```
- (user) navigate to http://127.0.0.1:8000/
- (admin) navigate to http://127.0.0.1:8000/admin/


# Production
In ```settings.py```
- set ```DEBUG=False```
- create a new ```SECRET_KEY``` by loading from an environment variable or reading from a server-only file
