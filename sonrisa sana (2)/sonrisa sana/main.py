
import importlib
import traceback
import customtkinter as ctk

from tkinter import Canvas, messagebox
from conexion import conectar
from login import VentanaLogin


# ============================================================
# SONRISA SANA - CONFIGURACION VISUAL
# ============================================================

NEGRO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
PANEL_HOVER = "#D7F1ED"
DORADO = "#159F95"
DORADO_CLARO = "#087F78"
TEXTO = "#263B3A"
BLANCO = "#FFFFFF"
BORDE = "#B8DED8"
SELECCION = "#BFEDE6"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# MODULOS ADMINISTRATIVOS
# ============================================================

MODULOS = [
    (
        "♙", "Pacientes",
        "Registro y datos personales.",
        "pacientes", "PanelPacientes"
    ),
    (
        "▦", "Citas",
        "Agenda y reprogramacion.",
        "citas", "PanelCitas"
    ),
    (
        "✚", "Tratamientos",
        "Seguimiento y sesiones.",
        "tratamientos", "PanelTratamientos"
    ),
    (
        "✧", "Procedimientos",
        "Catalogo y costos dentales.",
        "procedimientos", "PanelProcedimientos"
    ),
    (
        "♙", "Odontologas",
        "Datos de las profesionales.",
        "odontologas", "PanelOdontologas"
    ),
    (
        "☎", "Telefonos",
        "Contactos de pacientes.",
        "telefonos", "PanelTelefonos"
    ),
    (
        "▦", "Calendario de citas",
        "Consulta los dias ocupados y las proximas atenciones.",
        "calendario", "PanelCalendario"
    ),
    (
        "♙", "Usuarios",
        "Administracion de cuentas y accesos.",
        "usuarios", "PanelUsuarios"
    )
]


# ============================================================
# VENTANA PRINCIPAL DE LA RECEPCIONISTA
# ============================================================

