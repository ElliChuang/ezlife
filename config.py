import os
from dotenv import load_dotenv
load_dotenv()

# SESSION_PW = os.environ.get("SESSION_PW")
MYSQL_PW = os.environ.get("MYSQL_PW")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
TOKEN_PW = os.environ.get("TOKEN_PW")
SECRET_KEY = os.environ.get("SECRET_KEY")

JSON_AS_ASCII = False
TEMPLATES_AUTO_RELOAD = True
JSON_SORT_KEYS = False