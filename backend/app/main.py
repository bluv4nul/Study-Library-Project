import os
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "electrolibrary")

client: MongoClient = MongoClient(MONGO_URI)
db = client[DB_NAME]

app = FastAPI(title="Study Library API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

collections = {
    "authors": db["authors"],
    "genres": db["genres"],
    "publishers": db["publishers"],
    "books": db["books"],
}

entity_schemas = {
    "authors": {
        "name": "author",
        "required": ["author_name"],
        "fields": ["author_name", "author_nickname", "email", "social_media_link"],
        "search_fields": ["author_name", "author_nickname", "email"],
        "sort_fields": ["author_name", "email"],
    },
    "genres": {
        "name": "genre",
        "required": ["genre_name"],
        "fields": ["genre_name"],
        "search_fields": ["genre_name"],
        "sort_fields": ["genre_name"],
    },
    "publishers": {
        "name": "publisher",
        "required": ["publisher_name"],
        "fields": ["publisher_name", "publisher_city", "email", "publisher_website"],
        "search_fields": ["publisher_name", "publisher_city", "email"],
        "sort_fields": ["publisher_name", "publisher_city", "email"],
    },
}


def serialize(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def parse_object_id(value: str, field_name: str = "id") -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")
    return ObjectId(value)


def pagination(page: int, limit: int) -> tuple[int, int, int]:
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    return page, limit, (page - 1) * limit


def pick_allowed(payload: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: payload[field] for field in fields if field in payload}


def require_fields(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field for field in fields if payload.get(field) in (None, "")]
    if missing:
        raise HTTPException(status_code=400, detail={"message": "Required fields are missing", "missing": missing})


def build_sort(sort: str | None, order: str | None, allowed_fields: list[str], default_field: str) -> list[tuple[str, int]]:
    sort_field = sort if sort in allowed_fields else default_field
    direction = -1 if order == "desc" else 1
    return [(sort_field, direction)]


def build_entity_filter(q: str | None, search_fields: list[str]) -> dict[str, Any]:
    if not q:
        return {}
    return {"$or": [{field: {"$regex": q, "$options": "i"}} for field in search_fields]}


def normalize_book_payload(payload: dict[str, Any], partial: bool = False) -> dict[str, Any]:
    if not partial:
        require_fields(payload, ["title", "year", "isbn", "publisher_id", "author_ids", "genre_ids"])

    book = pick_allowed(payload, ["title", "isbn"])

    if "year" in payload:
        try:
            year = int(payload["year"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Year must be an integer")
        if year < 0:
            raise HTTPException(status_code=400, detail="Year must be a positive integer")
        book["year"] = year

    if "publisher_id" in payload:
        book["publisher_id"] = parse_object_id(payload["publisher_id"], "publisher_id")

    if "author_ids" in payload:
        if not isinstance(payload["author_ids"], list):
            raise HTTPException(status_code=400, detail="author_ids must be an array")
        book["author_ids"] = [parse_object_id(item, "author_id") for item in payload["author_ids"]]

    if "genre_ids" in payload:
        if not isinstance(payload["genre_ids"], list):
            raise HTTPException(status_code=400, detail="genre_ids must be an array")
        book["genre_ids"] = [parse_object_id(item, "genre_id") for item in payload["genre_ids"]]

    return book


def ensure_references(book: dict[str, Any]) -> None:
    publisher_id = book.get("publisher_id")
    author_ids = book.get("author_ids")
    genre_ids = book.get("genre_ids")

    if publisher_id and collections["publishers"].count_documents({"_id": publisher_id}) == 0:
        raise HTTPException(status_code=400, detail="Publisher does not exist")

    if author_ids and collections["authors"].count_documents({"_id": {"$in": author_ids}}) != len(author_ids):
        raise HTTPException(status_code=400, detail="One or more authors do not exist")

    if genre_ids and collections["genres"].count_documents({"_id": {"$in": genre_ids}}) != len(genre_ids):
        raise HTTPException(status_code=400, detail="One or more genres do not exist")


def books_lookup_pipeline(extra_stages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        *extra_stages,
        {"$lookup": {"from": "authors", "localField": "author_ids", "foreignField": "_id", "as": "authors"}},
        {"$lookup": {"from": "genres", "localField": "genre_ids", "foreignField": "_id", "as": "genres"}},
        {"$lookup": {"from": "publishers", "localField": "publisher_id", "foreignField": "_id", "as": "publisher"}},
        {"$unwind": {"path": "$publisher", "preserveNullAndEmptyArrays": True}},
    ]


def build_book_filter(
    search: str | None,
    year: int | None,
    year_from: int | None,
    year_to: int | None,
    publisher_id: str | None,
    author_id: str | None,
    genre_id: str | None,
) -> dict[str, Any]:
    query: dict[str, Any] = {}

    if search:
        query["title"] = {"$regex": search, "$options": "i"}

    if year is not None:
        query["year"] = year
    elif year_from is not None or year_to is not None:
        query["year"] = {}
        if year_from is not None:
            query["year"]["$gte"] = year_from
        if year_to is not None:
            query["year"]["$lte"] = year_to

    if publisher_id:
        query["publisher_id"] = parse_object_id(publisher_id, "publisher_id")
    if author_id:
        query["author_ids"] = parse_object_id(author_id, "author_id")
    if genre_id:
        query["genre_ids"] = parse_object_id(genre_id, "genre_id")

    return query


@app.exception_handler(DuplicateKeyError)
async def duplicate_key_handler(_request: Request, error: DuplicateKeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Document with unique field already exists", "error": str(error.details)},
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": DB_NAME}


@app.get("/api/books")
def list_books(
    search: str | None = None,
    year: int | None = None,
    yearFrom: int | None = None,
    yearTo: int | None = None,
    publisher_id: str | None = None,
    author_id: str | None = None,
    genre_id: str | None = None,
    sort: str | None = None,
    order: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    page, limit, skip = pagination(page, limit)
    book_filter = build_book_filter(search, year, yearFrom, yearTo, publisher_id, author_id, genre_id)
    sort_stage = dict(build_sort(sort, order, ["title", "year", "isbn"], "title"))

    items = list(
        collections["books"].aggregate(
            books_lookup_pipeline(
                [{"$match": book_filter}, {"$sort": sort_stage}, {"$skip": skip}, {"$limit": limit}]
            )
        )
    )
    total = collections["books"].count_documents(book_filter)

    return serialize({"data": items, "meta": {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}})


@app.get("/api/books/{book_id}")
def get_book(book_id: str) -> dict[str, Any]:
    book_object_id = parse_object_id(book_id)
    books = list(collections["books"].aggregate(books_lookup_pipeline([{"$match": {"_id": book_object_id}}])))

    if not books:
        raise HTTPException(status_code=404, detail="Book not found")

    return serialize(books[0])


@app.post("/api/books", status_code=status.HTTP_201_CREATED)
def create_book(payload: dict[str, Any]) -> dict[str, Any]:
    book = normalize_book_payload(payload)
    ensure_references(book)

    result = collections["books"].insert_one(book)
    return get_book(str(result.inserted_id))


@app.patch("/api/books/{book_id}")
def update_book(book_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    book_object_id = parse_object_id(book_id)
    book = normalize_book_payload(payload, partial=True)

    if not book:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    ensure_references(book)
    result = collections["books"].update_one({"_id": book_object_id}, {"$set": book})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")

    return get_book(book_id)


@app.put("/api/books/{book_id}")
def replace_book(book_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    book_object_id = parse_object_id(book_id)
    book = normalize_book_payload(payload)
    ensure_references(book)

    result = collections["books"].replace_one({"_id": book_object_id}, book)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")

    return get_book(book_id)


@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str) -> Response:
    result = collections["books"].delete_one({"_id": parse_object_id(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def register_entity_routes(collection_name: str, schema: dict[str, Any]) -> None:
    collection = collections[collection_name]
    route_prefix = f"/api/{collection_name}"

    @app.get(route_prefix)
    def list_entities(
        q: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
    ) -> dict[str, Any]:
        page, limit, skip = pagination(page, limit)
        query = build_entity_filter(q, schema["search_fields"])
        items = list(collection.find(query).sort(build_sort(sort, order, schema["sort_fields"], schema["sort_fields"][0])).skip(skip).limit(limit))
        total = collection.count_documents(query)

        return serialize({"data": items, "meta": {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}})

    @app.get(f"{route_prefix}/{{item_id}}")
    def get_entity(item_id: str) -> dict[str, Any]:
        item = collection.find_one({"_id": parse_object_id(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail=f"{schema['name']} not found")
        return serialize(item)

    @app.post(route_prefix, status_code=status.HTTP_201_CREATED)
    def create_entity(payload: dict[str, Any]) -> dict[str, Any]:
        item = pick_allowed(payload, schema["fields"])
        require_fields(item, schema["required"])

        result = collection.insert_one(item)
        return serialize(collection.find_one({"_id": result.inserted_id}))

    @app.patch(f"{route_prefix}/{{item_id}}")
    def update_entity(item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        item_object_id = parse_object_id(item_id)
        item = pick_allowed(payload, schema["fields"])

        if not item:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        result = collection.update_one({"_id": item_object_id}, {"$set": item})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"{schema['name']} not found")

        return serialize(collection.find_one({"_id": item_object_id}))

    @app.put(f"{route_prefix}/{{item_id}}")
    def replace_entity(item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        item_object_id = parse_object_id(item_id)
        item = pick_allowed(payload, schema["fields"])
        require_fields(item, schema["required"])

        result = collection.replace_one({"_id": item_object_id}, item)
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"{schema['name']} not found")

        return serialize(collection.find_one({"_id": item_object_id}))

    @app.delete(f"{route_prefix}/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_entity(item_id: str) -> Response:
        result = collection.delete_one({"_id": parse_object_id(item_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"{schema['name']} not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)


for name, entity_schema in entity_schemas.items():
    register_entity_routes(name, entity_schema)
