import sqlite3

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

def verificar_cita_duplicada(fecha, hora):
    conn = sqlite3.connect('citas.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM citas WHERE fecha = ? AND hora = ?', (fecha, hora))
    count = c.fetchone()[0]
    conn.close()
    return count > 0 