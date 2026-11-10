
import base64
import hashlib
import hmac

from conexion import conectar


# ============================================================
# SONRISA SANA - AUTENTICACION DE USUARIOS
# ============================================================


def verificar_contrasena(contrasena, hash_guardado):

    try:
        if not isinstance(contrasena, str):
            return False

        if not isinstance(hash_guardado, str):
            return False

        partes = hash_guardado.split("$")

        if len(partes) != 4:
            return False

        algoritmo, iteraciones, sal_b64, hash_b64 = partes

        if algoritmo != "pbkdf2_sha256":
            return False

        cantidad_iteraciones = int(iteraciones)

        if cantidad_iteraciones < 100_000:
            return False

        if cantidad_iteraciones > 2_000_000:
            return False

        sal = base64.b64decode(
            sal_b64,
            validate=True
        )

        hash_original = base64.b64decode(
            hash_b64,
            validate=True
        )

        if len(sal) < 16:
            return False

        if len(hash_original) != hashlib.sha256().digest_size:
            return False

        hash_calculado = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena.encode("utf-8"),
            sal,
            cantidad_iteraciones
        )

        return hmac.compare_digest(
            hash_original,
            hash_calculado
        )

    except (
        ValueError,
        TypeError,
        OverflowError,
        UnicodeError
    ):
        return False


# ============================================================
# VALIDAR QUE EL ROL TENGA SU IDENTIFICADOR CORRECTO
# ============================================================


def validar_rol(rol, id_paciente, id_odontologa):

    if rol == "Recepcionista":
        return (
            id_paciente is None
            and id_odontologa is None
        )

    if rol == "Paciente":
        return (
            id_paciente is not None
            and id_odontologa is None
        )

    if rol == "Odontologa":
        return (
            id_odontologa is not None
            and id_paciente is None
        )

    return False


# ============================================================
# AUTENTICAR USUARIO EN SQL SERVER
# ============================================================


def autenticar_usuario(nombre_usuario, contrasena):

    if not isinstance(nombre_usuario, str):
        return None

    if not isinstance(contrasena, str):
        return None

    nombre_usuario = nombre_usuario.strip()

    if not nombre_usuario or not contrasena:
        return None

    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                IdUsuario,
                NombreUsuario,
                ContrasenaHash,
                Rol,
                IdPaciente,
                IdOdontologa,
                Activo
            FROM dbo.UsuarioSistema
            WHERE NombreUsuario = ?
        """, (
            nombre_usuario,
        ))

        registro = cursor.fetchone()

        # ----------------------------------------------------
        # VERIFICAR QUE EXISTA EL USUARIO
        # ----------------------------------------------------

        if registro is None:
            return None

        # ----------------------------------------------------
        # IMPEDIR ACCESO A CUENTAS INACTIVAS
        # ----------------------------------------------------

        if registro.Activo != 1:
            return None

        # ----------------------------------------------------
        # VALIDAR CONTRASENA
        # ----------------------------------------------------

        if not verificar_contrasena(
            contrasena,
            registro.ContrasenaHash
        ):
            return None

        # ----------------------------------------------------
        # VALIDAR ROL E IDENTIFICADORES
        # ----------------------------------------------------

        if not validar_rol(
            registro.Rol,
            registro.IdPaciente,
            registro.IdOdontologa
        ):
            return None

        # ----------------------------------------------------
        # DEVOLVER DATOS DE LA SESION AUTENTICADA
        # ----------------------------------------------------

        return {
            "id_usuario": registro.IdUsuario,
            "nombre_usuario": registro.NombreUsuario,
            "rol": registro.Rol,
            "id_paciente": registro.IdPaciente,
            "id_odontologa": registro.IdOdontologa
        }

    finally:
        if conexion is not None:
            conexion.close()
