import os
import re
from pathlib import Path

from fastapi import FastAPI, Response, Form, Depends
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

print(db_path := os.getenv("SQLALCHEMY_DATABASE_URL"))
engine = create_engine(db_path)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
metadata = Base.metadata


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String)
    password = Column(String)


class Goose(Base):
    __tablename__ = "geese"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    geese_string = Column(String)


class Amogus(Base):
    __tablename__ = "amoguses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amoguses_string = Column(String)


class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    animes_string = Column(String)


class Meme(Base):
    __tablename__ = "memes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    memes_string = Column(String)


class Card:
    def __init__(self, text_list: list[str], start: int, end: int):
        self.text = "\n".join(text_list)
        self.id_start = start
        self.id_end = end


def fill_tables():
    db = SessionLocal()

    with open("static/txt/memes.txt", "r") as memes_txt:
        memes = memes_txt.readlines()
        for meme in memes:
            mem = Meme(memes_string=meme)
            db.add(mem)
            db.commit()
            db.refresh(mem)

    with open("static/txt/amoguses.txt", "r") as amoguses_txt:
        amoguses = amoguses_txt.readlines()
        for amogus_line in amoguses:
            sus = Amogus(amoguses_string=amogus_line)
            db.add(sus)
            db.commit()
            db.refresh(sus)

    with open("static/txt/animes.txt", "r") as animes_txt:
        animes = animes_txt.readlines()
        for anime_line in animes:
            anim = Anime(animes_string=anime_line)
            db.add(anim)
            db.commit()
            db.refresh(anim)

    with open("static/txt/geese.txt", "r") as geese_txt:
        geese = geese_txt.readlines()
        for goose in geese:
            gos = Goose(geese_string=goose)
            db.add(gos)
            db.commit()
            db.refresh(gos)

    with open("static/txt/users.txt", "r") as users_txt:
        users = users_txt.readlines()
        for user in users:
            splitted_user = user.split(" | ")
            user_db = Users(login=splitted_user[0], password=splitted_user[-1])
            db.add(user_db)
            db.commit()
            db.refresh(user_db)

    db.close()


metadata.drop_all(bind=engine)
metadata.create_all(bind=engine)
fill_tables()


@app.get("/")
async def root(request: Request, response: Response, db: Session = Depends(get_db)):
    table_info = None
    cookies = request.cookies
    response = templates.TemplateResponse(
        "Task8.html", {
            "response": response,
            "request": request,
            "info": None
        }
    )
    if "logged" not in cookies.keys() or "table" not in cookies.keys() or "offset" not in cookies.keys():
        response.set_cookie(key="logged", value="Nothing", httponly=True)
        response.set_cookie(key="table", value="Nothing", httponly=True)
        response.set_cookie(key="offset", value="0", httponly=True)
    else:
        match (cookies["logged"], cookies["table"]):
            case (_, "users"):
                table_info = [f"{user.login}  {user.password}" for user in db.query(Users).all()]
            case ("logged_anime", "animes"):
                table_info = [anime.animes_string for anime in db.query(Anime).all()]
            case ("logged_amogus", "amoguses"):
                table_info = [amogus.amoguses_string for amogus in db.query(Amogus).all()]
            case ("logged_goose", "geese"):
                table_info = [goose.geese_string for goose in db.query(Goose).all()]
            case ("logged_meme", "memes"):
                table_info = [meme.memes_string for meme in db.query(Meme).all()]
            case (_, _):
                table_info = None
    if table_info:
        offset = cookies["offset"]
        if offset == "-1":
            table_info = [table_info[int(offset)]]
        else:
            offset = int(re.sub(r"[^\d.]+", "", cookies["offset"]))
            table_info = table_info[offset:offset + 20]
        return templates.TemplateResponse(
            "Task8.html", {
                "response": response,
                "request": request,
                "info": table_info
            }
        )
    else:
        return response


@app.post('/run_query')
async def run_query(sql: str = Form()):
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    query = sql.split()
    if "SELECT" in query and "*" in query and "FROM" in query and 4 <= len(query) <= 8:
        response.set_cookie(key="table", value=query[3].lower(), httponly=True)
        if "WHERE" in query and ("id" in query or "string.id" in query) and \
                (">" in query or "=" in query) and len(query) == 8:
            if ">" in query and "=" not in query:
                response.set_cookie(key="offset", value=query[-1], httponly=True)
            elif "=" in query and ">" not in query:
                response.set_cookie(key="offset", value="-1", httponly=True)
            else:
                response.set_cookie(key="offset", value=query[-1], httponly=True)
        else:
            response.set_cookie(key="offset", value="0", httponly=True)
    return response


@app.post('/submit_form')
async def submit_form(login: str = Form(), password: str = Form()):
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    if login == "anime_enjoyer" and password == "FlydayChinatown":
        response.set_cookie(key="logged", value="logged_anime", httponly=True)
    elif login == "meme_lover" and password == "I_LOVE_MEMES":
        response.set_cookie(key="logged", value="logged_meme", httponly=True)
    elif login == "AMOGUS" and password == "SUS":
        response.set_cookie(key="logged", value="logged_amogus", httponly=True)
    elif login == "geese_genius" and password == "hard_worker":
        response.set_cookie(key="logged", value="logged_goose", httponly=True)
    else:
        response.set_cookie(key="logged", value="Nothing", httponly=True)

    return response
