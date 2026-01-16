"""
API v1 Router - Aggregates all API endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, chat, reports, projects, companies, analysis, search, activity, notifications, help, feedback, custom_fields

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Chat endpoints
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Report endpoints
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Project endpoints
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Company endpoints
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])

# Analysis endpoints
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])

# Search endpoints
api_router.include_router(search.router, prefix="/search", tags=["Search"])

# Activity endpoints
api_router.include_router(activity.router, prefix="/activity", tags=["Activity"])

# Notifications endpoints
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Help/Documentation endpoints
api_router.include_router(help.router, prefix="/help", tags=["Help"])

# Feedback endpoints
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])

# Custom Fields endpoints
api_router.include_router(custom_fields.router, prefix="/custom-fields", tags=["Custom Fields"])
