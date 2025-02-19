import os
from sqlalchemy import create_engine
from flask import redirect, render_template, request, session, jsonify, flash
from sqlalchemy.orm import Session
from helpers import (
    apology,
    get_novel_data,
    login_required,
    get_chapter_data,
    test_email,
    test_password,
    string_to_html,
    allowed_file,
)   
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from config import app, db
import os
from werkzeug.utils import secure_filename
from chapter import Base, Chapter
from cs50 import SQL

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    novels = get_novel_data(db)
    return render_template("index.html", novels=novels, x="Home")


@app.route("/novel/<name>")
def novel(name):
    try:
        novel = get_novel_data(db, name=name)[0]
        chapters = get_chapter_data(name, novel_id=novel["novel_id"])
        return render_template("novel.html", chapters=chapters, novel=novel)
    except Exception:
        return apology("novel does not exist", 404)

@app.route("/<name>/chapter-<int:num>")
def chapter(name, num):
    try:
        novel = get_novel_data(db, name=name)[0]
        chapter = get_chapter_data(name, novel_id=novel["novel_id"], chapter_num=num)

        previous = get_chapter_data(name, novel_id=novel["novel_id"], chapter_num=(num - 1))
        next_chapter = get_chapter_data(name, novel_id=novel["novel_id"], chapter_num=num + 1)

        return render_template(
            "chapter.html",
            chapter=chapter[0],
            name=name,
            previous=previous,
            next_chapter=next_chapter,
        )
    except Exception as e:
        return apology(f"chapter does not exist, {e}", 404)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        q = request.form.get("q")
        novels = db.execute(
            "SELECT * FROM novels WHERE name LIKE ? ORDER BY name", "%" + q + "%"
        )

        if novels:
            return render_template("index.html", novels=novels, x="Search")

        return apology("novel not found", 404)
    q = request.args.get("q")
    novels = db.execute(
        "SELECT * FROM novels WHERE name LIKE ? ORDER BY name", "%" + q + "%"
    )
    return jsonify(novels)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        row = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(row) != 1 or not check_password_hash(
            row[0]["password"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        session["user_id"] = row[0]["user_id"]
        return redirect("/")

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
            return apology("must provide username", 403)
        elif not password or not test_password(password):
            return apology(
                "must contain uppercase and lowercase, digits, special character and have a minimum length of 8",
                403,
            )
        elif not confirmation or confirmation != password:
            return apology("password must be the same", 403)
        elif not email or not test_email(email):
            return apology("provide vaild email", 403)
        try:
            session["user_id"] = db.execute("INSERT INTO users(username, password, email, date) VALUES(?, ?, ?, ?)",
                username,
                generate_password_hash(password),
                email,
                datetime.today().strftime("%d %B %Y %H:%M")
            )
        except Exception:
            return apology(f"user already exists, try login", 403)

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        novel_name = request.form.get("name")
        about = request.form.get("about")
        image = request.form.get("image")
        try:
            if about and novel_name:
                db.execute("INSERT INTO novels(name, user_id, about, image) VALUES(?, ?, ?, ?)", novel_name, session["user_id"], string_to_html(about), image)
                engine = create_engine(f"sqlite:///databases/{novel_name.replace(' ', '_')}.db", echo=True)
                Base.metadata.create_all(engine)
            else:
                return apology("missing fields")
        except ValueError:
            return apology("novel already exists")

        return redirect("/profile")
    else:
        print("debug")
        return render_template("create.html")


@app.route("/profile/<name>/add-chapter", methods=["GET", "POST"])
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
                engine = create_engine(f"sqlite:///databases/{name.replace(' ', '_')}.db")

                with Session(engine) as s:
                    chapter = Chapter(
                        content=string_to_html(content),
                        title=title,
                        chapter_num=chapter_num,
                        novel_id=novel["novel_id"]
                    )
                    s.add(chapter)
                    s.commit()

                return redirect(f"/profile/{name}/update")
            except Exception:
                return apology("provide a number or chapter already exist", 403)
        else:
            return render_template("add_chapter.html", name=name)
    except IndexError:
        return apology("access denied", 403)


@app.route("/profile/")
@login_required
def profile():
    try:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", session["user_id"])[0]
        return render_template("profile.html", user=user)
    except Exception:
        return apology(f"invalid user", 403)

@app.route("/comments", methods=["GET", "POST"])
@login_required
def comment():

    if request.method == "POST":
        comment = request.form.get("comment")
        comment_type = request.form.get("type")
        id = request.form.get("id")
        date = datetime.today().strftime("%d %B %Y %H:%M")
        link = request.form.get("link")
        try:

            if comment and comment_type == "novel":
                db.execute("INSERT INTO comments(comment, novel_id, user_id, date) VALUES(?, ?, ?, ?)",
                    string_to_html(comment),
                    int(id),
                    session["user_id"],
                    date
                )
        except Exception:
            flash("unable to create comment")

        return redirect(link)

    user = request.args.get("user")
    novel = request.args.get("novel")
    try:
        data = []
        if user:
            data = db.execute("SELECT * FROM comments WHERE user_id = ?", session["user_id"])
        elif novel:
            data = db.execute("SELECT * FROM comments WHERE novel_id = ?", int(novel))
        
        for i in data:
            i["username"] = db.execute("SELECT username FROM users WHERE user_id = ?", i["user_id"])[0]["username"]

        return data
    except ValueError:
        return []


@app.route("/profile/novels")
@login_required
def user_novels():
    try:
        novels = get_novel_data(db, user_id=session["user_id"])
        return jsonify(novels)
    except Exception as e:
        return {"error": e}

@app.route("/profile/<name>/update", methods=["GET", "POST"])
@login_required
def update(name):
    try:
        novel = db.execute("SELECT * FROM novels WHERE name = ? AND user_id = ?", name, session["user_id"])[0]
        if request.method == "POST":
            new_name = request.form.get("new_name")
            if new_name:
                db.execute(
                    "UPDATE novels SET name = ? WHERE name = ? AND user_id = ? AND novel_id = ?",
                    new_name,
                    name,
                    session["user_id"],
                    novel["novel_id"],
                )

                return redirect("/profile")

            return apology("provide valid name", 403)
        else:
            chapters = get_chapter_data(name, novel_id=novel["novel_id"])

            return render_template("update.html", chapters=chapters, novel=novel)
    except IndexError:
        return apology("access denied")


@app.route("/profile/<name>/update/chapter-<int:chapter_num>", methods=["GET", "POST"])
@login_required
def update_chapter(name, chapter_num):
    try:
        novel = db.execute("SELECT * FROM novels WHERE name = ? AND user_id = ?", name, session["user_id"])[0]
        if request.method == "POST":
            title = request.form.get("title")
            new_chapter_num = request.form.get("chapter_num")
            content = request.form.get("content")

            if not title or not chapter_num or not content:
                return apology("provide info to all fields")

            try:
                database = SQL(f"sqlite:///databases/{name.replace(' ', '_')}.db")

                database.execute(
                    "UPDATE chapters SET title = ?, chapter_num = ?, content = ? WHERE novel_id = ? AND chapter_num = ?",
                    title,
                    new_chapter_num,
                    string_to_html(content),
                    novel["user_id"],
                    chapter_num,
                )

            except Exception as e:
                return apology(f"{e}", 403)
            return redirect(f"profile/{name}/update")
        else:
            chapter = get_chapter_data(name, novel_id=novel["user_id"], chapter_num=chapter_num)
            print(chapter)
    
            return render_template("update_chapter.html", chapter=chapter, name=name)
    except IndexError:
        return apology("access denied", 403)


@app.route("/delete/<name>/<int:chapter_num>")
@login_required
def delete(name, chapter_num=0):
    try:
        filename = name.replace(' ', '_')
        database = SQL(f"sqlite:///databases/{filename}.db")
        novel = db.execute("SELECT * FROM novels WHERE name = ? AND user_id = ?", name, session["user_id"])[0]
        if chapter_num > 0:
            database.execute(
                "DELETE FROM chapters WHERE chapter_num = ? AND novel_id = ?",
                chapter_num,
                novel["novel_id"]
            )

            return redirect(f"/profile/{name}/update")
        else:
            if os.path.isfile(f"/databases/{filename}.db"):
                os.remove(f"/databases/{filename}.db")
            db.execute("DELETE FROM novels WHERE name = ? AND user_id = ?", name, session["user_id"])
            return redirect("/profile")
    except IndexError:
        return apology("you have no access to this novel")


if __name__ == "__main__":
    app.run(debug=True)
