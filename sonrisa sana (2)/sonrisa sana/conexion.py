
import pyodbc

# ============================================================
# CONFIGURACION DE LA BASE DE DATOS
# ============================================================

SERVIDOR = r"(localdb)\MSSQLLocalDB"
BASE_DATOS = "SonrisaSana"
CONTROLADOR = "ODBC Driver 18 for SQL Server"

CADENA_CONEXION = (
    f"DRIVER={{{CONTROLADOR}}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BASE_DATOS};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# ============================================================
# FUNCION CENTRAL DE CONEXION
# ============================================================

def conectar():
    """
    Abre y devuelve una conexion a la base de datos SonrisaSana.
    Todos los modulos del sistema deben utilizar esta funcion.
    """
    return pyodbc.connect(
        CADENA_CONEXION,
        timeout=5
    )


# ============================================================
# PRUEBA DE CONEXION
# ============================================================

if __name__ == "__main__":
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("SELECT DB_NAME()")
        nombre_bd = cursor.fetchone()[0]

        print("====================================")
        print("      CONEXION EXITOSA")
        print("====================================")
        print(f"Servidor: {SERVIDOR}")
        print(f"Base de datos: {nombre_bd}")
        print(f"Controlador: {CONTROLADOR}")
        print("====================================")

    except pyodbc.Error as error:
        print("ERROR AL CONECTAR CON SQL SERVER:")
        print(error)

    finally:
        if conexion is not None:
            conexion.close()
