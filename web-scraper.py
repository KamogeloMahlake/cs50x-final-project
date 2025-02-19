import requests
from bs4 import BeautifulSoup
from datetime import datetime
from cs50 import SQL
from werkzeug.security import generate_password_hash

keyword = input("Search: ").replace(" ", "+")

db = SQL("sqlite:///databases/database1.db")

r = requests.get(f"https://novelbin.me/search?keyword={keyword}")

links = BeautifulSoup(r.text, "html.parser").find_all("h3", class_="novel-title")

i = 0
array = []
for link in links:
    array.append(str(link.find("a")["href"]))
    print(f"{i}. {link.find('a').getText()}")
    i += 1

answer = int(input("Number: "))

soup = BeautifulSoup(requests.get(array[answer]).text, "html.parser")
name = soup.find("h3", itemprop="name").getText()
img = soup.find("img", class_="lazy")["data-src"]
author = "Admin"  # soup.find('ul', class_="info info-meta").getText().split(" ")[0].split("\n")[3]
about = soup.find("div", class_="desc-text")

try:
    user_id = db.execute(
        "INSERT INTO users(username, password, date) VALUES(?, ?, ?)",
        author,
        generate_password_hash("Shaunmah"),
        datetime.today().strftime("%d %B %Y %H:%M"),
    )

except ValueError:
    user_id = db.execute("SELECT user_id FROM users WHERE username = ?", author)[0][
        "user_id"
    ]

try:
    novel_id = db.execute(
        "INSERT INTO novels(name, image, about, user_id) VALUES(?, ?, ?, ?)",
        name,
        img,
        str(about),
        user_id,
    )
except ValueError:
    novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ? ", name)[0][
        "novel_id"
    ]

next_chapter = soup.find(title="READ NOW", href=True)
chapter_num = 0

while next_chapter["href"] is not None:
    try:
        page = requests.get(next_chapter["href"])
    except Exception:
        print("done")
        break
    soup = BeautifulSoup(page.text, "html.parser")

    content = soup.find("div", id="chr-content")
    try:
        title = soup.find("a", class_="chr-title")["title"]
    except TypeError:
        title = soup.find("h2").getText()

    print(title)
    chapter_num += 1

    if content and title and chapter_num and novel_id:
        try:
            print(
                db.execute(
                    "INSERT INTO chapters(content, title, novel_id, chapter_num) VALUES(?, ?, ?, ?)",
                    content.prettify(),
                    title,
                    novel_id,
                    chapter_num,
                )
            )
        # print(soup.find('div', class_='chr-c'))
        except Exception:
            pass

    next_chapter = soup.find("a", id="next_chap")
