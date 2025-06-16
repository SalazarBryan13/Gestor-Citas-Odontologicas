from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import init_db
from routers.citas import router as citas_router
import uvicorn

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar base de datos
init_db()

# Agregar rutas de citas
app.include_router(citas_router)

templates = Jinja2Templates(directory="templates")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 