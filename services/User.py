from sqlalchemy.ext.asyncio import AsyncSession
from schema.User import  UserCreate
from model.Model import User
from sqlalchemy import select
from core.Security import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError

class UserService():
    def __init__(self, db:AsyncSession):
        self.db: AsyncSession = db 
    
    
    async def get_user_by_email(self, email:str) -> User | None :
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()
        
        
    async def create_user(self,user_input:UserCreate):
        existing_user_by_email = await self.get_user_by_email(user_input.email)
        if existing_user_by_email:
            raise ValueError(f"User with this {user_input.email} is already exist ")
        
        hashed_password = get_password_hash(user_input.password)
        user_input.password = hashed_password
        
        
        user_create = User(**user_input.model_dump())
        self.db.add(user_create)
        try:
            await self.db.commit()
            await self.db.refresh(user_create)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("email is already registered ")
        return user_create
    
    
    