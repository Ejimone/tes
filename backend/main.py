from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Registrations import app as registrations_router
from chatservices import app as chatservices_router

# Create FastAPI application
app = FastAPI(
    title="WhatsApp DApp API",
    description="Decentralized WhatsApp API built on Ethereum blockchain",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    registrations_router,
    prefix="/api/v1",
    tags=["Users & Messaging"]
)

app.include_router(
    chatservices_router,
    prefix="/api/v1",
    tags=["Groups & Profile"]
)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "WhatsApp DApp API",
        "version": "1.0.0",
        "description": "Decentralized messaging platform on Ethereum",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "api_version": "1.0.0",
        "endpoints": {
            "user_management": {
                "register": "POST /api/v1/users/register",
                "get_user": "GET /api/v1/users/{address}",
                "check_exists": "GET /api/v1/users/{address}/exists",
                "update_status": "PUT /api/v1/users/status",
                "update_profile_picture": "PUT /api/v1/users/profile-picture",
                "block_user": "POST /api/v1/users/block"
            },
            "messaging": {
                "send_message": "POST /api/v1/messages/send",
                "get_chat": "POST /api/v1/messages/chat",
                "read_message": "POST /api/v1/messages/read",
                "delete_message": "DELETE /api/v1/messages/delete"
            },
            "groups": {
                "create_group": "POST /api/v1/groups/create",
                "get_user_groups": "GET /api/v1/groups/user/{user_address}",
                "send_group_message": "POST /api/v1/groups/messages/send",
                "get_group_messages": "GET /api/v1/groups/{group_id}/messages",
                "leave_group": "POST /api/v1/groups/leave"
            }
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
