import sqlite3

def init_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS services 
                      (host TEXT, port INTEGER, service TEXT, status TEXT, previewImage TEXT)''')
    conn.commit()
    conn.close()

def reset_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS services")
    conn.commit()
    conn.close()
    init_db()

def add_service_to_db(host, port, service, status, previewImage):
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services VALUES (?, ?, ?, ?, ?)", 
                   (host, port, service, status, previewImage))
    conn.commit()
    conn.close()

def get_services_from_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    conn.close()
    return services