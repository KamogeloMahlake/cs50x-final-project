from cs50 import SQL
from flask_session import Session
from flask import Flask

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = "./uploads"
Session(app)

db = SQL("sqlite:///database.db")
