from flask import redirect, render_template, session
from functools import wraps
from re import match
from cs50 import SQL

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def get_novel_data(database, name="", user_id=""):
    if name and user_id:
        return database.execute(
            "SELECT * FROM novels WHERE name = ? AND user_id = ?", name, user_id
        )
    elif name:
        return database.execute("SELECT * FROM novels WHERE name = ?", name)
    elif user_id:
        return database.execute(
            "SELECT * FROM novels WHERE user_id = ? ORDER BY name", user_id
        )
    else:
        return database.execute("SELECT * FROM novels ORDER BY name")


def get_chapter_data(name, novel_id="", chapter_num=""):
    database = SQL(f"sqlite:///databases/{name.replace(' ', '_')}.db")
    print(chapter_num, novel_id)
    if novel_id and chapter_num:
        return database.execute(
            "SELECT * FROM chapter WHERE novel_id = ? AND chapter_num = ?",
            novel_id,
            chapter_num,
        )
    elif novel_id:
        return database.execute(
            "SELECT * FROM chapter WHERE novel_id = ? ORDER BY chapter_num", novel_id
        )


def test_email(email):
    if match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return True
    return False


def test_password(password):
    if match(
        r"^(?=.*[A-Z])(?=(.*[a-z]){1,})(?=(.*[\d]){1,})(?=(.*[\W]){1,})(?!.*\s).{8,}$",
        password,
    ):
        return True
    return False


def string_to_html(text):
    text = text.split("\n")
    output = ""
    for i in text:
        output += f"<p>{i}</p>"

    return output


def allowed_file(filename):
    try:
        name, ext = filename.split(".")

        if ext in ALLOWED_EXTENSIONS and name:
            return True
        return False
    except Exception:
        return False
