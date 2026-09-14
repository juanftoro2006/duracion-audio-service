# main.py
# Servicio de duración de audio. Un solo trabajo: leer cuánto dura
# un archivo de audio SIN transcribirlo ni procesarlo con ffmpeg.

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from mutagen import File as MutagenFile
import io

app = FastAPI()

# Pydantic define la forma de la respuesta -- FastAPI la valida sola
# y genera documentación automática en /docs. Es la forma "seria" de
# hacerlo en vez de devolver un diccionario a mano.
class DuracionResponse(BaseModel):
    duracion_segundos: float


@app.post("/duracion", response_model=DuracionResponse)
async def duracion(request: Request):
    # El audio llega como bytes crudos en el body -- n8n nos lo manda
    # directo, sin envolverlo en JSON ni en un formulario.
    audio_bytes = await request.body()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No llegó ningún archivo")

    # mutagen necesita "algo que se pueda leer como archivo", no bytes
    # sueltos -- BytesIO lo simula en memoria, sin escribir nada a disco.
    audio_file = MutagenFile(io.BytesIO(audio_bytes))

    if audio_file is None or audio_file.info is None:
        # Esto pasa si el formato no es reconocible -- no es un error
        # nuestro, es un archivo raro o corrupto.
        raise HTTPException(status_code=422, detail="No se pudo leer la duración")

    # .info.length ya viene calculado en el propio archivo -- no lo
    # calculamos nosotros, solo lo leemos.
    return DuracionResponse(duracion_segundos=round(audio_file.info.length, 2))