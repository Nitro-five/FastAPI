from fastapi import FastAPI, HTTPException, Depends, Request
from authx import AuthX, AuthXConfig
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Создание объекта конфигурации
config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 час
config.JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 день

# Инициализация AuthX с конфигурацией
security = AuthX(config=config)


# Схема для логина пользователя
class UserLoginShema(BaseModel):
    username: str
    password: str


# Эндпоинт для логина
@app.post("/login")
def login(creds: UserLoginShema, response: JSONResponse):
    if creds.username == "test" and creds.password == "test":
        # Создание access токена
        access_token = security.create_access_token(uid="12345")
        # Создание refresh токена
        refresh_token = security.create_refresh_token(uid="12345")

        # Сохраняем токены в cookies
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
        response.set_cookie("refresh_token", refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    raise HTTPException(401, "Incorrect username or password")


# Пример защищенного эндпоинта
@app.get("/protected", dependencies=[Depends(security.access_token_required)])
def protected():
    return {"data": "secret data"}


# Эндпоинт для обновления токена
@app.post("/refresh")
def refresh_token(request: Request):
    # Извлекаем refresh token из cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is missing")

    try:
        # Проверяем, что refresh token действителен
        user_id = security.verify_refresh_token(refresh_token)

        # Создаем новый access token
        new_access_token = security.create_access_token(uid=user_id)

        return {"access_token": new_access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired")
