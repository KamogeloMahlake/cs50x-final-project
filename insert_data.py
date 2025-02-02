from cs50 import SQL
from os import listdir
import json
import re

filelist = listdir('./json_file')
db = SQL("sqlite:///novels.db")
for i in filelist:
    with open('./json_file/' + i, 'r') as file:
        reader = json.load(file)

        for row in reader:
            
            if row["content"] and row["user"] == "7530804":
                title_array = re.findall('(\d+|\D+)', row["title"])

                try:
                    chapter_num = int(title_array[-1])
                    title =  title_array[0].replace(": Chapter", "").rstrip().lstrip() #+ title_array[1] if len(title_array) > 3 else title_array[0]
                    author = "dirkgrey"

                    if title[-1] == "-":
                        title = title.replace("-", "")
                    if "Epilogue" in row["title"]:
                        if "Gamer" in row["title"]:
                            title = "A Gamer Adventure"
                            chapter_num = 327
                        else:
                            title = "Dark Lord ind Chains"
                            chapter_num = 131
                    elif "-" in title:
                        continue

                    novel_id = ""
                    try:
                        novel_id = (db.execute("INSERT INTO novels(name, author) VALUES(?, ?)", title, author))
                    except ValueError:
                        novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ?", title)[0]["novel_id"]
                        
                    
                    try:
                        db.execute("INSERT INTO chapters(content, novel_id, chapter_num) VALUES(?, ?, ?)", row["content"], novel_id, chapter_num)
                    except ValueError:
                        pass
                    
                except ValueError:
                    if "Epilogue" in row["title"]:
                        if "Gamer" in row["title"]:
                            title = "A Gamer Adventure"
                            chapter_num = 328
                            author = "dirkgrey"
                            try:
                                novel_id = (db.execute("INSERT INTO novels(name, author) VALUES(?, ?)", title, author))
                            except ValueError:
                                novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ?", title)[0]["novel_id"]
                                
                            
                            try:
                                db.execute("INSERT INTO chapters(content, novel_id, chapter_num) VALUES(?, ?, ?)", row["content"], novel_id, chapter_num)
                            except ValueError:
                                pass
                    continue
            
            elif row["user"] == "122944537":
                title_array = row["title"].split(":")
                chapter_num = 0
                name = title_array[0]
                author = "crossedge"
                title = ""
                novel_id = 0
                try:
                    _, chapter_num = title_array[1].strip().split(" ")
                    chapter_num = int(chapter_num)

                    if len(title_array) == 2:
                        title = title_array[1]
                    else:
                        title = title_array[1] + title_array[2]
                except ValueError:
                    chapter_num = 27
                    title = "Chapter 27: Project Regicide (Part - 2)"

                
                try:
                    novel_id = (db.execute("INSERT INTO novels(name, author) VALUES(?, ?)", name, author))
                except ValueError:
                    novel_id = db.execute("SELECT novel_id FROM novels WHERE name = ?", name)[0]["novel_id"]
                                            
                try:
                    db.execute("INSERT INTO chapters(content, novel_id, chapter_num, title) VALUES(?, ?, ?, ?)", row["content"], novel_id, chapter_num, title)
                except ValueError:
                    pass