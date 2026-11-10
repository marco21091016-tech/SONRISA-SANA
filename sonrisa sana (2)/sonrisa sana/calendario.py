
import calendar
from datetime import date, datetime

import customtkinter as ctk
from tkinter import ttk, messagebox

from conexion import conectar


# ============================================================
# COLORES SONRISA SANA
# ============================================================

NEGRO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
PANEL_HOVER = "#D7F1ED"
DORADO = "#159F95"
DORADO_CLARO = "#087F78"
BLANCO = "#FFFFFF"
TEXTO = "#263B3A"
BORDE = "#B8DED8"
SELECCION = "#BFEDE6"

MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


# ============================================================
# CONSULTAS A SQL SERVER
# ============================================================

def obtener_citas_mes(anio, mes):
    """Devuelve las citas del mes indicado, incluyendo canceladas."""
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        inicio = date(anio, mes, 1)

        if mes == 12:
            fin = date(anio + 1, 1, 1)
        else:
            fin = date(anio, mes + 1, 1)

        cursor.execute(
            """
            SELECT
                c.IdCita,
                c.FechaCita,
                c.HoraCita,
                p.Nombre + ' ' + p.Apellidos AS Paciente,
                o.Nombre + ' ' + o.Apellidos AS Odontologa,
                c.Motivo,
                c.Estado,
                c.CanalSolicitud
            FROM dbo.Cita AS c
            INNER JOIN dbo.Paciente AS p
                ON p.IdPaciente = c.IdPaciente
            INNER JOIN dbo.Odontologa AS o
                ON o.IdOdontologa = c.IdOdontologa
            WHERE c.FechaCita >= ?
              AND c.FechaCita < ?
            ORDER BY c.FechaCita, c.HoraCita
            """,
            inicio,
            fin
        )

        return cursor.fetchall()

    finally:
        if conexion is not None:
            conexion.close()


