import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.configuration.settings import config
from src.routes import healthchecker, user, photo, comment, cloudinary_func

app = FastAPI()

app.include_router(healthchecker.router)
app.include_router(user.router)
app.include_router(photo.router)
app.include_router(comment.router)
app.include_router(cloudinary_func.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=config.PORT,
        host=config.HOST,
        reload=config.RELOAD,
        log_level="info",
    )
