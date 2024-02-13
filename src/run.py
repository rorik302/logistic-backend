from src.core.config import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.core.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.env.RELOAD,
        ssl_keyfile=settings.security.SSL_KEYFILE,
        ssl_certfile=settings.security.SSL_CERTFILE,
    )
