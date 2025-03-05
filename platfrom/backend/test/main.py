from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:8080",  # твой фронт на Vue
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # откуда можно делать запросы
    allow_credentials=True,
    allow_methods=["*"],  # какие методы разрешены
    allow_headers=["*"],  # какие заголовки разрешены
)
