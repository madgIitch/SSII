import os
import hashlib
import sqlite3

directorio = r"C:\Users\peorr\OneDrive - UNIVERSIDAD DE SEVILLA\Universidad\4º Curso\1º Cuatrimestre\SSII"
directorioDB = r"C:\Users\peorr\OneDrive\Documentos\GitHub\SSII\hashes.db"

# Function to create the SQLite database and "hashes" table if it doesn't exist
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS hashes
                      (file_path TEXT PRIMARY KEY, hash_value TEXT)''')
    connection.commit()

# Function to calculate the SHA-1 hash of a single file
def hashFile(file_path):
    file_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# Function to hash files in the specified directory and store them in the database
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
                    
                    # Calculate the hash for the current file
                    file_hash = hashFile(file_path)
                    
                    cursor.execute("INSERT OR REPLACE INTO hashes (file_path, hash_value) VALUES (?, ?)", (file_path, file_hash))
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()
    
    return file_list

# Function to compare recalculated file hashes with the stored hashes in the database
def compareHashes(db_path):
    conn = sqlite3.connect(db_path)
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, hash_value FROM hashes")
            db_rows = cursor.fetchall()
            
            # Create a set of file paths that are already in the database
            db_file_paths = {row[0] for row in db_rows}
            
            for root, dirs, files in os.walk(directorio):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if file_path not in db_file_paths:
                        # Calculate the hash for the current file
                        file_hash = hashFile(file_path)
                        
                        cursor.execute("INSERT INTO hashes (file_path, hash_value) VALUES (?, ?)", (file_path, file_hash))
                        print(f"Added to database: {file_path} - Hash: {file_hash}")
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()

# Recalculate the hashes and compare
file_list = hashFiles(directorio, directorioDB)
compareHashes(directorioDB)
