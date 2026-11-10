
import customtkinter as ctk

from tkinter import ttk, messagebox
from conexion import conectar


# ============================================================
# SONRISA SANA - PANEL EXCLUSIVO PARA PACIENTES
# ============================================================

FONDO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
VERDE = "#159F95"
VERDE_OSCURO = "#087F78"
TEXTO = "#263B3A"
BORDE = "#B8DED8"


class PanelPaciente(ctk.CTkFrame):

    def __init__(self, master, usuario):
        super().__init__(
            master,
            fg_color=FONDO,
            corner_radius=0
        )

        if not isinstance(usuario, dict):
            raise PermissionError(
                "No existe una sesion valida."
            )

        if usuario.get("rol") != "Paciente":
            raise PermissionError(
                "Acceso exclusivo para pacientes."
            )

        self.id_usuario = usuario.get("id_usuario")
        self.id_paciente = usuario.get("id_paciente")

        if self.id_usuario is None or self.id_paciente is None:
            raise PermissionError(
                "La cuenta no tiene un paciente asociado."
            )

        self.id_usuario = int(self.id_usuario)
        self.id_paciente = int(self.id_paciente)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.crear_interfaz()
        self.mostrar_perfil()

    # ========================================================
    # VALIDAR LA CUENTA EN SQL SERVER
    # ========================================================

    def validar_acceso(self, cursor):

        cursor.execute("""
            SELECT IdPaciente
            FROM dbo.UsuarioSistema
            WHERE IdUsuario = ?
              AND Rol = 'Paciente'
              AND IdPaciente = ?
              AND Activo = 1
        """, (
            self.id_usuario,
            self.id_paciente
        ))

        registro = cursor.fetchone()

        if registro is None:
            raise PermissionError(
                "La cuenta no esta activa o "
                "no tiene permiso para consultar "
                "este paciente."
            )

    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            border_width=1,
            border_color=BORDE,
            corner_radius=13
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
            text="MI ESPACIO DENTAL",
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
                "Consulta tu informacion personal, "
                "tus citas y tus tratamientos."
            ),
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
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
            ("Mi perfil", self.mostrar_perfil),
            ("Mis citas", self.mostrar_citas),
            ("Mis tratamientos", self.mostrar_tratamientos)
        ]

        for titulo, comando in opciones:

            boton = ctk.CTkButton(
                navegacion,
                text=titulo,
                height=40,
                fg_color=VERDE,
                hover_color=VERDE_OSCURO,
                font=("Arial", 12, "bold"),
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
            scrollbar_button_color=BORDE
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
            border_width=1,
            border_color=BORDE,
            corner_radius=13
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

    def mostrar_campo(self, padre, etiqueta, valor):

        if valor is None:
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
            wraplength=700,
            justify="left"
        ).pack(
            anchor="w",
            padx=20,
            pady=(2, 10)
        )

    def consultar(self, consulta, parametros):

        conexion = None

        try:
            conexion = conectar()
            cursor = conexion.cursor()

            self.validar_acceso(cursor)

            cursor.execute(
                consulta,
                parametros
            )

            return cursor.fetchall()

        finally:
            if conexion is not None:
                conexion.close()

    def mostrar_error(self, error):

        print(
            "ERROR EN PANEL DE PACIENTE:",
            error
        )

        messagebox.showerror(
            "Sonrisa Sana",
            "No se pudo consultar la informacion.\n"
            "Revisa la terminal de VS Code.",
            parent=self.winfo_toplevel()
        )

    # ========================================================
    # MI PERFIL
    # ========================================================

    def mostrar_perfil(self):

        self.limpiar_contenido()

        tarjeta = self.crear_tarjeta(
            "MI PERFIL"
        )

        try:
            registros = self.consultar("""
                SELECT
                    IdPaciente,
                    Nombre,
                    Apellidos,
                    FechaNacimiento,
                    TelefonoPrincipal,
                    Correo,
                    FechaRegistro
                FROM dbo.Paciente
                WHERE IdPaciente = ?
            """, (self.id_paciente,))

            if not registros:
                self.mostrar_campo(
                    tarjeta,
                    "Informacion",
                    "No se encontro el paciente."
                )
                return

            paciente = registros[0]

            campos = [
                ("ID del paciente", paciente[0]),
                ("Nombre", paciente[1]),
                ("Apellidos", paciente[2]),
                ("Fecha de nacimiento", paciente[3]),
                ("Telefono principal", paciente[4]),
                ("Correo electronico", paciente[5]),
                ("Fecha de registro", paciente[6])
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
    # MIS CITAS
    # ========================================================

    def mostrar_citas(self):

        self.limpiar_contenido()

        tarjeta = self.crear_tarjeta(
            "MIS CITAS"
        )

        try:
            registros = self.consultar("""
                SELECT
                    c.IdCita,
                    c.FechaCita,
                    c.HoraCita,
                    c.Motivo,
                    c.Estado,
                    o.Nombre,
                    o.Apellidos
                FROM dbo.Cita c
                LEFT JOIN dbo.Odontologa o
                    ON c.IdOdontologa = o.IdOdontologa
                WHERE c.IdPaciente = ?
                ORDER BY c.FechaCita DESC,
                         c.HoraCita DESC
            """, (self.id_paciente,))

            if not registros:
                self.mostrar_campo(
                    tarjeta,
                    "Informacion",
                    "No tienes citas registradas."
                )
                return

            columnas = (
                "ID",
                "Fecha",
                "Hora",
                "Motivo",
                "Estado",
                "Odontologa"
            )

            self.crear_tabla(
                tarjeta,
                columnas,
                [
                    (
                        fila[0],
                        str(fila[1]),
                        str(fila[2]),
                        str(fila[3] or ""),
                        str(fila[4] or ""),
                        (
                            f"{fila[5] or ''} "
                            f"{fila[6] or ''}"
                        ).strip()
                    )
                    for fila in registros
                ]
            )

        except Exception as error:
            self.mostrar_error(error)

    # ========================================================
    # MIS TRATAMIENTOS
    # ========================================================

    def mostrar_tratamientos(self):

        self.limpiar_contenido()

        tarjeta = self.crear_tarjeta(
            "MIS TRATAMIENTOS"
        )

        try:
            registros = self.consultar("""
                SELECT
                    IdTratamiento,
                    NombreTratamiento,
                    Descripcion,
                    FechaInicio,
                    FechaFin,
                    Estado
                FROM dbo.Tratamiento
                WHERE IdPaciente = ?
                ORDER BY FechaInicio DESC,
                         IdTratamiento DESC
            """, (self.id_paciente,))

            if not registros:
                self.mostrar_campo(
                    tarjeta,
                    "Informacion",
                    "No tienes tratamientos registrados."
                )
                return

            columnas = (
                "ID",
                "Tratamiento",
                "Descripcion",
                "Inicio",
                "Fin",
                "Estado"
            )

            self.crear_tabla(
                tarjeta,
                columnas,
                [
                    (
                        fila[0],
                        str(fila[1] or ""),
                        str(fila[2] or ""),
                        str(fila[3] or ""),
                        str(fila[4] or ""),
                        str(fila[5] or "")
                    )
                    for fila in registros
                ]
            )

        except Exception as error:
            self.mostrar_error(error)

    # ========================================================
    # TABLAS DE CONSULTA
    # ========================================================

    def crear_tabla(self, padre, columnas, registros):

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
            "Paciente.Treeview",
            rowheight=30,
            font=("Arial", 10)
        )
        estilo.configure(
            "Paciente.Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            height=10,
            style="Paciente.Treeview"
        )

        for columna in columnas:
            tabla.heading(
                columna,
                text=columna
            )

            tabla.column(
                columna,
                width=150,
                minwidth=100,
                anchor="w"
            )

        for registro in registros:
            tabla.insert(
                "",
                "end",
                values=registro
            )

        desplazamiento = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
            command=tabla.xview
        )

        tabla.configure(
            xscrollcommand=desplazamiento.set
        )

        tabla.pack(
            fill="both",
            expand=True
        )

        desplazamiento.pack(
            fill="x"
        )
