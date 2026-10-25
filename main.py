from fastapi import FastAPI
from pydantic import BaseModel
from routers.fornecedor import router as fornecedor_router
from routers.categoria import router as categoria_router
from routers.produto import router as produto_router
from routers.estoque import router as estoque_router
from handlers import configurar_handlers

app = FastAPI()
app.include_router(fornecedor_router)
app.include_router(categoria_router)
app.include_router(produto_router)
app.include_router(estoque_router)
configurar_handlers(app)