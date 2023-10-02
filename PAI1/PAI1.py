import os
import hashlib

directorio = r"C:\Users\peorr\OneDrive - UNIVERSIDAD DE SEVILLA\Universidad\4º Curso\1º Cuatrimestre\SSII"
directorioHash = r"C:\Users\peorr\OneDrive\Documentos\GitHub\SSII\hash.txt"

def hashFiles(path, pathHash):
    file_list = []
    with open(pathHash, "w") as h:  # Abre el archivo de hash en modo escritura (reemplaza el archivo existente)
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
                with open(file_path, "rb") as f:  # Abre el archivo en modo binario
                    file_hash = hashlib.sha1()
                    while chunk := f.read(8192):
                        file_hash.update(chunk)
                    h.write(f"{file_path} {file_hash.hexdigest()}\n")
    return file_list

file_list = hashFiles(directorio, directorioHash)
print("Hashes calculados y almacenados en el archivo 'hash.txt'.")
