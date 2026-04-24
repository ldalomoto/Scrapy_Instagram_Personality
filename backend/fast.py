# api.py (FastAPI con CORS habilitado)
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # Importamos CORSMiddleware
import version3_funcional
import requests
from fastapi.responses import Response
from fastapi import Query

app = FastAPI()

# Agregar CORS middleware para permitir solicitudes desde cualquier origen
origins = [
    "http://localhost:5173",  # React corre en este puerto
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/send-username/{username}&&{numPosts}&&{numComments}")
async def receive_username(username: str, numPosts: int, numComments: int):

    result = await version3_funcional.main(username, numPosts, numComments)
    return result
    

@app.get("/image-proxy")
def image_proxy(url: str = Query(...)):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    return Response(
        content=response.content,
        media_type=response.headers.get("Content-Type")
    )

from fastapi.responses import StreamingResponse

@app.get("/media-proxy")
def media_proxy(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.instagram.com/"
    }

    response = requests.get(url, headers=headers, stream=True)

    return StreamingResponse(
        response.iter_content(chunk_size=1024),
        media_type=response.headers.get("Content-Type")
    )