class SistemaSonrisaSana(ctk.CTkToplevel):

    def __init__(self, login, usuario):
        super().__init__(login)

        self.login = login
        self.usuario = usuario
        self.panel_actual = None
        self.boton_actual = None
        self.botones_modulos = {}

        self.withdraw()

        if usuario.get("rol") != "Recepcionista":
            self.destroy()
            raise PermissionError(
                "Acceso exclusivo para recepcionista."
            )

        self.title(
            "Sonrisa Sana | Sistema de Gestion Dental"
        )
        self.geometry("1450x880")
        self.minsize(1100, 700)
        self.configure(fg_color=NEGRO)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_sesion
        )

        self.crear_encabezado()
        self.crear_estructura()
        self.crear_menu()
        self.mostrar_inicio()

        self.deiconify()
        self.lift()
        self.focus_force()

    # ========================================================
    # ENCABEZADO
    # ========================================================

    def crear_encabezado(self):

        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=15,
            border_width=1,
            border_color=DORADO
        )
        encabezado.pack(
            fill="x",
            padx=22,
            pady=(18, 14)
        )

        logo = ctk.CTkFrame(
            encabezado,
            fg_color=NEGRO,
            corner_radius=13,
            border_width=1,
            border_color=BORDE,
            width=82,
            height=82
        )
        logo.pack(
            side="left",
            padx=(18, 14),
            pady=12
        )
        logo.pack_propagate(False)

        diente = Canvas(
            logo,
            width=82,
            height=82,
            bg=NEGRO,
            highlightthickness=0,
            bd=0
        )
        diente.pack(
            fill="both",
            expand=True
        )

        diente.create_polygon(
            19, 24, 23, 17, 31, 14, 38, 17,
            41, 20, 45, 17, 52, 14, 60, 17,
            64, 24, 64, 32, 60, 41, 56, 51,
            52, 62, 48, 67, 44, 65, 41, 54,
            38, 48, 35, 54, 32, 65, 28, 67,
            24, 62, 20, 51, 16, 41, 12, 32,
            13, 27,
            fill=BLANCO,
            outline=BORDE,
            width=1,
            smooth=True
        )

        marca = ctk.CTkFrame(
            encabezado,
            fg_color="transparent"
        )
        marca.pack(
            side="left",
            fill="y",
            pady=15
        )

        ctk.CTkLabel(
            marca,
            text="SONRISA SANA",
            font=("Georgia", 30, "bold"),
            text_color=DORADO
        ).pack(anchor="w")

        ctk.CTkLabel(
            marca,
            text="Sistema integral de gestion dental",
            font=("Arial", 13),
            text_color=DORADO_CLARO
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        sesion = ctk.CTkFrame(
            encabezado,
            fg_color="transparent"
        )
        sesion.pack(
            side="right",
            padx=20,
            pady=12
        )

        ctk.CTkLabel(
            sesion,
            text="CONSULTORIO DENTAL",
            font=("Arial", 11, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="e")

        ctk.CTkLabel(
            sesion,
            text=(
                f"Usuario: "
                f"{self.usuario['nombre_usuario']}"
            ),
            font=("Arial", 12, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="e",
            pady=(5, 0)
        )

        ctk.CTkLabel(
            sesion,
            text=f"Rol: {self.usuario['rol']}",
            font=("Arial", 11),
            text_color=DORADO
        ).pack(anchor="e")

        ctk.CTkFrame(
            self,
            height=2,
            fg_color=DORADO
        ).pack(
            fill="x",
            padx=22,
            pady=(0, 14)
        )

    # ========================================================
    # ESTRUCTURA
    # ========================================================

    def crear_estructura(self):

        self.cuerpo = ctk.CTkFrame(
            self,
            fg_color=NEGRO,
            corner_radius=0
        )
        self.cuerpo.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(0, 8)
        )

        self.cuerpo.grid_columnconfigure(0, weight=0)
        self.cuerpo.grid_columnconfigure(1, weight=1)
        self.cuerpo.grid_rowconfigure(0, weight=1)

        self.menu = ctk.CTkFrame(
            self.cuerpo,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE,
            width=250
        )
        self.menu.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 16)
        )
        self.menu.grid_propagate(False)

        self.area_trabajo = ctk.CTkFrame(
            self.cuerpo,
            fg_color=NEGRO,
            corner_radius=0
        )
        self.area_trabajo.grid(
            row=0,
            column=1,
            sticky="nsew"
        )
        self.area_trabajo.grid_columnconfigure(
            0,
            weight=1
        )
        self.area_trabajo.grid_rowconfigure(
            0,
            weight=1
        )

    # ========================================================
    # MENU LATERAL
    # ========================================================

    def crear_menu(self):

        ctk.CTkLabel(
            self.menu,
            text="MENU PRINCIPAL",
            font=("Arial", 13, "bold"),
            text_color=DORADO
        ).pack(
            anchor="w",
            padx=18,
            pady=(22, 16)
        )

        self.boton_inicio = ctk.CTkButton(
            self.menu,
            text="⌂   Inicio",
            height=40,
            anchor="w",
            corner_radius=8,
            fg_color=SELECCION,
            hover_color=PANEL_HOVER,
            text_color=TEXTO,
            font=("Arial", 12, "bold"),
            command=self.mostrar_inicio
        )
        self.boton_inicio.pack(
            fill="x",
            padx=11,
            pady=3
        )

        self.boton_actual = self.boton_inicio

        for simbolo, titulo, descripcion, nombre, clase in MODULOS:

            if nombre == "calendario":
                continue

            boton = ctk.CTkButton(
                self.menu,
                text=f"{simbolo}   {titulo}",
                height=40,
                anchor="w",
                corner_radius=8,
                fg_color=PANEL,
                hover_color=PANEL_HOVER,
                text_color=DORADO_CLARO,
                border_width=1,
                border_color=BORDE,
                font=("Arial", 12, "bold"),
                command=lambda n=nombre, t=titulo:
                    self.abrir_panel(
                        n,
                        t,
                        self.botones_modulos[n]
                    )
            )

            boton.pack(
                fill="x",
                padx=11,
                pady=3
            )

            self.botones_modulos[nombre] = boton

        ctk.CTkButton(
            self.menu,
            text="⏻   Cerrar sesion",
            height=42,
            anchor="w",
            corner_radius=8,
            fg_color="#FFF0F0",
            hover_color="#F8DADA",
            text_color="#B33A3A",
            border_width=1,
            border_color="#E5B5B5",
            font=("Arial", 12, "bold"),
            command=self.cerrar_sesion
        ).pack(
            side="bottom",
            fill="x",
            padx=11,
            pady=(4, 12)
        )

        self.boton_calendario = ctk.CTkButton(
            self.menu,
            text="▦   Calendario de citas",
            height=42,
            anchor="w",
            corner_radius=8,
            fg_color=PANEL,
            hover_color=PANEL_HOVER,
            text_color=DORADO_CLARO,
            border_width=1,
            border_color=DORADO,
            font=("Arial", 12, "bold"),
            command=lambda: self.abrir_panel(
                "calendario",
                "Calendario de citas",
                self.boton_calendario
            )
        )
        self.boton_calendario.pack(
            side="bottom",
            fill="x",
            padx=11,
            pady=(8, 4)
        )

        self.botones_modulos[
            "calendario"
        ] = self.boton_calendario

        ctk.CTkFrame(
            self.menu,
            height=1,
            fg_color=BORDE
        ).pack(
            fill="x",
            padx=15,
            pady=(12, 8)
        )

        ctk.CTkLabel(
            self.menu,
            text="SONRISA SANA",
            font=("Georgia", 14, "bold"),
            text_color=DORADO
        ).pack(
            anchor="w",
            padx=18,
            pady=(3, 3)
        )

        ctk.CTkLabel(
            self.menu,
            text="Gestion dental",
            font=("Arial", 11),
            text_color=DORADO_CLARO
        ).pack(
            anchor="w",
            padx=18
        )

    # ========================================================
    # NAVEGACION
    # ========================================================

    def limpiar_area(self):

        for widget in self.area_trabajo.winfo_children():
            widget.destroy()

        self.panel_actual = None

    def actualizar_boton(self, boton):

        if self.boton_actual is not None:
            try:
                self.boton_actual.configure(
                    fg_color=PANEL,
                    text_color=DORADO_CLARO
                )
            except Exception:
                pass

        if boton is not None:
            boton.configure(
                fg_color=SELECCION,
                text_color=TEXTO
            )

        self.boton_actual = boton

    # ========================================================
    # ABRIR MODULOS ADMINISTRATIVOS
    # ========================================================

    def abrir_panel(self, nombre, titulo, boton=None):

        if self.usuario.get("rol") != "Recepcionista":
            messagebox.showerror(
                "Acceso denegado",
                "No tienes permisos para abrir este modulo.",
                parent=self
            )
            return

        definiciones = {
            modulo[3]: modulo[4]
            for modulo in MODULOS
        }

        if nombre not in definiciones:
            messagebox.showerror(
                "Sonrisa Sana",
                "El modulo solicitado no existe.",
                parent=self
            )
            return

        self.limpiar_area()
        self.actualizar_boton(boton)

        try:
            modulo = importlib.import_module(nombre)

            clase = getattr(
                modulo,
                definiciones[nombre]
            )

            if nombre == "usuarios":
                self.panel_actual = clase(
                    self.area_trabajo,
                    usuario_actual=self.usuario
                )
            else:
                self.panel_actual = clase(
                    self.area_trabajo
                )

            self.panel_actual.pack(
                fill="both",
                expand=True
            )

        except Exception as error:

            self.limpiar_area()

            tarjeta_error = ctk.CTkFrame(
                self.area_trabajo,
                fg_color=PANEL,
                border_color="#D99A9A",
                border_width=1,
                corner_radius=14
            )
            tarjeta_error.pack(
                fill="x",
                padx=20,
                pady=30
            )

            ctk.CTkLabel(
                tarjeta_error,
                text=f"No se pudo abrir {titulo}",
                font=("Georgia", 22, "bold"),
                text_color="#B33A3A"
            ).pack(
                anchor="w",
                padx=22,
                pady=(20, 8)
            )

            ctk.CTkLabel(
                tarjeta_error,
                text=(
                    f"{error}\n\n"
                    "Revisa la terminal de VS Code."
                ),
                font=("Arial", 12),
                text_color=TEXTO,
                wraplength=650,
                justify="left"
            ).pack(
                anchor="w",
                padx=22,
                pady=(0, 20)
            )

            print(
                f"\nERROR AL ABRIR {titulo.upper()}:"
            )
            traceback.print_exc()

    # ========================================================
    # PANTALLA DE INICIO
    # ========================================================

    def mostrar_inicio(self):

        self.limpiar_area()
        self.actualizar_boton(
            self.boton_inicio
        )

        contenido = ctk.CTkScrollableFrame(
            self.area_trabajo,
            fg_color=NEGRO,
            corner_radius=0,
            scrollbar_button_color=BORDE,
            scrollbar_button_hover_color=DORADO
        )
        contenido.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        contenido.grid_columnconfigure(
            0,
            weight=1
        )

        bienvenida = ctk.CTkFrame(
            contenido,
            fg_color=PANEL,
            corner_radius=14,
            border_width=1,
            border_color=DORADO
        )
        bienvenida.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=5,
            pady=(5, 14)
        )

        ctk.CTkLabel(
            bienvenida,
            text="BIENVENIDO A SONRISA SANA",
            font=("Georgia", 27, "bold"),
            text_color=DORADO_CLARO
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 5)
        )

        ctk.CTkLabel(
            bienvenida,
            text=(
                "Administra pacientes, agenda citas y da "
                "seguimiento a los tratamientos desde "
                "un solo lugar."
            ),
            font=("Arial", 12),
            text_color=TEXTO,
            wraplength=750,
            justify="left"
        ).pack(
            anchor="w",
            padx=23,
            pady=(0, 17)
        )

        ctk.CTkLabel(
            bienvenida,
            text=(
                "✦  ORGANIZACION  •  CONTROL  "
                "•  ATENCION DENTAL"
            ),
            font=("Arial", 10, "bold"),
            text_color=DORADO
        ).pack(
            anchor="w",
            padx=23,
            pady=(0, 17)
        )

        ctk.CTkLabel(
            contenido,
            text="RESUMEN DEL CONSULTORIO",
            font=("Arial", 12, "bold"),
            text_color=DORADO
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=8,
            pady=(2, 8)
        )

        estadisticas = self.obtener_estadisticas()

        contenedor_stats = ctk.CTkFrame(
            contenido,
            fg_color="transparent"
        )
        contenedor_stats.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=3,
            pady=(0, 17)
        )

        for columna in range(4):
            contenedor_stats.grid_columnconfigure(
                columna,
                weight=1,
                uniform="estadisticas"
            )

        definiciones_stats = [
            ("Pacientes", "♙"),
            ("Citas", "▦"),
            ("Tratamientos", "✚"),
            ("Procedimientos", "✧")
        ]

        for columna, (titulo, simbolo) in enumerate(
            definiciones_stats
        ):

            tarjeta = self.crear_tarjeta_estadistica(
                contenedor_stats,
                titulo,
                estadisticas[titulo],
                simbolo
            )

            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=4
            )

        if all(
            valor is None
            for valor in estadisticas.values()
        ):
            ctk.CTkLabel(
                contenido,
                text=(
                    "No se pudieron consultar los indicadores. "
                    "Comprueba la conexion a la base de datos."
                ),
                font=("Arial", 10),
                text_color=DORADO_CLARO
            ).grid(
                row=3,
                column=0,
                sticky="w",
                padx=8,
                pady=(0, 12)
            )

        ctk.CTkLabel(
            contenido,
            text="ACCESO A LOS MODULOS",
            font=("Arial", 12, "bold"),
            text_color=DORADO
        ).grid(
            row=4,
            column=0,
            sticky="w",
            padx=8,
            pady=(0, 8)
        )

        accesos = ctk.CTkFrame(
            contenido,
            fg_color="transparent"
        )
        accesos.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=3,
            pady=(0, 12)
        )

        for columna in range(3):
            accesos.grid_columnconfigure(
                columna,
                weight=1,
                uniform="modulos"
            )

        for indice, (
            simbolo,
            titulo,
            descripcion,
            nombre,
            clase
        ) in enumerate(MODULOS):

            tarjeta = self.crear_tarjeta_modulo(
                accesos,
                simbolo,
                titulo,
                descripcion,
                nombre
            )

            tarjeta.grid(
                row=indice // 3,
                column=indice % 3,
                sticky="nsew",
                padx=4,
                pady=4
            )

        ctk.CTkLabel(
            contenido,
            text=(
                "SONRISA SANA  |  Una sonrisa saludable "
                "comienza con una buena organizacion."
            ),
            font=("Arial", 10),
            text_color=DORADO_CLARO
        ).grid(
            row=6,
            column=0,
            sticky="w",
            padx=8,
            pady=(3, 15)
        )

    # ========================================================
    # ESTADISTICAS DE SQL SERVER
    # ========================================================

    def obtener_estadisticas(self):

        estadisticas = {
            "Pacientes": None,
            "Citas": None,
            "Tratamientos": None,
            "Procedimientos": None
        }

        consultas = {
            "Pacientes":
                "SELECT COUNT(*) FROM dbo.Paciente",
            "Citas":
                "SELECT COUNT(*) FROM dbo.Cita",
            "Tratamientos":
                "SELECT COUNT(*) FROM dbo.Tratamiento",
            "Procedimientos":
                "SELECT COUNT(*) FROM dbo.Procedimiento"
        }

        conexion_db = None

        try:
            conexion_db = conectar()
            cursor = conexion_db.cursor()

            for nombre, consulta in consultas.items():
                cursor.execute(consulta)
                resultado = cursor.fetchone()

                estadisticas[nombre] = int(
                    resultado[0]
                )

        except Exception as error:
            print(
                "No se pudieron cargar las estadisticas:",
                error
            )

        finally:
            if conexion_db is not None:
                conexion_db.close()

        return estadisticas

    # ========================================================
    # TARJETAS DE ESTADISTICAS
    # ========================================================

    def crear_tarjeta_estadistica(
        self,
        padre,
        titulo,
        valor,
        simbolo
    ):

        tarjeta = ctk.CTkFrame(
            padre,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDE
        )
        tarjeta.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            tarjeta,
            text=simbolo,
            font=("Georgia", 23, "bold"),
            text_color=DORADO
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 0)
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo.upper(),
            font=("Arial", 10, "bold"),
            text_color=DORADO_CLARO
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=15,
            pady=(6, 0)
        )

        ctk.CTkLabel(
            tarjeta,
            text=(
                str(valor)
                if valor is not None
                else "—"
            ),
            font=("Georgia", 27, "bold"),
            text_color=TEXTO
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=15,
            pady=(3, 13)
        )

        return tarjeta

    # ========================================================
    # TARJETAS DE MODULOS
    # ========================================================

    def crear_tarjeta_modulo(
        self,
        padre,
        simbolo,
        titulo,
        descripcion,
        nombre
    ):

        tarjeta = ctk.CTkFrame(
            padre,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDE
        )
        tarjeta.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            tarjeta,
            text=simbolo,
            font=("Georgia", 25, "bold"),
            text_color=DORADO
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=16,
            pady=(13, 0)
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=("Arial", 14, "bold"),
            text_color=DORADO_CLARO
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=16,
            pady=(6, 3)
        )

        ctk.CTkLabel(
            tarjeta,
            text=descripcion,
            font=("Arial", 11),
            text_color=TEXTO,
            wraplength=230,
            justify="left"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=16,
            pady=(0, 9)
        )

        ctk.CTkButton(
            tarjeta,
            text="Abrir modulo  →",
            height=32,
            corner_radius=7,
            fg_color=PANEL_CLARO,
            hover_color=BORDE,
            text_color=DORADO_CLARO,
            border_color=BORDE,
            border_width=1,
            font=("Arial", 11, "bold"),
            command=lambda n=nombre, t=titulo:
                self.abrir_panel(
                    n,
                    t,
                    self.botones_modulos[n]
                )
        ).grid(
            row=3,
            column=0,
            sticky="ew",
            padx=13,
            pady=(0, 13)
        )

        return tarjeta

    # ========================================================
    # CERRAR SESION DE RECEPCIONISTA
    # ========================================================

    def cerrar_sesion(self):

        confirmar = messagebox.askyesno(
            "Sonrisa Sana",
            "¿Deseas cerrar la sesion actual?",
            parent=self
        )

        if not confirmar:
            return

        self.login.usuario_autenticado = None

        self.destroy()

        self.login.regresar_login()


