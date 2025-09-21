from fastapi import FastAPI
from .routers import users, login
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000"
    ]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["*"] for all (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# inclui routers
app.include_router(users.router)
app.include_router(login.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}