from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import JWTError, jwt

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str, algorithm: str, open_routes: list = None):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.open_routes = open_routes or ["/register", "/login"]

    async def dispatch(self, request: Request, call_next):
        # Разрешаем доступ к открытым маршрутам без авторизации
        if any(request.url.path.startswith(route) for route in self.open_routes):
            return await call_next(request)

        # Проверяем наличие заголовка Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Необходима авторизация"},
                status_code=401
            )

        token = auth_header[len("Bearer "):]
        try:
            # Декодируем токен
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user = payload  # Сохраняем информацию о пользователе
        except JWTError:
            return JSONResponse(
                {"detail": "Неверный токен"},
                status_code=401
            )

        return await call_next(request)
