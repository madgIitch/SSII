import os
import hashlib
import sqlite3
from datetime import datetime
import configparser

# Directorio de la base de datos fijo
directorioDB = r"C:\Users\peorr\OneDrive\Documentos\GitHub\SSII\hashes.db"

# Obtener el directorio del script actual
script_directory = os.path.dirname(os.path.abspath(__file__))

# Ruta completa al archivo de configuración "config.ini"
config_file_path = os.path.join(script_directory, "config.ini")

# Crear el archivo "config.ini" si no existe
if not os.path.exists(config_file_path):
    with open(config_file_path, "w") as configfile:
        configfile.write("[Config]\n")
        configfile.write("directorios = \n")

# Cargar la configuración desde "config.ini"
config = configparser.ConfigParser()
config.read(config_file_path)

# Obtener la lista de directorios de la configuración
directorios = config.get("Config", "directorios").splitlines()

# Función para crear la base de datos SQLite y la tabla "hashes" si no existen
def create_database(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS hashes
                      (file_path TEXT PRIMARY KEY, hash_value TEXT, timestamp TEXT)''')
    connection.commit()

# Función para calcular el hash SHA-1 de un archivo
def hashFile(file_path):
    file_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# Función para crear o actualizar las entradas en la base de datos para archivos de configuración y directorios
def crearOActualizarConfigEntry(db_path):
    conn = sqlite3.connect(db_path)
    
    try:
        create_database(conn)
        
        with conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            # Consultar si ya existe una entrada para config.ini en la base de datos
            cursor.execute("SELECT hash_value FROM hashes WHERE file_path = ?", (config_file_path,))
            existing_hash = cursor.fetchone()
            
            if existing_hash:
                # Si ya existe una entrada, actualizar el hash y la marca de tiempo
                config_hash = hashFile(config_file_path)
                cursor.execute("UPDATE hashes SET hash_value = ?, timestamp = ? WHERE file_path = ?", (config_hash, timestamp, config_file_path))
                print(f"Actualizada entrada para {config_file_path} en la base de datos.")
            else:
                # Si no existe una entrada, crear una nueva
                config_hash = hashFile(config_file_path)
                cursor.execute("INSERT INTO hashes (file_path, hash_value, timestamp) VALUES (?, ?, ?)", (config_file_path, config_hash, timestamp))
                print(f"Añadida nueva entrada para {config_file_path} en la base de datos.")
            
            # Consultar si ya existe una entrada para hashes.db en la base de datos
            cursor.execute("SELECT hash_value FROM hashes WHERE file_path = ?", (directorioDB,))
            existing_db_hash = cursor.fetchone()
            
            if existing_db_hash:
                # Si ya existe una entrada, actualizar el hash y la marca de tiempo
                db_hash = hashFile(directorioDB)
                cursor.execute("UPDATE hashes SET hash_value = ?, timestamp = ? WHERE file_path = ?", (db_hash, timestamp, directorioDB))
                print(f"Actualizada entrada para {directorioDB} en la base de datos.")
            else:
                # Si no existe una entrada, crear una nueva
                db_hash = hashFile(directorioDB)
                cursor.execute("INSERT INTO hashes (file_path, hash_value, timestamp) VALUES (?, ?, ?)", (directorioDB, db_hash, timestamp))
                print(f"Añadida nueva entrada para {directorioDB} en la base de datos.")
    
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()

# Función para hashear archivos en el directorio especificado y almacenarlos en la base de datos
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
                    
                    # Calcular el hash para el archivo actual
                    file_hash = hashFile(file_path)
                    
                    # Obtener la fecha y hora actual en formato ISO
                    timestamp = datetime.now().isoformat()
                    
                    cursor.execute("INSERT OR REPLACE INTO hashes (file_path, hash_value, timestamp) VALUES (?, ?, ?)", (file_path, file_hash, timestamp))
    
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()
    
    return file_list

# Función para comparar los hashes recalculados de los archivos con los almacenados en la base de datos
def compareHashes(db_path):
    conn = sqlite3.connect(db_path)
    
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path, hash_value, timestamp FROM hashes")
            db_rows = cursor.fetchall()
            
            # Crear un diccionario de rutas de archivos, sus hashes y marcas de tiempo que ya están en la base de datos
            db_file_info = {row[0]: (row[1], row[2]) for row in db_rows}
            
            for directorio in directorios:
                for root, dirs, files in os.walk(directorio):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        if file_path in db_file_info:
                            # Calcular el hash para el archivo actual
                            file_hash = hashFile(file_path)
                            
                            # Obtener el hash y la marca de tiempo almacenados en la base de datos
                            stored_hash, timestamp = db_file_info[file_path]
                            
                            if file_hash != stored_hash:
                                # Si el hash es diferente, el archivo ha sido modificado
                                print(f"Archivo modificado: {file_path}")
                                print(f"Fecha y hora de creación en la base de datos: {timestamp}")
                                
                                # Obtener la fecha y hora de la última modificación del archivo
                                mod_timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                                print(f"Fecha y hora de la última modificación: {mod_timestamp}")
                                
                                # Registrar la modificación en el informe mensual
                                registrarModificacionEnInforme(file_path, mod_timestamp)
                        else:
                            # Si el archivo no está en la base de datos, agregar una nueva entrada
                            file_hash = hashFile(file_path)
                            timestamp = datetime.now().isoformat()
                            cursor.execute("INSERT INTO hashes (file_path, hash_value, timestamp) VALUES (?, ?, ?)", (file_path, file_hash, timestamp))
                            print(f"Añadida nueva entrada para {file_path} en la base de datos.")
    
    except sqlite3.Error as e:
        print("Error:", e)
    finally:
        conn.close()
# Función para registrar la modificación en el informe mensual
def registrarModificacionEnInforme(file_path, mod_timestamp):
    # Obtener la fecha y año actual para el nombre del informe
    now = datetime.now()
    month_year = now.strftime("%B_%Y")
    
    # Crear o abrir el archivo de informe mensual correspondiente
    informe_file_path = os.path.join(script_directory, f"Informe_{month_year}.txt")
    
    with open(informe_file_path, "a") as informe_file:
        informe_file.write(f"{mod_timestamp}-{file_path}\n")

# Función para agregar un nuevo directorio
def agregarDirectorio():
    nuevo_directorio = input("Ingrese el nuevo directorio a analizar (por ejemplo, C:\\ruta\\al\\directorio): ")
    directorios.append(nuevo_directorio)
    print(f"Directorio agregado: {nuevo_directorio}")
    
    # Crear o actualizar la entrada de config.ini en la base de datos
    crearOActualizarConfigEntry(directorioDB)
    
    # Guardar la lista de directorios en la configuración y en el archivo "config.ini"
    config.set("Config", "directorios", "\n".join(directorios))
    with open(config_file_path, "w") as configfile:
        config.write(configfile)

# Función para crear un menú de opciones para el HIDS
def hids_menu():
    while True:
        print("\nMenú de Sistema de Detección de Intrusos Basado en el Host (HIDS):")
        print("1. Agregar Directorio")
        print("2. Inicializar base de datos (Crear la base de datos y hashear archivos)")
        print("3. Actualizar HIDS (Comparar y actualizar la base de datos)")
        print("4. Salir (Salir)")
        
        choice = input("Seleccione una opción: ")
        
        if choice == '1':
            agregarDirectorio()
        elif choice == '2':
            for directorio in directorios:
                print(f"Inicializando HIDS para el directorio: {directorio}")
                file_list = hashFiles(directorio, directorioDB)
                print(f"HIDS inicializado con éxito para el directorio: {directorio}")
        elif choice == '3':
            print("Actualizando HIDS...")
            compareHashes(directorioDB)
            print("HIDS actualizado con éxito.")
        elif choice == '4':
            print("Saliendo del Menú de HIDS.")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida (1, 2, 3 o 4).")

# Ejecutar el menú de HIDS
if __name__ == "__main__":
    hids_menu()
