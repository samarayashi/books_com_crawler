from fastapi import FastAPI
from .routers import books, admin
from .database import engine
from .models import Base

# 創建所有表格
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book Crawler API")

app.include_router(books.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Crawler API"} 