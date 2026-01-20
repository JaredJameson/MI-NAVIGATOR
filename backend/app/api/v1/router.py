"""
API v1 Router - Aggregates all API endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, chat, reports, projects, companies, analysis, search, activity, notifications, help, feedback, custom_fields, tags, workspaces, billing, system, analytics, errors, admin, alerts, files, test_endpoints, research, webhooks, api_keys, ab_testing

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Chat endpoints
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Report endpoints
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Research endpoints
api_router.include_router(research.router, prefix="/research", tags=["Research"])

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

# Alerts endpoints
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])

# Help/Documentation endpoints
api_router.include_router(help.router, prefix="/help", tags=["Help"])

# Feedback endpoints
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])

# Custom Fields endpoints
api_router.include_router(custom_fields.router, prefix="/custom-fields", tags=["Custom Fields"])

# Tags endpoints
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])

# Workspace endpoints
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])

# Billing endpoints
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])

# System endpoints
api_router.include_router(system.router, prefix="/system", tags=["System"])

# Analytics endpoints
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Error tracking endpoints
api_router.include_router(errors.router, prefix="/errors", tags=["Errors"])

# Admin endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# File upload endpoints
api_router.include_router(files.router, prefix="/files", tags=["Files"])

# Webhook endpoints
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

# API Keys endpoints
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])

# Test endpoints (for development/testing only)
api_router.include_router(test_endpoints.router, prefix="/test", tags=["Testing"])

# A/B Testing endpoints
api_router.include_router(ab_testing.router, prefix="/ab-testing", tags=["A/B Testing"])
