from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import init_db
from auth import manager, get_user
from routers.citas import router as citas_router
import uvicorn
from passlib.hash import bcrypt
from fastapi.responses import RedirectResponse
import sqlite3
from fastapi.routing import APIRoute
from starlette.requests import Request as StarletteRequest
from fastapi import status
import functools

app = FastAPI()

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar base de datos
init_db()

# Agregar rutas de citas
app.include_router(citas_router)

templates = Jinja2Templates(directory="templates")

# --- Registro de usuario (asistente) ---
@app.get('/register')
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post('/register')
def register(request: Request, username: str = Form(...), password: str = Form(...), nombre: str = Form(...), apellido: str = Form(...), email: str = Form(...)):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    password_hash = bcrypt.hash(password)
    try:
        c.execute('INSERT INTO usuarios (username, password_hash, nombre, apellido, email, rol) VALUES (?, ?, ?, ?, ?, ?)', (username, password_hash, nombre, apellido, email, 'asistente'))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return templates.TemplateResponse("register.html", {"request": request, "msg": "El usuario ya existe"})
    conn.close()
    return RedirectResponse(url="/login", status_code=303)

# --- Login ---
@app.get('/')
def root(request: Request):
    return RedirectResponse(url='/login', status_code=303)

@app.get('/login')
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post('/login')
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if not user or not bcrypt.verify(password, user[2]):
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Credenciales incorrectas"})
    access_token = manager.create_access_token(data={'sub': username})
    resp = RedirectResponse(url='/citas', status_code=303)
    manager.set_cookie(resp, access_token)
    return resp

@app.get('/logout')
def logout():
    resp = RedirectResponse(url='/login', status_code=303)
    resp.delete_cookie(manager.cookie_name)
    return resp

# --- Proteger rutas de citas ---
def login_required(route_func):
    @functools.wraps(route_func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request') or (args[0] if args else None)
        if request is None or not hasattr(request, 'cookies'):
            return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
        try:
            user = manager(request)
            if not user:
                return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
        except Exception:
            return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
        return await route_func(*args, **kwargs)
    return wrapper

# Proteger rutas de citas
import routers.citas as citas_router_mod
for route in citas_router_mod.router.routes:
    if isinstance(route, APIRoute):
        route.endpoint = login_required(route.endpoint)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 