# ============================================================
# VENTANA EXCLUSIVA PARA PACIENTES
# ============================================================

class VentanaPaciente(ctk.CTkToplevel):

    def __init__(self, login, usuario):
        super().__init__(login)

        self.login = login
        self.usuario = usuario

        self.withdraw()

        if (
            usuario.get("rol") != "Paciente"
            or usuario.get("id_paciente") is None
            or usuario.get("id_usuario") is None
        ):
            self.destroy()
            raise PermissionError(
                "Cuenta de paciente no valida."
            )

        self.title(
            "Sonrisa Sana | Portal del Paciente"
        )
        self.geometry("1150x760")
        self.minsize(850, 550)
        self.configure(fg_color=NEGRO)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_sesion
        )

        # ENCABEZADO DEL PACIENTE

        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE
        )
        encabezado.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            encabezado,
            text="SONRISA SANA | PORTAL DEL PACIENTE",
            font=("Georgia", 23, "bold"),
            text_color=DORADO_CLARO
        ).pack(
            side="left",
            padx=18,
            pady=18
        )

        ctk.CTkButton(
            encabezado,
            text="Cerrar sesion",
            width=145,
            fg_color="#B33A3A",
            hover_color="#922B2B",
            command=self.cerrar_sesion
        ).pack(
            side="right",
            padx=18,
            pady=15
        )

        ctk.CTkLabel(
            self,
            text=(
                f"Usuario: "
                f"{usuario.get('nombre_usuario', '')}"
            ),
            text_color=TEXTO,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 4)
        )

        # CARGAR UNICAMENTE EL MODULO DEL PACIENTE

        from panel_paciente import PanelPaciente

        self.panel = PanelPaciente(
            self,
            usuario=usuario
        )
        self.panel.pack(
            fill="both",
            expand=True
        )

        self.deiconify()
        self.lift()
        self.focus_force()

    # ========================================================
    # CERRAR SESION DEL PACIENTE
    # ========================================================

    def cerrar_sesion(self):

        confirmar = messagebox.askyesno(
            "Sonrisa Sana",
            "¿Deseas cerrar la sesion actual?",
            parent=self
        )

        if not confirmar:
            return

        self.login.usuario_autenticado = None

        self.destroy()

        self.login.regresar_login()



