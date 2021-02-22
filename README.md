# Description
Web application to play the investment game...for science!

# Installation
Clone the git repository
- ```git clone https://github.com/psipeter/investment-game-webapp.git```
- (Start a virtual environment, I use pipenv)
Install dependencies
- ```pip install django numpy scipy matplotlib seaborn mpld3```

# Production
In ```settings.py```
- set ```DEBUG=False```
- create a new ```SECRET_KEY``` by loading from an environment variable or reading from a server-only file
