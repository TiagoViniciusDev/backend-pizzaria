import os
from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

app = FastAPI() #variável app é uma instancia de FastAPI

#No parâmetro Schemes passamos o sistema de criptrografia, no caso, bcrypt (você pode ter mais de um)
#O deprecated serve para casa algum dos sistemas de criptrafia usado se torne obsoleto, o sistema pararia automaticamente de usa-lo e passaria a usar apenas os outros. Para nossa sintuação não é tão util já que estámos usando apenas apenas um sistema
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_routes
from order_routes import order_routes

app.include_router(auth_routes)
app.include_router(order_routes)

#Rodar Servidor: uvicorn main:app --reload

