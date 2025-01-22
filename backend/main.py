import os
from contextlib import asynccontextmanager
from fileinput import filename
from typing import List, Annotated, Optional
import shutil

from click import Tuple
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form, BackgroundTasks
from multipart import file_path
from pydantic import validator, field_validator

from backend.api.dependencies.db import DBSession_Depends
from backend.database import session_manager
from backend.settings import DB_CONFIG
from backend.crud.users import create_user, get_user, get_all_users


def get_application(settings_db: str, init_db: bool = True) -> FastAPI:
    if init_db:
        session_manager.init(settings_db)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if session_manager._engine is None:
                await session_manager.close()

    app = FastAPI(lifespan=lifespan)


    @app.post("/users")
    async def users(
            session: DBSession_Depends,
            name: str = Query(description="Your name for your future account", max_length=255, min_length=2),
            email: str = Query(description="Your email for your future account", max_length=255, min_length=6),
            password: str = Query(example="password", min_length=8, max_length=255)
    ):
        new_user = await create_user(session, name, email, password)

        return new_user

    class Session(BaseModel):
        id_ram: int = Field(ge=1)
        title_ram: str = Field(min_length=15)
        db_name: str

        @field_validator("db_name")
        def check_dbname(self, db_name):
            if db_name != "MySQL":
                raise HTTPException(status_code=404, detail="Wrong DB")

    @app.get("/users")
    async def users(session: Session):
        users = await get_all_users(session)
        if not users:
            return HTTPException(status_code=201, detail="None found")

        return users


    @app.get("/user")
    async def user(session: DBSession_Depends, id: int):
        user = await get_user(session, id)
        if not user:
            return HTTPException(status_code=404, detail="Not exits this user")

        return user


    @app.post("/upload_image")
    async def upload_image(file: UploadFile = File(...)):
        with open(f"app/temp/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"File upload": file.filename}


    @app.post("/create_post")
    async def create_post(
            description: Optional[str] = Form(""),
            images: List[UploadFile] = File(...)
    ):
        img_list = []
        for img in images:
            img_data = await img.read()

            img_list.append(
                {
                    "file_size":len(img_data),
                    "data": img_data.hex()
                }
            )

        return {"Status": 200, "Description": description, "Photos": img_list}

    @app.post("/photo")
    async def create_photo(photo: UploadFile = File()):
        os.makedirs("UPLOAD_FILES", exist_ok=True)

        file_path = os.path.join("UPLOAD_FILES", photo.filename)

        with open(file_path, "wb") as buffer:
            buffer.write(photo.file.read())

        return {"filename": photo.filename, "location": file_path}


    return app


#backend = get_application(DB_CONFIG)

# backend = FastAPI()
#
#
# @backend.post("/upload_image")
# async def upload_image(file: UploadFile = File(...)):
#     with open(f"backend/temp/jackharlow_ava.jpg", "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"File upload": file.filename}
#
#
# @backend.post("/create_post")
# async def create_post(
#         description: Optional[str] = Form(""),
#         images: List[UploadFile] = File(...)
# ):
#     img_list = []
#     for photo in images:
#         with open(f"UPLOAD_FILES/{photo.filename}", "wb") as buffer:
#
#             shutil.copyfileobj(photo.file, buffer)
#
#         img_list.append(
#             {
#                 "file_size": photo.size,
#                 "data": photo.headers
#             }
#         )
#
#     return {"Status": 200, "Description": description, "Photos": img_list}
#
#
# @backend.post("/photo")
# async def create_photo(photo: UploadFile = File()):
#     os.makedirs("UPLOAD2_FILES", exist_ok=True)
#
#     file_path = os.path.join("UPLOAD2_FILES", photo.filename)
#
#     with open(file_path, "wb") as buffer:
#         buffer.write(photo.file.read())
#
#     return {"filename": photo.filename, "location": file_path}
#
#
# MAX_FILE_SIZE = 10 * 1024 * 1024
# ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
#
#
# @backend.post("/upload-photo")
# async def upload_photo(file: UploadFile = File()):
#     if file.content_type not in ALLOWED_FILE_TYPES:
#         raise HTTPException(status_code=400, detail="Недопустимий формат файлу")
#
#     if file.file.__sizeof__() >MAX_FILE_SIZE:
#         raise HTTPException(status_code=413, detail="Файл занадто великий")
#
#     return {"filename": file.filename}
#
#
# from PIL import Image
# import io
#
#
# def resize_photo(image_data: bytes, max_size: tuple = (600.0, 800.0)):
#     with Image.open(io.BytesIO(image_data)) as img:
#         img.thumbnail(max_size)
#         img_byte_array = io.BytesIO()
#         img.save(img_byte_array, format=img.format)
#         return img_byte_array.getvalue()
#
#
# async def process_img(file_path: str, photo):
#     with open(file_path, "rb") as file:
#         resized_img = resize_photo(file.read())
#
#     with open(file_path, "wb") as buffer:
#         buffer.write(resized_img)
#
#
#
# @backend.post("/upload-photo2")
# async def upload_photo2(background_tasks: BackgroundTasks, file: UploadFile = File()):
#     if file.content_type not in ALLOWED_FILE_TYPES:
#         raise HTTPException(status_code=400, detail="Недопустимий формат файлу")
#
#     if file.file.__sizeof__() > MAX_FILE_SIZE:
#         raise HTTPException(status_code=413, detail="Файл занадто великий")
#
#
#     file_path = f"UPLOAD2_FILES/{file.filename}"
#     with open(file_path, "wb") as buffer:
#         buffer.write(file.file.read())
#
#     background_tasks.add_task(process_img, file_path, file)
#
#     return {"info": "Фотографія завантажена, розпочато обробку."}
#
#
# ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
# def validate_and_sanitize_image(file: UploadFile):
#     if file.content_type not in ALLOWED_IMAGE_TYPES:
#         raise HTTPException(status_code=400, detail="Недозволений формат файлу.")
#
#     try:
#         image = Image.open(file.file)
#         buffered = io.BytesIO()
#         image.save(buffered, format=image.format)
#         return buffered.getvalue()
#     except Exception:
#         raise HTTPException(status_code=400, detail="Неможливо обробити файл.")
#
#
# @backend.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     file_data = validate_and_sanitize_image(file)
#     return {"status": "Файл успішно завантажено"}


from fastapi import FastAPI, Query, Path
from pydantic import  BaseModel, Field

app = FastAPI()

class Book(BaseModel):
    id: int = Field(ge=5)
    title: str
    author: str
    isAvailable: bool
    tags: List[str]
    metadata: Optional[dict] = None

    @validator('author')
    def validate_author(cls, author):
        list_of_non_authors = ["Stepn", "Misha", "Vasa"] # список з неіснуючих авторів
        if author in list_of_non_authors:
            raise ValueError(f'your author not real')
        return author

    @validator('title')
    def title_validate(cls, title):
        if title[0] != title[0].upper():
            raise ValueError(f'First letter in title must be in upper case but got this {title[0]}')
        return title


@app.post("/book")
async def create_book(book: Book):
    return book


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    return {
        "id": book_id,
        "title": "Введення в алгоритми",
        "author": "Томас Кормен",
        "isAvailable": True,
        "tags": ["програмування", "алгоритми", "дані"],
        "metadata": {
            "publisher": "MIT Press",
            "publicationYear": 2009
        }
    }