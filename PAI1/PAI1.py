import os
import hashlib
import sqlite3

directorio = r"C:\Users\peorr\OneDrive - UNIVERSIDAD DE SEVILLA\Universidad\4º Curso\1º Cuatrimestre\SSII"
directorioDB = r"C:\Users\peorr\OneDrive\Documentos\GitHub\SSII\hashes.db"

def create_database(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS hashes
                      (file_path TEXT PRIMARY KEY, hash_value TEXT)''')
    connection.commit()

def hashFiles(path, db_path):
    file_list = []
    conn = sqlite3.connect(db_path)
    
    try:
        create_database(conn)
        
        with conn:
            cursor = conn.cursor()
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_list.append(file_path)
                    
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha1()
                        while chunk := f.read(8192):
                            file_hash.update(chunk)
                            
                        cursor.execute("INSERT OR REPLACE INTO hashes (file_path, hash_value) VALUES (?, ?)", (file_path, file_hash.hexdigest()))
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()
    
    return file_list

file_list = hashFiles(directorio, directorioDB)
print("Hashes calculados y almacenados en la base de datos 'hashes.db'.")
