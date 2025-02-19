from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column 

class Base(DeclarativeBase):
    pass

class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String(50))
    chapter_num: Mapped[int] = mapped_column(Integer)
    novel_id: Mapped[int] = mapped_column(Integer)

class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column(Text)
    chapter_id: Mapped[int] = mapped_column(Integer)



"""
db = SQL("sqlite:///copy.db")
novels = get_novel_data(db)

for novel in novels:
    engine = create_engine(f"sqlite:///databases/{novel['name'].replace(' ', '_')}.db", echo=True)

    Base.metadata.create_all(engine)

    chapters = get_chapter_data(db, novel_id=novel["novel_id"])
    with Session(engine) as s:
        for chapter in chapters:
            page = Page(content=str(chapter["content"]), title=chapter["title"], chapter_num=chapter["chapter_num"], novel_id=novel["novel_id"])
            s.add(page)
        s.commit()
"""
