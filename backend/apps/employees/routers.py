from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .models import EmployeeModel, UpdateEmployeeModel

router = APIRouter()

@router.post("/", response_description="Add new employee")
async def create_employee(request: Request, employee: EmployeeModel = Body(...)):
    document = jsonable_encoder(employee)
    new_document = await request.app.mongodb["employees"].insert_one(document)
    created_document = await request.app.mongodb["employees"].find_one(
        {"_id": new_document.inserted_id}
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_document)


@router.get("/", response_description="List all employees")
async def list_employees(request: Request):
    documents = []
    for document in await request.app.mongodb["employees"].find().to_list(length=100):
        documents.append(document)
    return documents


@router.get("/{id}", response_description="Get a single employee")
async def show_employee(id: str, request: Request):
    if (document := await request.app.mongodb["employees"].find_one({"_id": id})) is not None:
        return document

    raise HTTPException(status_code=404, detail=f"Employee {id} not found")


@router.put("/{id}", response_description="Update an employee")
async def update_employee(id: str, request: Request, employee: UpdateEmployeeModel = Body(...)):
    document = {k: v for k, v in employee.dict().items() if v is not None}

    if len(document) >= 1:
        update_result = await request.app.mongodb["employees"].update_one(
            {"_id": id}, {"$set": document}
        )

        if update_result.modified_count == 1:
            if (
                updated_document := await request.app.mongodb["employees"].find_one({"_id": id})
            ) is not None:
                return updated_document

    if (
        existing_document := await request.app.mongodb["employees"].find_one({"_id": id})
    ) is not None:
        return existing_document

    raise HTTPException(status_code=404, detail=f"Employee {id} not found")


@router.delete("/{id}", response_description="Delete employee")
async def delete_employee(id: str, request: Request):
    delete_result = await request.app.mongodb["employees"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Employee {id} not found")