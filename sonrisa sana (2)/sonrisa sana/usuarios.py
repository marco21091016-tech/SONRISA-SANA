
import base64
import hashlib
import secrets
import customtkinter as ctk

from tkinter import ttk, messagebox
from conexion import conectar


# ============================================================
# SONRISA SANA - ADMINISTRACION DE USUARIOS
# ACCESO EXCLUSIVO PARA RECEPCIONISTA
# ============================================================

FONDO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
VERDE = "#159F95"
VERDE_OSCURO = "#087F78"
TEXTO = "#263B3A"
BORDE = "#B8DED8"
BLANCO = "#FFFFFF"

ITERACIONES = 600_000


# ============================================================
# PROTECCION DE CONTRASEÑAS
# COMPATIBLE CON autenticacion.py
# ============================================================

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


# ============================================================
# PANEL DE USUARIOS
# ============================================================

class PanelUsuarios(ctk.CTkFrame):

    def __init__(self, master, usuario_actual=None):
        super().__init__(
            master,
            fg_color=FONDO,
            corner_radius=0
        )

        self.usuario_actual = usuario_actual or {}

        if self.usuario_actual.get("rol") != "Recepcionista":
            raise PermissionError(
                "Acceso exclusivo para recepcionista."
            )

        self.personas = {}
        self.usuario_seleccionado = None

        self.crear_interfaz()
        self.cargar_usuarios()

    # ========================================================
    # INTERFAZ PRINCIPAL
    # ========================================================

    def crear_interfaz(self):

        contenido = ctk.CTkScrollableFrame(
            self,
            fg_color=FONDO,
            scrollbar_button_color=BORDE
        )
        contenido.pack(fill="both", expand=True)

        ctk.CTkLabel(
            contenido,
            text="ADMINISTRACION DE USUARIOS",
            font=("Georgia", 25, "bold"),
            text_color=VERDE_OSCURO
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            contenido,
            text=(
                "Crea y administra las cuentas de acceso "
                "de pacientes y odontologas."
            ),
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        formulario = ctk.CTkFrame(
            contenido,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE
        )
        formulario.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            formulario,
            text="CREAR NUEVA CUENTA",
            font=("Arial", 15, "bold"),
            text_color=VERDE
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 15)
        )

        ctk.CTkLabel(
            formulario,
            text="Rol del usuario",
            text_color=TEXTO
        ).pack(anchor="w", padx=20)

        self.combo_rol = ctk.CTkComboBox(
            formulario,
            values=["Paciente", "Odontologa"],
            state="readonly",
            width=350,
            command=self.cambiar_rol
        )
        self.combo_rol.pack(
            anchor="w",
            padx=20,
            pady=(5, 12)
        )
        self.combo_rol.set("Paciente")

        ctk.CTkLabel(
            formulario,
            text="Persona registrada",
            text_color=TEXTO
        ).pack(anchor="w", padx=20)

        self.combo_persona = ctk.CTkComboBox(
            formulario,
            values=["Selecciona una persona"],
            state="readonly",
            width=350
        )
        self.combo_persona.pack(
            anchor="w",
            padx=20,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            formulario,
            text="Nombre de usuario",
            text_color=TEXTO
        ).pack(anchor="w", padx=20)

        self.entrada_usuario = ctk.CTkEntry(
            formulario,
            width=350,
            height=40,
            placeholder_text="Nombre de usuario",
            fg_color=PANEL_CLARO,
            border_color=BORDE,
            text_color=TEXTO
        )
        self.entrada_usuario.pack(
            anchor="w",
            padx=20,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            formulario,
            text="Contraseña inicial",
            text_color=TEXTO
        ).pack(anchor="w", padx=20)

        self.entrada_contrasena = ctk.CTkEntry(
            formulario,
            width=350,
            height=40,
            placeholder_text="Minimo 12 caracteres",
            show="●",
            fg_color=PANEL_CLARO,
            border_color=BORDE,
            text_color=TEXTO
        )
        self.entrada_contrasena.pack(
            anchor="w",
            padx=20,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            formulario,
            text="Confirmar contraseña",
            text_color=TEXTO
        ).pack(anchor="w", padx=20)

        self.entrada_confirmar = ctk.CTkEntry(
            formulario,
            width=350,
            height=40,
            placeholder_text="Repite la contraseña",
            show="●",
            fg_color=PANEL_CLARO,
            border_color=BORDE,
            text_color=TEXTO
        )
        self.entrada_confirmar.pack(
            anchor="w",
            padx=20,
            pady=(5, 15)
        )

        ctk.CTkButton(
            formulario,
            text="CREAR CUENTA",
            width=350,
            height=42,
            fg_color=VERDE,
            hover_color=VERDE_OSCURO,
            font=("Arial", 12, "bold"),
            command=self.crear_usuario
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # TABLA DE CUENTAS

        tabla_frame = ctk.CTkFrame(
            contenido,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE
        )
        tabla_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            tabla_frame,
            text="CUENTAS REGISTRADAS",
            font=("Arial", 15, "bold"),
            text_color=VERDE
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        estilo = ttk.Style()
        estilo.configure(
            "Usuarios.Treeview",
            rowheight=30,
            font=("Arial", 10)
        )
        estilo.configure(
            "Usuarios.Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        columnas = (
            "id",
            "usuario",
            "rol",
            "persona",
            "estado"
        )

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=9,
            style="Usuarios.Treeview",
            selectmode="browse"
        )

        encabezados = {
            "id": "ID",
            "usuario": "Usuario",
            "rol": "Rol",
            "persona": "Persona",
            "estado": "Estado"
        }

        for columna, titulo in encabezados.items():
            self.tabla.heading(
                columna,
                text=titulo
            )

        self.tabla.column(
            "id",
            width=55,
            anchor="center"
        )
        self.tabla.column("usuario", width=150)
        self.tabla.column("rol", width=120)
        self.tabla.column("persona", width=210)
        self.tabla.column(
            "estado",
            width=100,
            anchor="center"
        )

        self.tabla.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12)
        )

        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.seleccionar_usuario
        )

        botones = ctk.CTkFrame(
            tabla_frame,
            fg_color="transparent"
        )
        botones.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        ctk.CTkButton(
            botones,
            text="Actualizar lista",
            fg_color=VERDE,
            hover_color=VERDE_OSCURO,
            command=self.cargar_usuarios
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botones,
            text="Activar cuenta",
            fg_color=VERDE,
            hover_color=VERDE_OSCURO,
            command=lambda: self.cambiar_estado(True)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botones,
            text="Desactivar cuenta",
            fg_color="#B33A3A",
            hover_color="#922B2B",
            command=lambda: self.cambiar_estado(False)
        ).pack(side="left", padx=5)

        self.cargar_personas()

    # ========================================================
    # CARGAR PACIENTES Y ODONTOLOGAS
    # ========================================================

    def cambiar_rol(self, valor):
        self.cargar_personas()

    def cargar_personas(self):

        conexion = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            rol = self.combo_rol.get()

            if rol == "Paciente":
                consulta = """
                    SELECT IdPaciente, Nombre, Apellidos
                    FROM dbo.Paciente
                    ORDER BY Nombre, Apellidos
                """
            else:
                consulta = """
                    SELECT IdOdontologa, Nombre, Apellidos
                    FROM dbo.Odontologa
                    ORDER BY Nombre, Apellidos
                """

            cursor.execute(consulta)

            self.personas = {}

            for fila in cursor.fetchall():
                identificador = int(fila[0])
                nombre = f"{fila[1]} {fila[2]}"

                etiqueta = (
                    f"{identificador} - {nombre}"
                )

                self.personas[etiqueta] = identificador

            opciones = list(self.personas.keys())

            if opciones:
                self.combo_persona.configure(
                    values=opciones
                )
                self.combo_persona.set(opciones[0])
            else:
                self.combo_persona.configure(
                    values=["Sin registros"]
                )
                self.combo_persona.set("Sin registros")

        except Exception as error:
            print("ERROR AL CARGAR PERSONAS:", error)

            messagebox.showerror(
                "Sonrisa Sana",
                "No se pudieron cargar las personas.",
                parent=self.winfo_toplevel()
            )

        finally:
            if conexion is not None:
                conexion.close()

    # ========================================================
    # CREAR CUENTA
    # ========================================================

    def crear_usuario(self):

        rol = self.combo_rol.get()
        persona = self.combo_persona.get()

        nombre_usuario = (
            self.entrada_usuario.get().strip()
        )

        contrasena = self.entrada_contrasena.get()
        confirmar = self.entrada_confirmar.get()

        if rol not in ("Paciente", "Odontologa"):
            messagebox.showwarning(
                "Sonrisa Sana",
                "Selecciona un rol valido.",
                parent=self.winfo_toplevel()
            )
            return

        if persona not in self.personas:
            messagebox.showwarning(
                "Sonrisa Sana",
                "Selecciona una persona registrada.",
                parent=self.winfo_toplevel()
            )
            return

        if not nombre_usuario:
            messagebox.showwarning(
                "Sonrisa Sana",
                "Escribe el nombre de usuario.",
                parent=self.winfo_toplevel()
            )
            return

        if (
            len(nombre_usuario) > 100
            or not all(
                c.isascii() and (
                    c.isalnum() or c in "._-"
                )
                for c in nombre_usuario
            )
        ):
            messagebox.showwarning(
                "Sonrisa Sana",
                "El usuario solo puede contener letras, "
                "numeros, puntos, guiones y guion bajo "
                "(maximo 100 caracteres).",
                parent=self.winfo_toplevel()
            )
            return

        if len(contrasena) < 12:
            messagebox.showwarning(
                "Sonrisa Sana",
                "La contraseña debe tener "
                "al menos 12 caracteres.",
                parent=self.winfo_toplevel()
            )
            return

        if len(contrasena.encode("utf-8")) > 1024:
            messagebox.showwarning(
                "Sonrisa Sana",
                "La contraseña es demasiado larga.",
                parent=self.winfo_toplevel()
            )
            return

        if contrasena != confirmar:
            messagebox.showwarning(
                "Sonrisa Sana",
                "Las contraseñas no coinciden.",
                parent=self.winfo_toplevel()
            )
            return

        identificador = self.personas[persona]

        id_paciente = (
            identificador
            if rol == "Paciente"
            else None
        )

        id_odontologa = (
            identificador
            if rol == "Odontologa"
            else None
        )

        conexion = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            # COMPROBAR NOMBRE DE USUARIO

            cursor.execute("""
                SELECT COUNT(*)
                FROM dbo.UsuarioSistema
                WHERE NombreUsuario = ?
            """, (nombre_usuario,))

            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Sonrisa Sana",
                    "Ese nombre de usuario ya existe.",
                    parent=self.winfo_toplevel()
                )
                return

            # COMPROBAR CUENTA DE LA PERSONA

            if rol == "Paciente":
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.UsuarioSistema
                    WHERE IdPaciente = ?
                """, (identificador,))
            else:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.UsuarioSistema
                    WHERE IdOdontologa = ?
                """, (identificador,))

            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Sonrisa Sana",
                    "Esta persona ya tiene una cuenta.",
                    parent=self.winfo_toplevel()
                )
                return

            hash_contrasena = generar_hash(contrasena)

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
                VALUES (?, ?, ?, ?, ?, 1)
            """, (
                nombre_usuario,
                hash_contrasena,
                rol,
                id_paciente,
                id_odontologa
            ))

            conexion.commit()

            self.entrada_usuario.delete(0, "end")
            self.entrada_contrasena.delete(0, "end")
            self.entrada_confirmar.delete(0, "end")

            self.cargar_usuarios()

            messagebox.showinfo(
                "Sonrisa Sana",
                "Cuenta creada correctamente.",
                parent=self.winfo_toplevel()
            )

        except Exception as error:
            if conexion is not None:
                conexion.rollback()

            print("ERROR AL CREAR USUARIO:", error)

            messagebox.showerror(
                "Sonrisa Sana",
                "No se pudo crear la cuenta.\n"
                "Revisa la terminal de VS Code.",
                parent=self.winfo_toplevel()
            )

        finally:
            if conexion is not None:
                conexion.close()

    # ========================================================
    # CONSULTAR CUENTAS
    # ========================================================

    def cargar_usuarios(self):

        conexion = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT
                    u.IdUsuario,
                    u.NombreUsuario,
                    u.Rol,
                    COALESCE(
                        p.Nombre + ' ' + p.Apellidos,
                        o.Nombre + ' ' + o.Apellidos,
                        'Recepcionista'
                    ) AS Persona,
                    u.Activo
                FROM dbo.UsuarioSistema u
                LEFT JOIN dbo.Paciente p
                    ON u.IdPaciente = p.IdPaciente
                LEFT JOIN dbo.Odontologa o
                    ON u.IdOdontologa = o.IdOdontologa
                ORDER BY u.IdUsuario
            """)

            for elemento in self.tabla.get_children():
                self.tabla.delete(elemento)

            self.usuario_seleccionado = None

            for fila in cursor.fetchall():

                estado = (
                    "Activo"
                    if fila[4]
                    else "Inactivo"
                )

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        fila[0],
                        fila[1],
                        fila[2],
                        fila[3],
                        estado
                    )
                )

        except Exception as error:
            print("ERROR AL CONSULTAR USUARIOS:", error)

            messagebox.showerror(
                "Sonrisa Sana",
                "No se pudo consultar la lista de usuarios.",
                parent=self.winfo_toplevel()
            )

        finally:
            if conexion is not None:
                conexion.close()

    # ========================================================
    # SELECCIONAR CUENTA
    # ========================================================

    def seleccionar_usuario(self, event=None):

        seleccion = self.tabla.selection()

        if not seleccion:
            self.usuario_seleccionado = None
            return

        valores = self.tabla.item(
            seleccion[0],
            "values"
        )

        self.usuario_seleccionado = int(valores[0])

    # ========================================================
    # ACTIVAR / DESACTIVAR CUENTA
    # ========================================================

    def cambiar_estado(self, activar):

        if self.usuario_seleccionado is None:
            messagebox.showwarning(
                "Sonrisa Sana",
                "Selecciona una cuenta de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        conexion = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT NombreUsuario, Rol
                FROM dbo.UsuarioSistema
                WHERE IdUsuario = ?
            """, (self.usuario_seleccionado,))

            registro = cursor.fetchone()

            if registro is None:
                messagebox.showwarning(
                    "Sonrisa Sana",
                    "La cuenta ya no existe.",
                    parent=self.winfo_toplevel()
                )
                return

            # PROTEGER LA CUENTA DE RECEPCIONISTA

            if registro[1] == "Recepcionista":
                messagebox.showwarning(
                    "Sonrisa Sana",
                    "La cuenta de recepcionista "
                    "no puede modificarse desde este modulo.",
                    parent=self.winfo_toplevel()
                )
                return

            accion = (
                "activar"
                if activar
                else "desactivar"
            )

            confirmar = messagebox.askyesno(
                "Sonrisa Sana",
                f"¿Deseas {accion} la cuenta "
                f"'{registro[0]}'?",
                parent=self.winfo_toplevel()
            )

            if not confirmar:
                return

            cursor.execute("""
                UPDATE dbo.UsuarioSistema
                SET Activo = ?
                WHERE IdUsuario = ?
                  AND Rol IN ('Paciente', 'Odontologa')
            """, (
                1 if activar else 0,
                self.usuario_seleccionado
            ))

            conexion.commit()

            self.cargar_usuarios()

            messagebox.showinfo(
                "Sonrisa Sana",
                "Estado actualizado correctamente.",
                parent=self.winfo_toplevel()
            )

        except Exception as error:
            if conexion is not None:
                conexion.rollback()

            print("ERROR AL CAMBIAR ESTADO:", error)

            messagebox.showerror(
                "Sonrisa Sana",
                "No se pudo actualizar la cuenta.",
                parent=self.winfo_toplevel()
            )

        finally:
            if conexion is not None:
                conexion.close()
