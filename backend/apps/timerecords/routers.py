from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .models import TimeRecordModel, UpdateTimeRecordModel

router = APIRouter()

@router.post("/", response_description="Add new timerecord")
async def create_timerecord(request: Request, timerecord: TimeRecordModel = Body(...)):
    document = jsonable_encoder(timerecord)
    new_document = await request.app.mongodb["timerecords"].insert_one(document)
    created_document = await request.app.mongodb["timerecords"].find_one(
        {"_id": new_document.inserted_id}
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_document)


@router.get("/", response_description="List all timerecords")
async def list_timerecords(request: Request):
    documents = []
    for document in await request.app.mongodb["timerecords"].find().to_list(length=100):
        documents.append(document)
    return documents


@router.get("/{id}", response_description="Get a single timerecord")
async def show_task(id: str, request: Request):
    if (document := await request.app.mongodb["timerecords"].find_one({"_id": id})) is not None:
        return document

    raise HTTPException(status_code=404, detail=f"Timerecord {id} not found")


@router.put("/{id}", response_description="Update a timerecord")
async def update_timerecord(id: str, request: Request, timerecord: UpdateTimeRecordModel = Body(...)):
    document = {k: v for k, v in timerecord.dict().items() if v is not None}

    if len(document) >= 1:
        update_result = await request.app.mongodb["timerecords"].update_one(
            {"_id": id}, {"$set": document}
        )

        if update_result.modified_count == 1:
            if (
                updated_document := await request.app.mongodb["timerecords"].find_one({"_id": id})
            ) is not None:
                return updated_document

    if (
        existing_document := await request.app.mongodb["timerecords"].find_one({"_id": id})
    ) is not None:
        return existing_document

    raise HTTPException(status_code=404, detail=f"Timerecord {id} not found")


@router.delete("/{id}", response_description="Delete timerecord")
async def delete_timerecord(id: str, request: Request):
    delete_result = await request.app.mongodb["timerecords"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Timerecord {id} not found")