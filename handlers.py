import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


def configurar_handlers(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def tratar_http_exception(
        request: Request,
        exc: StarletteHTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "erro": {
                    "codigo": exc.status_code,
                    "mensagem": str(exc.detail),
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(
        request: Request,
        exc: RequestValidationError,
    ):
        detalhes = []

        for erro in exc.errors():
            detalhes.append({
                "campo": ".".join(map(str, erro["loc"])),
                "mensagem": erro["msg"],
            })

        return JSONResponse(
            status_code=422,
            content={
                "erro": {
                    "codigo": 422,
                    "mensagem": "Dados inválidos na requisição",
                    "detalhes": detalhes,
                }
            },
        )

    @app.exception_handler(IntegrityError)
    async def tratar_integridade(
        request: Request,
        exc: IntegrityError,
    ):
        logger.warning(
            "Violação de integridade em %s %s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=409,
            content={
                "erro": {
                    "codigo": 409,
                    "mensagem": "Operação viola uma restrição do banco de dados",
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def tratar_banco(
        request: Request,
        exc: SQLAlchemyError,
    ):
        logger.exception("Erro de banco de dados")

        return JSONResponse(
            status_code=500,
            content={
                "erro": {
                    "codigo": 500,
                    "mensagem": "Erro interno ao acessar o banco de dados",
                }
            },
        )

    @app.exception_handler(Exception)
    async def tratar_erro_inesperado(
        request: Request,
        exc: Exception,
    ):
        logger.exception("Erro inesperado na API")

        return JSONResponse(
            status_code=500,
            content={
                "erro": {
                    "codigo": 500,
                    "mensagem": "Erro interno do servidor",
                }
            },
        )