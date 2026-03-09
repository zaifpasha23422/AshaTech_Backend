from sqlalchemy import AsyncSession



class WebService:
    def __init__(self, db:AsyncSession):
        self.db: AsyncSession = db 
    
    async def  create_service(self, user_input:)    