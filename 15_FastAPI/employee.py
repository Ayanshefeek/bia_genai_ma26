from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

employees = []

class Employee(BaseModel):
    id: int
    name: str
    age: int
    salary: int

@app.post("/employee")
def create_employee(emp: Employee):
    employees.append(emp)
    return {
        "message": "Employee added",
        "employee" : emp
    }

@app.get("/employees")
def get_employees():
    return employees

@app.get("/employee/{id}")
def get_employee(id: int):
    for emp in employees:
        if emp.id == id:
            return emp
    return {"message": "Employee not found"}


@app.delete("/employee/{id}")
def delete_employee(id: int):
    for emp in employees:
        if emp.id == id:
            employees.remove(emp)
            return {"message": "Employee deleted"}
    return {"message": "Employee not found"}

@app.put("/employee/{id}")
def update_employee(id: int, updated_emp:   Employee):
    for emp in employees:
        if emp.id == id:
            emp.name = updated_emp.name
            emp.age = updated_emp.age
            emp.salary = updated_emp.salary
            return {"message": "Employee updated", "employee": emp}
    return {"message": "Employee not found"}