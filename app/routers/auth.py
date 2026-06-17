from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, UserCreate, UserOut, TokenResponse, UserUpdate
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user, require_roles
from app.utils.helpers import log_action

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    log_action(db, user, "User login", ip=request.client.host if request.client else None)
    return {"access_token": token, "user": user}

@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user=Depends(require_roles("admin"))):
    return db.query(User).all()

@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_roles("admin"))):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        password=hash_password(payload.password),
        role=payload.role,
        firm=payload.firm,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, current_user, "Created user account", target=user.email)
    return user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user=Depends(require_roles("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.full_name is not None: user.full_name = payload.full_name
    if payload.role is not None:      user.role = payload.role
    if payload.is_active is not None: user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user
