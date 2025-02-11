from flask import redirect, render_template, request, session, jsonify, flash
from helpers import apology, login_required, get_novel_data, get_chapter_data, test_email, test_password
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
    novels = get_novel_data(db)
    return render_template("index.html", novels=novels)

@app.route("/novel/<name>")
def novel(name):
    novel = get_novel_data(db, name=name)[0]
    chapters = get_chapter_data(db, novel_id=novel["novel_id"])

    return render_template("novel.html", chapters=chapters, novel=novel)

@app.route("/<name>/chapter-<int:num>")
def chapter(name, num):
    novel_id = get_novel_data(db, name=name)[0]["novel_id"]
    chapter = get_chapter_data(db, novel_id=novel_id, chapter_num=num)[0]
    previous = get_chapter_data(db, novel_id=novel_id, chapter_num=(num-1))
    next_chapter = get_chapter_data(db, novel_id=novel_id, chapter_num=num+1)

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
        elif not password or not test_password(password):
            return apology("must contain uppercase and lowercase, digits, special character and have a minimum length of 8", 400)
        elif not confirmation or confirmation != password:
            return apology("password must be the same", 400)
        elif not email or not test_email(email):
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
            return apology("novel already exists")

        return redirect("/profile")
    else:
        return render_template("create.html")


@app.route('/profile/<name>/add-chapter', methods=["GET", "POST"])
@login_required
def add_chapter(name):
    try:
        novel = get_novel_data(db, name=name, user_id=session["user_id"])[0]
        if request.method == "POST":
            chapter_num = request.form.get("chapter_num")
            title = request.form.get("title")
            content = request.form.get("content")

            if not chapter_num or not title or not content:
                return apology("provide data to all fields")

            try:
                chapter_num = int(chapter_num)
                db.execute("INSERT INTO chapters(content, title, chapter_num, novel_id) VALUES(?, ?, ?, ?)", content, title, chapter_num, novel["novel_id"])
                return redirect(f"/profile/{name}/update")
            except ValueError:
                return apology("provide a number or chapter already exist")
        else: 
            return render_template("add_chapter.html", name=name)
    except IndexError:
        return apology("access denied")

@app.route('/profile/')
@login_required
def profile():
    user = db.execute("SELECT * FROM users WHERE user_id = ?", session["user_id"])[0]
    return render_template("profile.html", user=user)

@app.route('/comments', methods=["GET", "POST"])
@login_required
def comment():

    if request.method == "POST":
        comment = request.form.get("comment")
        comment_type = request.form.get("type")
        id = request.form.get("id")
        date = datetime.today().strftime("%d %B %Y %H:%M")
        link = request.form.get("link")

        if comment and comment_type == "novel":
            db.execute("INSERT INTO comments(comment, novel_id, date, user_id) VALUES(?, ?, ?, ?)", comment, int(id), date, session["user_id"])
        elif comment and comment_type == "chapter":
            db.execute("INSERT INTO comments(comment, chapter_id, date, user_id) VALUES(?, ?, ?, ?)", comment, int(id), date, session["user_id"])
        
        return redirect(link)
            
    user = request.args.get("user")
    novel = request.args.get("novel")
    chapter = request.args.get("chapter")
    try:
        if user:
            return jsonify(db.execute("SELECT * FROM comments WHERE user_id = ?", int(user)))
        elif novel:
            return jsonify(db.execute("SELECT * FROM comments WHERE novel_id = ?", int(novel)))
        elif chapter:
            return jsonify(db.execute("SELECT * FROM comments WHERE chapter_id = ?", int(chapter)))
        return 
    except ValueError:
        return []

@app.route('/profile/novels')
@login_required
def user_novels():
    novels = get_novel_data(db, user_id=session["user_id"])
    return jsonify(novels)

@app.route('/profile/<name>/update', methods=["GET", "POST"])
@login_required
def update(name):
    try:
        novel = get_novel_data(db, name=name, user_id=session["user_id"])[0]
        
        if request.method == "POST":
            new_name = request.form.get("new_name")
            if new_name:
                db.execute("UPDATE novels SET name = ? WHERE name = ? AND user_id = ? AND novel_id = ?", new_name, name, session["user_id"], novel["novel_id"])
                return redirect("/profile")

            return apology("provide valid name")
        else:
            chapters = get_chapter_data(db, novel_id=novel["novel_id"])

            return render_template("update.html", chapters=chapters, novel=novel)
    except IndexError:
        return apology("access denied")

@app.route("/profile/<name>/update/chapter-<int:chapter_num>", methods=["GET", "POST"])
@login_required
def update_chapter(name, chapter_num):
    try:
        novel = get_novel_data(db, name=name, user_id=session["user_id"])[0]
        if request.method == "POST":
            title = request.form.get("title")
            new_chapter_num = request.form.get("chapter_num")
            content = request.form.get("content")

            if not title or not chapter_num or not content:
                return apology("provide info to all fields")

            try:
                db.execute("UPDATE chapters SET title = ?, chapter_num = ?, content = ? WHERE novel_id = ? AND chapter_num = ?", title, new_chapter_num, content, novel["novel_id"], chapter_num)

            except ValueError:
                return apology("chapter number already exists")
        else:
            chapter = get_chapter_data(db, chapter_num=chapter_num, novel_id=novel["novel_id"])[0]
            return render_template("update_chapter.html", chapter=chapter, name=name)
    except IndexError:
        return apology("access denied")

@app.route('/delete/<name>/<int:chapter_num>')
@login_required
def delete(name, chapter_num=0):
    try:
        novel = get_novel_data(db, name=name, user_id=session["user_id"])[0]
        if chapter_num > 0:
            db.execute("DELETE FROM chapters WHERE chapter_num = ? AND novel_id = ?", chapter_num, novel["novel_id"])

            return redirect(f"/profile/{name}/update")
        else:
            db.execute("DELETE FROM chapters WHERE novel_id = ?", novel["novel_id"])
            db.execute("DELETE FROM novels WHERE novel_id = ? AND name = ?", novel["novel_id"], name)

            return redirect("/profile")
    except IndexError:
        return apology("you have no access to this novel")
