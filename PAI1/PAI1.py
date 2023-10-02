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



def compareHashes(db_path):
    conn = sqlite3.connect(db_path)
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, hash_value FROM hashes")
            rows = cursor.fetchall()
            for row in rows:
                cursor.execute("SELECT file_path, hash_value FROM hashes WHERE hash_value = ?", (row[1],))
                rows = cursor.fetchall()
                if len(rows) > 1:
                    print("Los siguientes archivos son iguales:")
                    for row in rows:
                        print(row[0])
                    print()
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()

compareHashes(directorioDB)