from fastapi import FastAPI, Request,Form,Response
from fastapi.responses import HTMLResponse,RedirectResponse,FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Sequence, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session


app=FastAPI()
templates=Jinja2Templates(directory="./")

Base = declarative_base()

# db모델 만들기
class Post(Base):
    __tablename__ = 'new_blog_post'
    id = Column(Integer, Sequence('post_id_seq'), primary_key=True)
    title = Column(String(100))
    content = Column(String(100))

# 데이터베이스 만들기
DATABASE_URL = "sqlite:///./test.db"  # SQLite 또는 Mysql,MariaDB등 사용가능
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)



# create
@app.post("/posts")
def create_blog_post(request: Request, response: Response,title: str = Form(...), content: str = Form(...)):
    new_blog_post = Post(title=title, content=content)
    session = SessionLocal()
    session.add(new_blog_post)
    session.commit()
    session.refresh(new_blog_post)

    tmp=session.query(Post).all()
    # RedirectResponse를 강제로 응답상태로 만들어야 가능하다
    return RedirectResponse(url="/home",status_code=302)


# read
@app.get("/home")
async def read_posts(request: Request):
    db = SessionLocal()
    posts = db.query(Post).all()
    return templates.TemplateResponse("new_post.html", context={"request":request,"posts": posts})

# update
@app.get("/edit/{post_id}")
async def edit_get(request: Request,post_id: int):
    db=SessionLocal()
    row=db.query(Post).get(post_id)
    return templates.TemplateResponse("edit.html", context={"request":request,"row":row})
@app.post("/update")
async def edit_post(request: Request, response: Response,title: str = Form(...), content: str = Form(...), id:int=Form(...)):
    db=SessionLocal()
    row=db.query(Post).get(id)
    row.title=title
    row.content=content
    db.commit()
    return RedirectResponse(url="/home",status_code=302)

# delete
@app.get("/delete/{post_id}")
async def delete_post(post_id: int):
    db=SessionLocal()
    row=db.query(Post).get(post_id)
    db.delete(row)
    db.commit()
    return RedirectResponse(url="/home",status_code=302)