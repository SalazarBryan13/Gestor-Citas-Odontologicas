import sqlite3

def init_db():
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_paciente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT NOT NULL,
            telefono TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()

def verificar_cita_duplicada(fecha, hora):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM citas WHERE fecha = ? AND hora = ?', (fecha, hora))
    count = c.fetchone()[0]
    conn.close()
    return count > 0 