# ============================================================
# VENTANA EXCLUSIVA PARA ODONTOLOGAS
# ============================================================

class VentanaOdontologa(ctk.CTkToplevel):

    def __init__(self, login, usuario):
        super().__init__(login)

        self.login = login
        self.usuario = usuario

        self.withdraw()

        # ====================================================
        # VALIDACION DEL ROL Y LA CUENTA
        # ====================================================

        if (
            not isinstance(usuario, dict)
            or usuario.get("rol") != "Odontologa"
            or usuario.get("id_odontologa") is None
            or usuario.get("id_usuario") is None
        ):
            self.destroy()
            raise PermissionError(
                "Cuenta de odontologa no valida."
            )

        # ====================================================
        # CONFIGURACION DE LA VENTANA
        # ====================================================

        self.title(
            "Sonrisa Sana | Portal de la Odontologa"
        )

        self.geometry("1150x760")
        self.minsize(850, 550)

        self.configure(fg_color=NEGRO)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_sesion
        )

        # ====================================================
        # ENCABEZADO
        # ====================================================

        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=BORDE
        )

        encabezado.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            encabezado,
            text="SONRISA SANA | PORTAL DE LA ODONTOLOGA",
            font=("Georgia", 23, "bold"),
            text_color=DORADO_CLARO
        ).pack(
            side="left",
            padx=18,
            pady=18
        )

        ctk.CTkButton(
            encabezado,
            text="Cerrar sesion",
            width=145,
            fg_color="#B33A3A",
            hover_color="#922B2B",
            command=self.cerrar_sesion
        ).pack(
            side="right",
            padx=18,
            pady=15
        )

        # ====================================================
        # INFORMACION DE LA SESION
        # ====================================================

        ctk.CTkLabel(
            self,
            text=(
                f"Usuario: "
                f"{usuario.get('nombre_usuario', '')}"
            ),
            text_color=TEXTO,
            font=("Arial", 12)
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 4)
        )

        # ====================================================
        # CARGAR PANEL EXCLUSIVO DE LA ODONTOLOGA
        # ====================================================

        from panel_odontologa import PanelOdontologa

        self.panel = PanelOdontologa(
            self,
            usuario=usuario
        )

        self.panel.pack(
            fill="both",
            expand=True
        )

        self.deiconify()
        self.lift()
        self.focus_force()

    # ========================================================
    # CERRAR SESION DE ODONTOLOGA
    # ========================================================

    def cerrar_sesion(self):

        confirmar = messagebox.askyesno(
            "Sonrisa Sana",
            "¿Deseas cerrar la sesion actual?",
            parent=self
        )

        if not confirmar:
            return

        self.login.usuario_autenticado = None

        self.destroy()

        self.login.regresar_login()


