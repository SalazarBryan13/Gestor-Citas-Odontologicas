from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from db import verificar_cita_duplicada
from notificaciones import enviar_notificacion_email

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/citas")
async def listar_citas(request: Request):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('SELECT * FROM citas ORDER BY fecha, hora')
    citas = c.fetchall()
    conn.close()
    return templates.TemplateResponse("citas.html", {"request": request, "citas": citas})

@router.get("/nueva-cita")
async def nueva_cita_form(request: Request):
    return templates.TemplateResponse("nueva_cita.html", {"request": request})

@router.post("/nueva-cita")
async def crear_cita(
    nombre_paciente: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    motivo: str = Form(...),
    telefono: str = Form(...)
):
    if verificar_cita_duplicada(fecha, hora):
        raise HTTPException(status_code=400, detail="Ya existe una cita programada para esta fecha y hora.")
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO citas (nombre_paciente, fecha, hora, motivo, telefono)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre_paciente, fecha, hora, motivo, telefono))
    conn.commit()
    conn.close()
    enviar_notificacion_email(nombre_paciente, fecha, hora)
    return RedirectResponse(url="/citas", status_code=303)

@router.get("/eliminar-cita/{cita_id}")
async def eliminar_cita(cita_id: int):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('DELETE FROM citas WHERE id = ?', (cita_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/citas", status_code=303) 