from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient

from .routes import paper, projects, summary, chat
from .config import AppSettings, app_settings

app = FastAPI(
    title="Inquiro",
    description="Research Assistant API",
    version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup_db():
    settings = app_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.mongodb_client = app.mongodb_conn[settings.MONGO_DB]

@app.on_event("shutdown")
async def shutdown_db():
    app.mongodb_conn.close()
    app.vdb_client.disconnect()


#app.include_router(auth.router)
app.include_router(projects.projects_router, prefix="/projects", tags=["projects"])
app.include_router(paper.papers_router, prefix="/projects/{project_id}/papers", tags=["papers"])
app.include_router(summary.summaries_router, prefix="/projects/{project_id}/papers/{paper_id}/summaries", tags=["summaries"])
app.include_router(chat.chat_router, prefix="projects/{project_id}/papers/{paper_id}/chat", tags=["chat"])

@app.get("/")
async def root(settings: AppSettings = Depends(app_settings)):
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)