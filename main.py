from fastapi import FastAPI
from pydantic import BaseModel
from routers.fornecedor import router as fornecedor_router

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


app = FastAPI()
app.include_router(fornecedor_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}