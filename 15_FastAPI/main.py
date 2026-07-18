from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World!"}


# Browser -> GET / ->Uvicorn -> FastAPI which function -> home() -> return {"message": "Hello World!"} -> Browser


# Path Parameters

@app.get("/student/{id}")
def get_student(id: int):
    return {"student_id": id}

# Browser -> GET /student/123 -> Uvicorn -> FastAPI which function -> get_student() -> return {"student_id": 123} -> Browser


#Query Parameters
@app.get("/products")
def get_products(category: str):
    return {"category": category}

# Browser -> GET /products?category=electronics -> Uvicorn -> FastAPI which function -> get_products() -> return {"category": "electronics"} -> Browser

from pydantic import BaseModel

class Employee(BaseModel):
    name:str
    age:int
    salary:int

@app.post("/employee")
def create_employee(emp:Employee):
    return emp