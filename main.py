from contextlib import asynccontextmanager
from fastapi import FastAPI , Depends, HTTPException,BackgroundTasks, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from database.Database import engine,Base , get_db, AsyncSession
from schema.User import MessageCreate , UserCreate , UserLogin 
from services.User import UserService
from services.Auth import AuthService
from model.Model import User
from email.mime.text import MIMEText
from core.Security import JWT_ALGORITHM, create_access_token
import smtplib
from jose import jwt,JWTError
from datetime import timedelta 
from core.Config import settings
from schema.Blog import BlogCreate
from services.Blog import BlogService

@asynccontextmanager
async def lifespan(app=FastAPI):
    async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    
app= FastAPI(debug=True,lifespan=lifespan)

@app.get("/")
def hello():
    return{"message":"welcome to Ashatech"}

#-------------------------------------------------register------------------------------------------------------------------------------------#

@app.post("/register")
async def create_user(user_input:UserCreate,db:AsyncSession=Depends(get_db)):
    user_service = UserService(db)
    await user_service.create_user(user_input)
    return "user is created"
    
#--------------------------------------------------login---------------------------------------------------------------------------------------#

@app.post("/login")
async def login_user(user_input:UserLogin, response:Response,db: AsyncSession =Depends(get_db)):
    auth_service  = AuthService(db)
    token_data = await auth_service.login_user(user_input)
    response.set_cookie(
        key = "access_token",
        value= token_data,
        httponly=True,
        secure = True,
        samesite= "lax"
    )
    return {
        "message": token_data
    }
#--------------------------------------------------refresh---------------------------------------------------------------------------------------#
@app.post("/refresh")
def refresh_access_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    
    refresh_access = credentials.credentials
    
    try:
        payload = jwt.decode(refresh_access, settings.SECRET_KEY,algorithms= [JWT_ALGORITHM] )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=403, detail="Invalid token type")
        
        user_id = payload.get("sub")
    
    except JWTError:
        raise HTTPException(status_code=403, detail = "Invalid or expired refresh token ")
    
    new_access_token = create_access_token(
        data= {"sub": user_id, "type": "access"},
        expires_delta= timedelta(minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token ": new_access_token,
        "token_type": "bearer"
    }       
    

#---------------------------------------------logout----------------------------------------------------------------------------#
@app.post("/logout")
def logout():
    response = JSONResponse({"message": "Logout"})
    response.delete_cookie("access_token")
    return response

#--------------------------------------------create blog--------------------------------------------------------------------------
@app.post("/blog")
async def create_blog(user_input:BlogCreate, db:AsyncSession = Depends(get_db)):
    blog_service = BlogService(db)
    await blog_service.create_blog(user_input)
    return {
        "message": "Blog is created"
    }    
    
#--------------------------------------------get blog data--------------------------------------------------------------------------
# @app.get("/blog_all")
# async def get_blog(db:AsyncSession= Depends(get_db)):
#     blog_service = BlogService(db)
#     blog = await blog_service.get_blog()
#     return blog

#-----------------------------------------get blog by id----------------------------------------------------------------------------------
# @app.get("blog_id")
# async def get_blog_by_id(blog_id:int,db:AsyncSession = Depends(get_db)):
#     blog_service = BlogService(db)
#     blog = await blog_service.get_blog_by_id(blog_id)
#     return blog 
# ---------------------------------------send email message from a contact from-----------------------------------------------------------#



def send_email_background(user_input: MessageCreate):
    body = f"""
    New Message Received 
    Name: {user_input.name}
    Email: {user_input.email}
    Phone: {user_input.phone_no}
    Message: {user_input.message}
    """
    msg = MIMEText(body)
    msg["Subject"] = user_input.subject
    msg["From"] = user_input.email
    msg["To"] = settings.EMAIL_ADDRESS
    
    with smtplib.SMTP(settings.SMTP_SERVER ,settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.send_message(msg)

@app.post("/sendmessage")
async def send_message(user_input: MessageCreate,bg:BackgroundTasks, db:AsyncSession = Depends(get_db)):
    user_message = user_input
    if not user_message:
        raise HTTPException(status_code=404, detail={"message":"message not found"})
    bg.add_task(send_email_background, user_input)
    return "message is sent successfully"



