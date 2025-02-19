#from cs50 import SQL
from flask_session import Session
from flask import Flask
import os
from cs50 import SQL

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
db = SQL("sqlite:///copy.db")

