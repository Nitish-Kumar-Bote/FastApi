from fastapi import FastAPI, Form, Request
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List
import csv
import io
import os
from sqlalchemy.ext.declarative import declarative_base


print("Current working directory:", os.getcwd())

app = FastAPI()

# SQLite Database Configuration
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Define the Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("age", String),
)

# Create the database and tables
metadata.create_all(engine)


# Pydantic model for CSV data
class CSVData(BaseModel):
    content: List[List[str]]


# Jinja2 Templates Configuration
templates = Jinja2Templates(directory="templates")


# Process CSV file and save data to SQLite databases
@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = Form(...), name_col: str = Form(...),
                      age_col: str = Form(...)):
    try:
        content = await file.read()
        csv_data = read_csv(content.decode())
        print(csv_data)
        header_row = csv_data[0]
        name_index = header_row.index(name_col)
        age_index = header_row.index(age_col)
        # Extract name and age column
        names = [row[name_index] for row in csv_data[1:]]
        print(names)
        ages = [row[age_index] for row in csv_data[1:]]
        print(ages)

        # Save data to SQLite database
        db = SessionLocal()
        try:
            for name, age in zip(names, ages):
                db.execute(users.insert().values(name=name, age=age))
            db.commit()
        finally:
            db.close()

        return {"message": "Data uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}


# Home route to upload CSV file
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Process CSV file and save data to SQLite database
@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = Form(...), name_col: str = Form(...),
                      age_col: str = Form(...)):
    content = await file.read()
    csv_data = read_csv(content.decode())

    # Extract name and age columns
    names = [row[name_col] for row in csv_data[1:]]
    ages = [row[age_col] for row in csv_data[1:]]

    # Save data to SQLite database
    db = SessionLocal()
    try:
        for name, age in zip(names, ages):
            db.execute(users.insert().values(name=name, age=age))
        db.commit()
    finally:
        db.close()

    return {"message": "Data uploaded successfully"}


# Helper function to read CSV content
def read_csv(csv_content: str):
    csv_file = io.StringIO(csv_content)
    csv_reader = csv.reader(csv_file)
    return list(csv_reader)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)