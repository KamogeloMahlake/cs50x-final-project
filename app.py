from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

db = SQL("sqlite:///novels.db")
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    novels = db.execute("SELECT * from novels ORDER BY name")

    for novel in novels:
        novel["novel_name_id"] = novel["name"].replace(" ", "") + "-" + str(novel["novel_id"])
    return render_template("index.html", novels=novels)

@app.route("/search", methods=["GET", "POST"])
def search():
    q = request.args.get("q")
    if request.method == "POST":
        q = request.form.get("q")
        novels = db.execute("SELECT * FROM novels WHERE name LIKE ?", "%" + q + "%")

        if novels:
            for novel in novels:
                novel["novel_name"] = novel["name"].replace(" ", "")
            return render_template("search.html", novels=(novels))

        return apology("novel not found", 404)   
    novels = db.execute("SELECT * FROM novels WHERE name LIKE ?", "%" + q + "%")
    return jsonify(novels)


@app.route("/novel/<novel_name_id>")
def novels(novel_name_id):
    novel_name, novel_id = novel_name_id.split("-")
    novel = db.execute("SELECT * FROM novels WHERE novel_id = ?", int(novel_id))
    chapters = db.execute("SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_num", int(novel_id))

    for i in chapters:
        i["chapter_num"] = str(i["chapter_num"])
        i["chapter_novelname_novelid_chapterid_chapter_num"] = novel_name + "-" + novel_id + "-" + str(i["chapter_id"]) + "-" + i["chapter_num"]

        if not i["title"]:
            db.execute("UPDATE chapters SET title = ? WHERE chapter_id = ? and novel_id = ?", "Chapter " + i["chapter_num"], i["chapter_id"], int(novel_id))
    return render_template("novels.html", chapters=chapters, novelname=novel[0]["name"])

@app.route("/chapter/<chapter_novelname_novelid_chapterid_chapter_num>")
def chapter(chapter_novelname_novelid_chapterid_chapter_num):
    novel_name, novel_id, chapter_id, chapter_num = chapter_novelname_novelid_chapterid_chapter_num.split("-")
    content = db.execute("SELECT content FROM chapters WHERE chapter_id = ?", int(chapter_id))[0]["content"]
    novel = db.execute("SELECT name FROM novels WHERE novel_id = ?", int(novel_id))[0]["name"]
    
    previous = db.execute("SELECT chapter_id FROM chapters WHERE novel_id = ? AND chapter_num = ?", int(novel_id), int(chapter_num) - 1)
    next = db.execute("SELECT chapter_id FROM chapters WHERE novel_id = ? AND chapter_num = ?", int(novel_id), int(chapter_num) + 1)

    return render_template("chapters.html", chapter_num=chapter_num, content=content, novel=novel, next=next, previous=previous, novel_name=novel_name, novel_id=novel_id, previous_num=(int(chapter_num) - 1), next_num=(int(chapter_num) + 1))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation or confirmation != password:
            return apology("password must be the same", 400)

        try:
            session["user_id"] = db.execute(
                "INSERT INTO users(username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        except ValueError:
            return apology("user already exists, try login", 400)

        return redirect("/")
    else:
        return render_template("register.html")

