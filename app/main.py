from fastapi import FastAPI
from app.routes import health, auth, debug
from app.config import settings

app = FastAPI(
    title="Epic FHIR Backend API",
    version="0.1.0",
    description="FastAPI boilerplate for Epic FHIR backend OAuth2 using JWT client assertion"
)

# Startup validation
@app.on_event("startup")
async def validate_configuration():
    """
    Validate required configuration on startup.
    Raises ValueError if critical configuration is missing.
    """
    if not settings.EPIC_CLIENT_ID:
        raise ValueError(
            "EPIC_CLIENT_ID is required. "
            "Set it in your .env file or environment variables."
        )

    if not settings.EPIC_PRIVATE_KEY_PATH:
        raise ValueError(
            "EPIC_PRIVATE_KEY_PATH is required. "
            "Set it in your .env file or environment variables."
        )

    print("✓ Configuration validated successfully")
    print(f"  Client ID: {settings.EPIC_CLIENT_ID}")
    print(f"  Key Path: {settings.EPIC_PRIVATE_KEY_PATH}")
    print(f"  Token Endpoint: {settings.EPIC_TOKEN_ENDPOINT}")
    if settings.EPIC_JWT_KID:
        print(f"  JWT Key ID (kid): {settings.EPIC_JWT_KID}")

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(debug.router, prefix="/debug", tags=["debug"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Epic FHIR Backend API",
        "version": "0.1.0",
        "docs": "/docs"
    }
