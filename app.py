from flask import redirect, render_template, request, session, jsonify, flash
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from config import app, db


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    novels = db.execute("SELECT name FROM novels ORDER BY name")
    return render_template("index.html", novels=novels)

@app.route("/novel/<name>")
def novel(name):
    novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ?", name)[0]["novel_id"]
    chapters = db.execute("SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_num", novel_id)

    return render_template("novel.html", chapters=chapters, name=name)

@app.route("/<name>/chapter-<int:num>")
def chapter(name, num):
    novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ?", name)[0]["novel_id"]
    chapter = db.execute("SELECT content, title FROM chapters WHERE novel_id = ? AND chapter_num = ?", novel_id, num)[0]
    previous = db.execute("SELECT chapter_num FROM chapters WHERE novel_id =  ? AND chapter_num = ?", novel_id, num - 1)
    next_chapter = db.execute("SELECT chapter_num FROM chapters WHERE novel_id = ? AND chapter_num = ?", novel_id, num + 1)

    return render_template("chapter.html", chapter=chapter, name=name, previous=previous, next_chapter=next_chapter)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        q = request.form.get("q")
        novels = db.execute("SELECT name FROM novels WHERE name LIKE ? ORDER BY name", "%" + q + "%")

        if novels:
            return render_template("search.html", novels=novels)

        return apology("novel not found", 404)
    q = request.args.get("q")
    novels = db.execute("SELECT name FROM novels WHERE name LIKE ? ORDER BY name", "%" + q + "%")
    return jsonify(novels)


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
            rows[0]["password"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
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
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation or confirmation != password:
            return apology("password must be the same", 400)
        elif not email:
            flash("Provide valid email")
            return redirect("/register")
            #return apology("provide vaild email", 403)
        try:
            session["user_id"] = db.execute(
                "INSERT INTO users(username, password, email, date) VALUES(?, ?, ?, ?)", username, generate_password_hash(password), email, datetime.today().strftime("%d %B %Y %H:%M"))

        except ValueError:
            return apology("user already exists, try login", 400)

        return redirect("/")
    else:
        return render_template("register.html")

@app.route('/create', methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        novel_name = request.form.get("name")
        about = request.form.get("about")
        author = db.execute("SELECT username FROM users WHERE user_id = ?", session["user_id"])

        try:
            db.execute("INSERT INTO novels(name, about, author, user_id) VALUES(?, ?, ?, ?)", novel_name, about, author, session["user_id"])
        except ValueError:
            pass

        return redirect("/profile")
    else:
        return render_template("create.html")


@app.route('/profile/')
@login_required
def profile():
    user = db.execute("SELECT * FROM users WHERE user_id = ?", session["user_id"])[0]
    return render_template("profile.html", user=user)

@app.route('/profile/comments')
@login_required
def user_comments():
    pass

@app.route('/profile/novels')
@login_required
def user_novels():
    novels = db.execute("SELECT * FROM novels WHERE user_id = ?", session["user_id"])
    return jsonify(novels)

@app.route('/profile/<name>/update', methods=["GET", "POST"])
@login_required
def update(name):
    if request.method == "POST":
        pass
    else:
        novel = db.execute("SELECT * FROM novels WHERE name = ?", name)[0]
        chapters = db.execute("SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_num", novel["novel_id"])

        return render_template("update.html", chapters=chapters, novel=novel)

@app.route("/profile/<name>/update/chapter-<int:chapter_num>", methods=["GET", "POST"])
@login_required
def update_chapter(name, chapter_num):
    novel_data = db.execute("SELECT * FROM novels WHERE name = ? AND user_id = ?", name, session["user_id"])[0]
    
    if request.method == "POST":
        pass
    else:
        chapter = db.execute("SELECT * FROM chapters WHERE chapter_num = ? AND novel_id = ?", chapter_num, novel_data["novel_id"])[0]
        return render_template("update_chapter.html", chapter=chapter, name=name)

@app.route('/delete/<novel>/<int:chapter_num>')
@login_required
def delete(novel, chapter_num=0):
    novel_data = db.execute("SELECT * FROM novels WHERE name = ? AND user_id = ?", novel, session["user_id"])[0]
    if chapter_num > 0:
        db.execute("DELETE FROM chapters WHERE chapter_num = ? AND novel_id = ?", chapter_num, novel_data["novel_id"])

        return redirect(f"/profile/{novel}/update")
    else:
        db.execute("DELETE FROM chapters WHERE novel_id = ?", novel_data["novel_id"])
        db.execute("DELETE FROM novels WHERE novel_id = ? AND name = ?", novel_data["novel_id"], novel)

        return redirect("/profile")
