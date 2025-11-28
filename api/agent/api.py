from fastapi import APIRouter
from api.agent.endpoints import auth, users, jobs, interviews, webhooks

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(jobs.router)
api_router.include_router(interviews.router)
api_router.include_router(webhooks.router)
