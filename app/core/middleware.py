from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_user_from_request, generate_cookie_token
from config import settings
import json


class CookieAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip middleware for health check and static files
            if request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:
                await self.app(scope, receive, send)
                return
            
            # Get database session
            db = next(get_db())
            
            try:
                # Get or create user from cookie
                user = get_user_from_request(request, db)
                
                # Add user to request state
                request.state.user = user
                
                # Process request
                response = await self.app(scope, receive, send)
                
                # Set cookie if it doesn't exist
                if not request.cookies.get(settings.cookie_name):
                    # Generate new cookie token
                    cookie_token = generate_cookie_token()
                    # Update user with new token
                    user.cookie_token = cookie_token
                    db.commit()
                    
                    # Create response with cookie
                    if hasattr(response, 'set_cookie'):
                        response.set_cookie(
                            key=settings.cookie_name,
                            value=cookie_token,
                            max_age=settings.cookie_max_age,
                            httponly=True,
                            secure=False,  # Set to True in production with HTTPS
                            samesite="lax"
                        )
                
                return response
                
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"}
                )
            finally:
                db.close()
        else:
            await self.app(scope, receive, send)
