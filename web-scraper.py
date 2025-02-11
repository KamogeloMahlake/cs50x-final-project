import requests
from bs4 import BeautifulSoup
from datetime import datetime
from cs50 import SQL
from werkzeug.security import generate_password_hash

db = SQL("sqlite:///database.db")

url =  'https://novelbin.com/b/the-legendary-mechanic'
r = requests.get(url)

soup = BeautifulSoup(r.text, 'html.parser')
name = soup.find('h3', itemprop="name").getText()
img = soup.find('img', class_="lazy")["data-src"]
author =  'Chocolion'#soup.find('ul', class_="info info-meta").getText().split(" ")[0].split("\n")[3]
about = soup.find('div', class_="desc-text")

try:
    user_id = db.execute("INSERT INTO users(username, password, date) VALUES(?, ?, ?)", author, generate_password_hash(author),datetime.today().strftime("%d %B %Y %H:%M"))

except ValueError:
    user_id = db.execute("SELECT user_id FROM users WHERE username = ?", author)[0]["user_id"]

try:
    novel_id = db.execute("INSERT INTO novels(name, image, about, user_id) VALUES(?, ?, ?, ?)", name, img, str(about), user_id)
except ValueError:
    novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ? ", name)[0]["novel_id"]

next_chapter = soup.find(title="READ NOW", href=True)
chapter_num = 0

while next_chapter is not None:
    page = requests.get(next_chapter['href'])
    soup = BeautifulSoup(page.text, 'html.parser')
    
    content = soup.find('div', id="chr-content")
    title = soup.find('a', class_="chr-title")['title']
    chapter_num += 1
    
    if content and title and chapter_num and novel_id:
        try:
            print(db.execute("INSERT INTO chapters(content, title, novel_id, chapter_num) VALUES(?, ?, ?, ?)", content.prettify(), title, novel_id, chapter_num))
   # print(soup.find('div', class_='chr-c'))
        except ValueError:
            pass
        
    next_chapter = soup.find('a', id='next_chap')

