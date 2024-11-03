from fastapi import FastAPI
from .routers import books
from .database import engine
from .models import book

book.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Crawler API")

app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Crawler API"} 