from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import routes as app_routes
import uvicorn

app = FastAPI(
    title="Question Gen API", 
    description="API for exam questions",
    version="1.0.0"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Question Gen API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

app.include_router(app_routes.router, prefix="/questions", tags=["api"])