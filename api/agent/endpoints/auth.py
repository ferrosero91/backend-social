from fastapi import APIRouter, HTTPException, status, Depends
from api.schemas import LoginRequest, TokenResponse, UserResponse
from api.dependencies import get_user_service, UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, user_service: UserService = Depends(get_user_service)):
    """Authenticate user and return JWT tokens."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    user = user_service.authenticate(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return TokenResponse(
        access=str(refresh.access_token),
        refresh=str(refresh),
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh")
def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    from rest_framework_simplejwt.tokens import RefreshToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    try:
        refresh = RefreshToken(refresh_token)
        return {
            "access": str(refresh.access_token)
        }
    except (InvalidToken, TokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
