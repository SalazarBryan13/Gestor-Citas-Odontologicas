from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Database initialization
def init_db():
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_paciente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Agregar función de ejemplo para enviar notificaciones por email
def enviar_notificacion_email(nombre_paciente, fecha, hora):
    # Simulación de envío de email
    print(f"Notificación enviada a {nombre_paciente} para la cita del {fecha} a las {hora}")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/citas")
async def listar_citas(request: Request):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('SELECT * FROM citas ORDER BY fecha, hora')
    citas = c.fetchall()
    conn.close()
    return templates.TemplateResponse("citas.html", {"request": request, "citas": citas})

@app.get("/nueva-cita")
async def nueva_cita_form(request: Request):
    return templates.TemplateResponse("nueva_cita.html", {"request": request})

@app.post("/nueva-cita")
async def crear_cita(
    nombre_paciente: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    motivo: str = Form(...),
    telefono: str = Form(...)
):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO citas (nombre_paciente, fecha, hora, motivo, telefono)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre_paciente, fecha, hora, motivo, telefono))
    conn.commit()
    conn.close()
    # Llamar a la función de notificación
    enviar_notificacion_email(nombre_paciente, fecha, hora)
    return RedirectResponse(url="/citas", status_code=303)

@app.get("/eliminar-cita/{cita_id}")
async def eliminar_cita(cita_id: int):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('DELETE FROM citas WHERE id = ?', (cita_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/citas", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 