from fastapi import APIRouter, HTTPException, status, Depends
from api.schemas import LoginRequest, TokenResponse, UserResponse, UserCreate
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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    """Register a new user and return JWT tokens."""
    from rest_framework_simplejwt.tokens import RefreshToken
    from api.schemas import UserCreate
    from api.dependencies import get_candidate_service, get_company_service
    
    # Check if user already exists
    if user_service.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if user_service.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Validate role
    if user_data.role not in ['candidate', 'company']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'candidate' or 'company'"
        )
    
    # Create new user
    user = user_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
        phone=user_data.phone
    )
    
    # Create corresponding profile based on role
    if user_data.role == 'candidate':
        from apps.core.models import Candidate
        Candidate.objects.create(
            user=user,
            full_name=user_data.username,
            skills=[],
            experience_years=0,
            education='',
        )
    elif user_data.role == 'company':
        from apps.core.models import Company
        Company.objects.create(
            user=user,
            company_name=user_data.username,
            industry='',
            size='',
            description='',
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
