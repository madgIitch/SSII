#Sistema HIDS para la deteccion de intrusiones en sistemas Windows

import os
import sys
import time
import hashlib

directorio = r"C:\Users\peorr\OneDrive - UNIVERSIDAD DE SEVILLA\Universidad\4º Curso\1º Cuatrimestre\SSII"

pathHash = "C:/Users/Usuario/Desktop/SSII/PAI/PAI1/hash.txt"



#Read a path and return a list with all files in the path
def readPath(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


#Por cada fichero que nos devuelve readPath, calculamos su hash y lo guardamos en un fichero

def hashFiles(file_list):
    f = open(pathHash, "w")
    for file in file_list:
        try:
            hash = hashlib.sha256(open(file, "rb").read()).hexdigest()
            f.write(file + " " + hash + "\n")
        except:
            print("Error al calcular el hash del fichero " + file)
    f.close()

hashFiles(readPath(directorio))
