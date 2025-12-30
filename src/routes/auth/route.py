from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.db import get_db
from src.models.users import Users
from src.models.schemas.user import UserCreate, UserOut
from src.routes.auth.schemas import SignupIn, TokenWithUserOut
from src.utils.security import hash_password, verify_password
from src.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(data: SignupIn, db: AsyncSession = Depends(get_db)):
	# check existing
	result = await db.execute(select(Users).where(Users.email == data.email))
	if result.scalars().first():
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

	new_user = Users(email=data.email, username=data.username, password_hash=hash_password(data.password))
	db.add(new_user)
	await db.commit()
	await db.refresh(new_user)
	return new_user


@router.post("/token", response_model=TokenWithUserOut)
async def token(form_data: SignupIn, db: AsyncSession = Depends(get_db)):
	# Accepts email/password and returns JWT and user info if valid
	result = await db.execute(select(Users).where(Users.email == form_data.email))
	user = result.scalars().first()
	if user is None or not verify_password(form_data.password, user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	# ensure relationships are available while session is open
	await db.refresh(user)

	token = create_access_token({"user_id": user.id})
	return {"access_token": token, "user": user}

