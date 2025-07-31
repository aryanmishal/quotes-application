from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import quotes, auth
from app.database import db

app = FastAPI(title="Quotes API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(quotes.router)

@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_database_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to the Quotes API"}