def obtener_proximas_citas(limite=15):
    """Devuelve las próximas citas vigentes desde hoy."""
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT TOP (?)
                c.IdCita,
                c.FechaCita,
                c.HoraCita,
                p.Nombre + ' ' + p.Apellidos AS Paciente,
                o.Nombre + ' ' + o.Apellidos AS Odontologa,
                c.Motivo,
                c.Estado
            FROM dbo.Cita AS c
            INNER JOIN dbo.Paciente AS p
                ON p.IdPaciente = c.IdPaciente
            INNER JOIN dbo.Odontologa AS o
                ON o.IdOdontologa = c.IdOdontologa
            WHERE c.FechaCita >= CAST(GETDATE() AS DATE)
              AND c.Estado <> N'Cancelada'
            ORDER BY c.FechaCita, c.HoraCita
            """,
            limite
        )

        return cursor.fetchall()

    finally:
        if conexion is not None:
            conexion.close()


# ============================================================
# FORMATO DE FECHA Y HORA
# ============================================================

def fecha_a_date(valor):
    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    return date.fromisoformat(str(valor)[:10])


def hora_a_texto(valor):
    if valor is None:
        return ""

    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M")

    return str(valor)[:5]


# ============================================================
# PANEL DEL CALENDARIO
# ============================================================

class PanelCalendario(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=NEGRO, corner_radius=0)

        hoy = date.today()

        self.anio = hoy.year
        self.mes = hoy.month
        self.fecha_seleccionada = hoy
        self.citas_mes = []
        self.botones_dias = {}

        self._crear_interfaz()
        self.actualizar_calendario()

    # --------------------------------------------------------
    # INTERFAZ PRINCIPAL
    # --------------------------------------------------------

    def _crear_interfaz(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=13,
            border_width=1,
            border_color=DORADO
        )
        encabezado.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=5,
            pady=(5, 12)
        )

        ctk.CTkLabel(
            encabezado,
            text="CALENDARIO DE CITAS",
            font=("Georgia", 25, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=20, pady=(17, 4))

        ctk.CTkLabel(
            encabezado,
            text=(
                "Consulta las citas programadas, selecciona un día "
                "y revisa las próximas atenciones."
            ),
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=21, pady=(0, 16))

        # Panel izquierdo: calendario mensual
        self.panel_mes = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDE
        )
        self.panel_mes.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(5, 6),
            pady=(0, 8)
        )

        for columna in range(7):
            self.panel_mes.grid_columnconfigure(columna, weight=1)

        navegacion = ctk.CTkFrame(
            self.panel_mes,
            fg_color="transparent"
        )
        navegacion.grid(
            row=0,
            column=0,
            columnspan=7,
            sticky="ew",
            padx=12,
            pady=(12, 14)
        )

        navegacion.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            navegacion,
            text="‹",
            width=42,
            height=35,
            fg_color=PANEL_CLARO,
            hover_color=BORDE,
            text_color=DORADO_CLARO,
            border_width=1,
            border_color=BORDE,
            font=("Arial", 22, "bold"),
            command=lambda: self.cambiar_mes(-1)
        ).grid(row=0, column=0, padx=(0, 8))

        self.etiqueta_mes = ctk.CTkLabel(
            navegacion,
            text="",
            font=("Georgia", 19, "bold"),
            text_color=DORADO
        )
        self.etiqueta_mes.grid(row=0, column=1)

        ctk.CTkButton(
            navegacion,
            text="›",
            width=42,
            height=35,
            fg_color=PANEL_CLARO,
            hover_color=BORDE,
            text_color=DORADO_CLARO,
            border_width=1,
            border_color=BORDE,
            font=("Arial", 22, "bold"),
            command=lambda: self.cambiar_mes(1)
        ).grid(row=0, column=2, padx=(8, 0))

        self.boton_hoy = ctk.CTkButton(
            self.panel_mes,
            text="Ir a hoy",
            height=31,
            fg_color=BORDE,
            hover_color="#0E8F85",
            text_color=TEXTO,
            font=("Arial", 11, "bold"),
            command=self.ir_a_hoy
        )
        self.boton_hoy.grid(
            row=1,
            column=0,
            columnspan=7,
            sticky="ew",
            padx=12,
            pady=(0, 10)
        )

        for columna, dia in enumerate(DIAS_SEMANA):
            ctk.CTkLabel(
                self.panel_mes,
                text=dia,
                font=("Arial", 11, "bold"),
                text_color=DORADO_CLARO
            ).grid(
                row=2,
                column=columna,
                sticky="ew",
                padx=2,
                pady=(4, 7)
            )

        self.marco_dias = ctk.CTkFrame(
            self.panel_mes,
            fg_color="transparent"
        )
        self.marco_dias.grid(
            row=3,
            column=0,
            columnspan=7,
            sticky="nsew",
            padx=9,
            pady=(0, 8)
        )

        for columna in range(7):
            self.marco_dias.grid_columnconfigure(
                columna,
                weight=1,
                uniform="dia"
            )

        for fila in range(6):
            self.marco_dias.grid_rowconfigure(
                fila,
                weight=1,
                uniform="semana"
            )

        self.panel_mes.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self.panel_mes,
            text="● Día con citas     Hoy: borde turquesa",
            font=("Arial", 10),
            text_color=DORADO_CLARO
        ).grid(
            row=4,
            column=0,
            columnspan=7,
            sticky="w",
            padx=15,
            pady=(4, 13)
        )

        # Panel derecho: detalle del día y próximas citas
        self.panel_detalle = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDE
        )
        self.panel_detalle.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(6, 5),
            pady=(0, 8)
        )

        self.panel_detalle.grid_columnconfigure(0, weight=1)
        self.panel_detalle.grid_rowconfigure(2, weight=1)
        self.panel_detalle.grid_rowconfigure(5, weight=1)

        self.etiqueta_seleccion = ctk.CTkLabel(
            self.panel_detalle,
            text="CITAS DEL DÍA",
            font=("Georgia", 17, "bold"),
            text_color=DORADO_CLARO
        )
        self.etiqueta_seleccion.grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(15, 3)
        )

        self.etiqueta_total = ctk.CTkLabel(
            self.panel_detalle,
            text="Selecciona un día del calendario.",
            font=("Arial", 11),
            text_color=TEXTO
        )
        self.etiqueta_total.grid(
            row=1,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 8)
        )

        self.tabla_dia = self._crear_tabla(
            self.panel_detalle,
            ("hora", "paciente", "estado"),
            ("Hora", "Paciente", "Estado"),
            (65, 150, 100)
        )
        self.tabla_dia.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            self.panel_detalle,
            text="PRÓXIMAS CITAS",
            font=("Georgia", 16, "bold"),
            text_color=DORADO_CLARO
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=15,
            pady=(3, 4)
        )

        ctk.CTkLabel(
            self.panel_detalle,
            text="Próximas atenciones no canceladas.",
            font=("Arial", 10),
            text_color=TEXTO
        ).grid(
            row=4,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 7)
        )

        self.tabla_proximas = self._crear_tabla(
            self.panel_detalle,
            ("fecha", "hora", "paciente", "estado"),
            ("Fecha", "Hora", "Paciente", "Estado"),
            (85, 55, 135, 90)
        )
        self.tabla_proximas.grid(
            row=5,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        pie = ctk.CTkFrame(
            self.panel_detalle,
            fg_color="transparent"
        )
        pie.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 10)
        )

        ctk.CTkButton(
            pie,
            text="Actualizar citas",
            height=34,
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color="#000000",
            font=("Arial", 11, "bold"),
            command=self.actualizar_calendario
        ).pack(fill="x")

    # --------------------------------------------------------
    # TABLAS
    # --------------------------------------------------------

    def _crear_tabla(self, padre, columnas, titulos, anchos):
        marco = ctk.CTkFrame(
            padre,
            fg_color=PANEL_CLARO,
            corner_radius=8,
            border_width=1,
            border_color=BORDE
        )

        estilo = ttk.Style()

        estilo.configure(
            "Calendario.Treeview",
            background=PANEL_CLARO,
            foreground=TEXTO,
            fieldbackground=PANEL_CLARO,
            rowheight=29,
            borderwidth=0,
            font=("Arial", 9)
        )

        estilo.configure(
            "Calendario.Treeview.Heading",
            background="#DDF3EF",
            foreground=DORADO_CLARO,
            font=("Arial", 9, "bold"),
            relief="flat"
        )

        estilo.map(
            "Calendario.Treeview",
            background=[("selected", SELECCION)],
            foreground=[("selected", "#000000")]
        )

        tabla = ttk.Treeview(
            marco,
            columns=columnas,
            show="headings",
            style="Calendario.Treeview"
        )

        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            tabla.heading(columna, text=titulo)
            tabla.column(
                columna,
                width=ancho,
                minwidth=55,
                anchor="center",
                stretch=True
            )

        barra = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=tabla.yview
        )
        tabla.configure(yscrollcommand=barra.set)

        tabla.pack(
            side="left",
            fill="both",
            expand=True
        )
        barra.pack(side="right", fill="y")

        return marco

    # --------------------------------------------------------
    # NAVEGACIÓN ENTRE MESES
    # --------------------------------------------------------

    def cambiar_mes(self, desplazamiento):
        self.mes += desplazamiento

        if self.mes < 1:
            self.mes = 12
            self.anio -= 1
        elif self.mes > 12:
            self.mes = 1
            self.anio += 1

        dias_mes = calendar.monthrange(self.anio, self.mes)[1]

        if self.fecha_seleccionada.month == self.mes:
            dia = min(self.fecha_seleccionada.day, dias_mes)
        else:
            dia = 1

        self.fecha_seleccionada = date(
            self.anio,
            self.mes,
            dia
        )

        self.actualizar_calendario()

    def ir_a_hoy(self):
        hoy = date.today()
        self.anio = hoy.year
        self.mes = hoy.month
        self.fecha_seleccionada = hoy
        self.actualizar_calendario()

    # --------------------------------------------------------
    # ACTUALIZACIÓN GENERAL
    # --------------------------------------------------------

    def actualizar_calendario(self):
        try:
            self.citas_mes = obtener_citas_mes(
                self.anio,
                self.mes
            )

            self._dibujar_dias()
            self._mostrar_citas_del_dia()
            self._mostrar_proximas_citas()

        except Exception as error:
            messagebox.showerror(
                "Error del calendario",
                "No se pudieron consultar las citas.\n\n"
                f"Detalle: {error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # DIBUJAR CALENDARIO MENSUAL
    # --------------------------------------------------------

    def _dibujar_dias(self):
        self.etiqueta_mes.configure(
            text=f"{MESES[self.mes - 1]} {self.anio}"
        )

        for widget in self.marco_dias.winfo_children():
            widget.destroy()

        self.botones_dias.clear()

        citas_por_dia = {}

        for cita in self.citas_mes:
            fecha = fecha_a_date(cita[1])
            estado = str(cita[6]).strip().lower()

            if estado != "cancelada":
                citas_por_dia[fecha.day] = (
                    citas_por_dia.get(fecha.day, 0) + 1
                )

        calendario_mes = calendar.Calendar(
            firstweekday=0
        ).monthdayscalendar(
            self.anio,
            self.mes
        )

        hoy = date.today()

        for fila in range(6):
            for columna in range(7):
                dia = (
                    calendario_mes[fila][columna]
                    if fila < len(calendario_mes)
                    and columna < len(calendario_mes[fila])
                    else 0
                )

                if dia == 0:
                    ctk.CTkLabel(
                        self.marco_dias,
                        text="",
                        fg_color="transparent"
                    ).grid(
                        row=fila,
                        column=columna,
                        sticky="nsew",
                        padx=2,
                        pady=2
                    )
                    continue

                fecha = date(
                    self.anio,
                    self.mes,
                    dia
                )

                cantidad = citas_por_dia.get(dia, 0)

                if cantidad > 0:
                    texto = f"{dia}\n● {cantidad}"
                    fondo = "#D5F2ED"
                else:
                    texto = str(dia)
                    fondo = PANEL_CLARO

                # Corrección: números negros en todos los días
                color_texto = "#000000"

                if fecha == self.fecha_seleccionada:
                    borde = DORADO_CLARO
                    grosor = 2
                elif fecha == hoy:
                    borde = DORADO
                    grosor = 2
                else:
                    borde = BORDE
                    grosor = 1

                boton = ctk.CTkButton(
                    self.marco_dias,
                    text=texto,
                    height=53,
                    corner_radius=8,
                    fg_color=fondo,
                    hover_color=PANEL_HOVER,
                    text_color=color_texto,
                    border_width=grosor,
                    border_color=borde,
                    font=("Arial", 11, "bold"),
                    command=lambda f=fecha: self.seleccionar_dia(f)
                )

                boton.grid(
                    row=fila,
                    column=columna,
                    sticky="nsew",
                    padx=2,
                    pady=2
                )

                self.botones_dias[fecha] = boton

    # --------------------------------------------------------
    # SELECCIONAR FECHA
    # --------------------------------------------------------

    def seleccionar_dia(self, fecha):
        self.fecha_seleccionada = fecha
        self.anio = fecha.year
        self.mes = fecha.month

        self._dibujar_dias()
        self._mostrar_citas_del_dia()

    # --------------------------------------------------------
    # DETALLE DE LAS CITAS DE UN DÍA
    # --------------------------------------------------------

    def _mostrar_citas_del_dia(self):
        tabla = self.tabla_dia.winfo_children()[0]

        for elemento in tabla.get_children():
            tabla.delete(elemento)

        fecha = self.fecha_seleccionada

        self.etiqueta_seleccion.configure(
            text=f"CITAS DEL {fecha.strftime('%d/%m/%Y')}"
        )

        citas_dia = []

        for cita in self.citas_mes:
            if fecha_a_date(cita[1]) == fecha:
                citas_dia.append(cita)

        activas = [
            cita for cita in citas_dia
            if str(cita[6]).strip().lower() != "cancelada"
        ]

        self.etiqueta_total.configure(
            text=(
                f"{len(activas)} cita(s) vigente(s) · "
                f"{len(citas_dia)} en total"
            )
        )

        for cita in citas_dia:
            tabla.insert(
                "",
                "end",
                values=(
                    hora_a_texto(cita[2]),
                    cita[3],
                    cita[6]
                )
            )

        if not citas_dia:
            tabla.insert(
                "",
                "end",
                values=("--:--", "Sin citas", "--")
            )

    # --------------------------------------------------------
    # PRÓXIMAS CITAS
    # --------------------------------------------------------

    def _mostrar_proximas_citas(self):
        tabla = self.tabla_proximas.winfo_children()[0]

        for elemento in tabla.get_children():
            tabla.delete(elemento)

        citas = obtener_proximas_citas(15)

        for cita in citas:
            fecha = fecha_a_date(cita[1])

            tabla.insert(
                "",
                "end",
                values=(
                    fecha.strftime("%d/%m/%Y"),
                    hora_a_texto(cita[2]),
                    cita[3],
                    cita[6]
                )
            )

        if not citas:
            tabla.insert(
                "",
                "end",
                values=("-", "-", "No hay próximas citas", "-")
            )


# ============================================================
# EJECUCIÓN INDEPENDIENTE PARA PRUEBAS
# ============================================================

if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Calendario de citas")
    ventana.geometry("1350x800")
    ventana.minsize(1050, 650)
    ventana.configure(fg_color=NEGRO)

    panel = PanelCalendario(ventana)
    panel.pack(fill="both", expand=True, padx=12, pady=12)

    ventana.mainloop()
