"""API v1 router aggregation."""# ruff: noqa: I001 - Imports structured for Jinja2 template conditionals
from fastapi import APIRouter

from app.api.routes.v1 import healthfrom app.api.routes.v1 import admin_ratings, auth, usersfrom app.api.routes.v1 import sessionsfrom app.api.routes.v1 import conversationsfrom app.api.routes.v1 import admin_conversationsfrom app.api.routes.v1 import agentfrom app.api.routes.v1 import ragfrom app.api.routes.v1 import filesfrom app.api.routes.v1 import channelsfrom app.api.routes.v1 import telegram_webhook
v1_router = APIRouter()

# Health check routes (no auth required)
v1_router.include_router(health.router, tags=["health"])
# Authentication routes
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# User routes
v1_router.include_router(users.router, prefix="/users", tags=["users"])

# Admin routes
v1_router.include_router(admin_ratings.router, prefix="/admin/ratings", tags=["admin:ratings"])
# Session management routes
v1_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
# Conversation routes (AI chat persistence)
v1_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# AI Agent routes
v1_router.include_router(agent.router, tags=["agent"])
# RAG routes
v1_router.include_router(rag.router, prefix="/rag", tags=["rag"])
# File upload/download routes
v1_router.include_router(files.router, tags=["files"])
# Admin: conversation browser + user listing
v1_router.include_router(admin_conversations.router, prefix="/admin/conversations", tags=["admin-conversations"])
# Messaging channel admin routes (shared across Telegram, Slack)
v1_router.include_router(channels.router, prefix="/channels", tags=["channels"])
# Telegram webhook endpoint
v1_router.include_router(telegram_webhook.router, prefix="/telegram", tags=["telegram"])