# ============================================================
# INICIO GENERAL DE LA APLICACION
# ============================================================

def iniciar_aplicacion():

    login = VentanaLogin()

    ventana_sistema = None

    def abrir_sistema(usuario):

        nonlocal ventana_sistema

        if not isinstance(usuario, dict):
            messagebox.showerror(
                "Sonrisa Sana",
                "La informacion de la sesion no es valida.",
                parent=login
            )

            login.regresar_login()
            return

        rol = usuario.get("rol")

        try:

            # ================================================
            # ROL: RECEPCIONISTA
            # ================================================

            if rol == "Recepcionista":

                ventana_sistema = SistemaSonrisaSana(
                    login,
                    usuario
                )

            # ================================================
            # ROL: PACIENTE
            # ================================================

            elif rol == "Paciente":

                ventana_sistema = VentanaPaciente(
                    login,
                    usuario
                )

            # ================================================
            # ROL: ODONTOLOGA
            # ================================================

            elif rol == "Odontologa":

                ventana_sistema = VentanaOdontologa(
                    login,
                    usuario
                )

            # ================================================
            # ROL NO AUTORIZADO
            # ================================================

            else:

                messagebox.showerror(
                    "Acceso denegado",
                    "Tu cuenta no tiene un rol autorizado.",
                    parent=login
                )

                login.regresar_login()

        except Exception as error:

            print(
                "ERROR AL ABRIR LA INTERFAZ:",
                error
            )

            traceback.print_exc()

            messagebox.showerror(
                "Sonrisa Sana",
                "No se pudo abrir la interfaz. "
                "Revisa la terminal de VS Code.",
                parent=login
            )

            login.regresar_login()

    # ========================================================
    # CONECTAR LOGIN CON LA INTERFAZ CORRESPONDIENTE
    # ========================================================

    login.al_iniciar_sesion = abrir_sistema

    login.mainloop()


# ============================================================
# EJECUTAR SONRISA SANA
# ============================================================

if __name__ == "__main__":
    iniciar_aplicacion()

