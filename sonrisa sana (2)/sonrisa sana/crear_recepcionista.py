
import hashlib
import hmac
import secrets
import base64
import getpass

from conexion import conectar


# ============================================================
# SONRISA SANA
# CREACION SEGURA DE LA CUENTA INICIAL DE RECEPCIONISTA
# ============================================================

USUARIO = "recepcionista"
ROL = "Recepcionista"
ITERACIONES = 600_000


def generar_hash(contrasena):
    sal = secrets.token_bytes(16)

    derivado = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        sal,
        ITERACIONES
    )

    return (
        f"pbkdf2_sha256${ITERACIONES}$"
        f"{base64.b64encode(sal).decode('ascii')}$"
        f"{base64.b64encode(derivado).decode('ascii')}"
    )


def verificar_contrasena(contrasena, hash_guardado):
    try:
        algoritmo, iteraciones, sal_b64, hash_b64 = (
            hash_guardado.split("$")
        )

        if algoritmo != "pbkdf2_sha256":
            return False

        sal = base64.b64decode(sal_b64, validate=True)
        hash_original = base64.b64decode(
            hash_b64, validate=True
        )

        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            sal,
            int(iteraciones)
        )

        return hmac.compare_digest(
            hash_original,
            hash_calculado
        )

    except (ValueError, TypeError):
        return False


def crear_recepcionista():
    conexion = None

    print("=" * 55)
    print("SONRISA SANA - CUENTA INICIAL DE RECEPCIONISTA")
    print("=" * 55)

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdUsuario
            FROM dbo.UsuarioSistema
            WHERE NombreUsuario = ?
        """, (USUARIO,))

        if cursor.fetchone() is not None:
            print(
                "\nLa cuenta 'recepcionista' ya existe."
            )
            print(
                "No se modificaron sus datos ni contraseña."
            )
            return

        contrasena = getpass.getpass(
            "\nEscribe la contraseña nueva: "
        )

        confirmar = getpass.getpass(
            "Confirma la contraseña: "
        )

        if contrasena != confirmar:
            print("\nERROR: Las contraseñas no coinciden.")
            return

        if len(contrasena) < 12:
            print(
                "\nERROR: Utiliza una contraseña "
                "de al menos 12 caracteres."
            )
            return

        if len(contrasena.encode("utf-8")) > 1024:
            print("\nERROR: La contraseña es demasiado larga.")
            return

        contrasena_hash = generar_hash(contrasena)

        cursor.execute("""
            INSERT INTO dbo.UsuarioSistema
            (
                NombreUsuario,
                ContrasenaHash,
                Rol,
                IdPaciente,
                IdOdontologa,
                Activo
            )
            VALUES (?, ?, ?, NULL, NULL, 1)
        """, (
            USUARIO,
            contrasena_hash,
            ROL
        ))

        conexion.commit()

        print("\n" + "=" * 55)
        print("CUENTA CREADA CORRECTAMENTE")
        print("=" * 55)
        print(f"Usuario: {USUARIO}")
        print(f"Rol: {ROL}")
        print("Estado: Activo")
        print("Contraseña: Protegida mediante hash")
        print("=" * 55)

    except Exception as error:
        if conexion is not None:
            conexion.rollback()

        print("\nERROR AL CREAR LA CUENTA:")
        print(error)

    finally:
        if conexion is not None:
            conexion.close()


if __name__ == "__main__":
    crear_recepcionista()
