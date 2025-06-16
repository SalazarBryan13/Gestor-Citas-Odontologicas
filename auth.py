from fastapi_login import LoginManager
import sqlite3

SECRET = "super-secret-key"
manager = LoginManager(SECRET, token_url="/login", use_cookie=True)

def get_user(username: str):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

@manager.user_loader()
def load_user(username: str):
    user = get_user(username)
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'password_hash': user[2],
            'nombre': user[3],
            'apellido': user[4],
            'email': user[5],
            'rol': user[6]
        }
    return None 