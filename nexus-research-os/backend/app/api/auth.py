from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_current_user,
    TokenData
)
from app.models import User, Organization
from app.models.schemas import (
    UserCreate, 
    UserResponse, 
    UserLogin, 
    TokenResponse,
    OrganizationCreate,
    OrganizationResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Get or create organization
    organization = None
    if user_data.organization_id:
        result = await db.execute(
            select(Organization).where(Organization.id == user_data.organization_id)
        )
        organization = result.scalar_one_or_none()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not found"
            )
    else:
        # Create default organization for user
        org_name = f"{user_data.full_name or user_data.email.split('@')[0]}'s Lab"
        org_slug = org_name.lower().replace(" ", "-")[:100]
        
        # Ensure slug uniqueness
        counter = 1
        original_slug = org_slug
        while True:
            result = await db.execute(select(Organization).where(Organization.slug == org_slug))
            if not result.scalar_one_or_none():
                break
            org_slug = f"{original_slug}-{counter}"
            counter += 1
        
        organization = Organization(
            name=org_name,
            slug=org_slug,
            description=f"Research organization for {user_data.full_name or user_data.email}"
        )
        db.add(organization)
        await db.flush()
    
    # Create user
    hashed_pw = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name,
        role=user_data.role,
        organization_id=organization.id
    )
    
    db.add(user)
    await db.flush()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens."""
    # Find user
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    await db.flush()
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "org_id": str(user.organization_id) if user.organization_id else None,
        "roles": [user.role.value]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # In a real implementation, you would validate the refresh token separately
    # and check if it's been revoked
    
    token_data = {
        "sub": current_user.user_id,
        "email": current_user.email,
        "org_id": current_user.organization_id,
        "roles": current_user.roles
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user information."""
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/logout")
async def logout(
    current_user: TokenData = Depends(get_current_user)
):
    """Logout user (invalidate tokens)."""
    # In a real implementation, you would add the token to a blacklist
    # or use short-lived tokens with Redis for session management
    return {"message": "Successfully logged out"}
