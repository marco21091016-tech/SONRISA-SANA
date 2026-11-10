
import tkinter as tk
from tkinter import ttk, messagebox

import customtkinter as ctk

from conexion import conectar


# ============================================================
# SONRISA SANA
# PANEL EXCLUSIVO PARA ODONTOLOGAS
# ============================================================

FONDO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
VERDE = "#159F95"
VERDE_OSCURO = "#087F78"
TEXTO = "#263B3A"
BORDE = "#B8DED8"
SELECCION = "#BFEDE6"


class PanelOdontologa(ctk.CTkFrame):

    def __init__(self, master, usuario):
        super().__init__(
            master,
            fg_color=FONDO,
            corner_radius=0
        )

        # ====================================================
        # VALIDAR DATOS DE LA SESION
        # ====================================================

        if not isinstance(usuario, dict):
            raise PermissionError(
                "No existe una sesion valida."
            )

        if usuario.get("rol") != "Odontologa":
            raise PermissionError(
                "Acceso exclusivo para odontologas."
            )

        if (
            usuario.get("id_usuario") is None
            or usuario.get("id_odontologa") is None
        ):
            raise PermissionError(
                "La cuenta no tiene una odontologa asociada."
            )

        self.id_usuario = int(
            usuario["id_usuario"]
        )

        self.id_odontologa = int(
            usuario["id_odontologa"]
        )

        self.nombre_usuario = usuario.get(
            "nombre_usuario",
            ""
        )

        # Validar cuenta antes de mostrar datos
        self.verificar_sesion()

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            1,
            weight=1
        )

        self.crear_interfaz()
        self.mostrar_perfil()

    # ========================================================
    # SEGURIDAD Y VALIDACION
    # ========================================================

    def validar_acceso(self, cursor):

        cursor.execute("""
            SELECT IdOdontologa
            FROM dbo.UsuarioSistema
            WHERE IdUsuario = ?
              AND Rol = 'Odontologa'
              AND IdOdontologa = ?
              AND Activo = 1
        """, (
            self.id_usuario,
            self.id_odontologa
        ))

        registro = cursor.fetchone()

        if registro is None:
            raise PermissionError(
                "La cuenta no esta activa o "
                "no tiene autorizacion para "
                "consultar esta odontologa."
            )

    def verificar_sesion(self):

        conexion_db = None

        try:
            conexion_db = conectar()
            cursor = conexion_db.cursor()

            self.validar_acceso(cursor)

        finally:
            if conexion_db is not None:
                conexion_db.close()

    def consultar(self, sql, parametros):

        conexion_db = None

        try:
            conexion_db = conectar()
            cursor = conexion_db.cursor()

            # Validar cuenta en cada consulta
            self.validar_acceso(cursor)

            cursor.execute(
                sql,
                parametros
            )

            return cursor.fetchall()

        finally:
            if conexion_db is not None:
                conexion_db.close()

    # ========================================================
    # CREAR INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE
        )

        encabezado.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            encabezado,
            text="MI ESPACIO PROFESIONAL",
            font=("Georgia", 25, "bold"),
            text_color=VERDE_OSCURO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        ctk.CTkLabel(
            encabezado,
            text=(
                "Consulta tu informacion profesional "
                "y las citas que tienes asignadas."
            ),
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 14)
        )

        navegacion = ctk.CTkFrame(
            encabezado,
            fg_color="transparent"
        )

        navegacion.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        self.botones = {}

        opciones = [
            (
                "Mi perfil profesional",
                self.mostrar_perfil
            ),
            (
                "Mis citas",
                self.mostrar_citas
            )
        ]

        for titulo, comando in opciones:

            boton = ctk.CTkButton(
                navegacion,
                text=titulo,
                height=40,
                fg_color=VERDE,
                hover_color=VERDE_OSCURO,
                text_color=PANEL,
                font=("Arial", 12, "bold"),
                corner_radius=8,
                command=comando
            )

            boton.pack(
                side="left",
                padx=(0, 10)
            )

            self.botones[titulo] = boton

        self.contenido = ctk.CTkScrollableFrame(
            self,
            fg_color=FONDO,
            corner_radius=0,
            scrollbar_button_color=BORDE,
            scrollbar_button_hover_color=VERDE
        )

        self.contenido.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20)
        )

    # ========================================================
    # FUNCIONES GENERALES
    # ========================================================

    def limpiar_contenido(self):

        for widget in self.contenido.winfo_children():
            widget.destroy()

    def crear_tarjeta(self, titulo):

        tarjeta = ctk.CTkFrame(
            self.contenido,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE
        )

        tarjeta.pack(
            fill="x",
            padx=5,
            pady=10
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=("Georgia", 21, "bold"),
            text_color=VERDE_OSCURO
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        return tarjeta

    def mostrar_campo(
        self,
        padre,
        etiqueta,
        valor
    ):

        if valor is None or valor == "":
            valor = "No registrado"

        ctk.CTkLabel(
            padre,
            text=f"{etiqueta}:",
            font=("Arial", 12, "bold"),
            text_color=VERDE_OSCURO
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0)
        )

        ctk.CTkLabel(
            padre,
            text=str(valor),
            font=("Arial", 12),
            text_color=TEXTO,
            wraplength=750,
            justify="left"
        ).pack(
            anchor="w",
            padx=20,
            pady=(2, 10)
        )

    def mostrar_error(self, error):

        print(
            "ERROR EN PANEL DE ODONTOLOGA:",
            error
        )

        if isinstance(error, PermissionError):
            mensaje = (
                "Tu cuenta no tiene autorizacion "
                "para realizar esta consulta."
            )
        else:
            mensaje = (
                "No se pudo consultar la informacion.\n"
                "Revisa la terminal de VS Code."
            )

        messagebox.showerror(
            "Sonrisa Sana",
            mensaje,
            parent=self.winfo_toplevel()
        )

    # ========================================================
    # MI PERFIL PROFESIONAL
    # ========================================================

    def mostrar_perfil(self):

        self.limpiar_contenido()

        tarjeta = self.crear_tarjeta(
            "MI PERFIL PROFESIONAL"
        )

        try:
            registros = self.consultar("""
                SELECT
                    IdOdontologa,
                    Nombre,
                    Apellidos,
                    Especialidad,
                    Telefono,
                    Correo
                FROM dbo.Odontologa
                WHERE IdOdontologa = ?
            """, (
                self.id_odontologa,
            ))

            if not registros:

                self.mostrar_campo(
                    tarjeta,
                    "Informacion",
                    "No se encontro el registro profesional."
                )

                return

            odontologa = registros[0]

            campos = [
                (
                    "ID de odontologa",
                    odontologa[0]
                ),
                (
                    "Nombre",
                    odontologa[1]
                ),
                (
                    "Apellidos",
                    odontologa[2]
                ),
                (
                    "Especialidad",
                    odontologa[3]
                ),
                (
                    "Telefono",
                    odontologa[4]
                ),
                (
                    "Correo electronico",
                    odontologa[5]
                )
            ]

            for etiqueta, valor in campos:

                self.mostrar_campo(
                    tarjeta,
                    etiqueta,
                    valor
                )

        except Exception as error:
            self.mostrar_error(error)

    # ========================================================
    # MIS CITAS ASIGNADAS
    # ========================================================

    def mostrar_citas(self):

        self.limpiar_contenido()

        tarjeta = self.crear_tarjeta(
            "MIS CITAS ASIGNADAS"
        )

        try:
            registros = self.consultar("""
                SELECT
                    c.IdCita,
                    c.FechaCita,
                    c.HoraCita,
                    p.Nombre,
                    p.Apellidos,
                    c.Motivo,
                    c.Estado
                FROM dbo.Cita AS c
                INNER JOIN dbo.Paciente AS p
                    ON c.IdPaciente = p.IdPaciente
                WHERE c.IdOdontologa = ?
                ORDER BY
                    c.FechaCita DESC,
                    c.HoraCita DESC,
                    c.IdCita DESC
            """, (
                self.id_odontologa,
            ))

            if not registros:

                self.mostrar_campo(
                    tarjeta,
                    "Informacion",
                    "No tienes citas asignadas."
                )

                return

            columnas = (
                "ID",
                "Fecha",
                "Hora",
                "Paciente",
                "Motivo",
                "Estado"
            )

            datos = []

            for fila in registros:

                nombre_paciente = (
                    f"{fila[3] or ''} "
                    f"{fila[4] or ''}"
                ).strip()

                datos.append((
                    fila[0],
                    str(fila[1] or ""),
                    str(fila[2] or ""),
                    nombre_paciente,
                    str(fila[5] or ""),
                    str(fila[6] or "")
                ))

            self.crear_tabla(
                tarjeta,
                columnas,
                datos
            )

        except Exception as error:
            self.mostrar_error(error)

    # ========================================================
    # TABLA DE RESULTADOS
    # ========================================================

    def crear_tabla(
        self,
        padre,
        columnas,
        registros
    ):

        contenedor = ctk.CTkFrame(
            padre,
            fg_color="transparent"
        )

        contenedor.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        estilo = ttk.Style()

        estilo.configure(
            "Odontologa.Treeview",
            rowheight=31,
            font=("Arial", 10),
            background="#FFFFFF",
            foreground=TEXTO,
            fieldbackground="#FFFFFF"
        )

        estilo.configure(
            "Odontologa.Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        estilo.map(
            "Odontologa.Treeview",
            background=[
                ("selected", SELECCION)
            ],
            foreground=[
                ("selected", TEXTO)
            ]
        )

        tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            height=12,
            style="Odontologa.Treeview"
        )

        anchos = {
            "ID": 65,
            "Fecha": 130,
            "Hora": 115,
            "Paciente": 240,
            "Motivo": 290,
            "Estado": 140
        }

        for columna in columnas:

            tabla.heading(
                columna,
                text=columna
            )

            tabla.column(
                columna,
                width=anchos.get(
                    columna,
                    150
                ),
                minwidth=80,
                anchor="w"
            )

        for registro in registros:

            tabla.insert(
                "",
                "end",
                values=registro
            )

        desplazamiento_vertical = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=tabla.yview
        )

        desplazamiento_horizontal = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
            command=tabla.xview
        )

        tabla.configure(
            yscrollcommand=desplazamiento_vertical.set,
            xscrollcommand=desplazamiento_horizontal.set
        )

        contenedor.grid_columnconfigure(
            0,
            weight=1
        )

        contenedor.grid_rowconfigure(
            0,
            weight=1
        )

        tabla.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        desplazamiento_vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        desplazamiento_horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )
