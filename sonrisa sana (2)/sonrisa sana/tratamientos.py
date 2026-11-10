import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from conexion import conectar


# ============================================================
# CONFIGURACIÓN VISUAL: SONRISA SANA
# ============================================================

NEGRO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
DORADO = "#159F95"
DORADO_CLARO = "#087F78"
TEXTO = "#263B3A"
BLANCO = "#FFFFFF"
SELECCION = "#BFEDE6"
BORDE = "#B8DED8"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def obtener_pacientes():
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT IdPaciente, Nombre, Apellidos
            FROM dbo.Paciente
            ORDER BY Apellidos, Nombre
        """)
        return cursor.fetchall()
    finally:
        conexion.close()


def obtener_tratamientos(termino=None):
    conexion = conectar()
    try:
        cursor = conexion.cursor()

        sql = """
            SELECT
                t.IdTratamiento,
                p.Nombre + ' ' + p.Apellidos AS Paciente,
                t.NombreTratamiento,
                t.FechaInicio,
                t.FechaFin,
                t.Estado,
                t.Descripcion
            FROM dbo.Tratamiento t
            INNER JOIN dbo.Paciente p
                ON p.IdPaciente = t.IdPaciente
        """

        if termino:
            patron = f"%{termino}%"
            sql += """
                WHERE
                    p.Nombre LIKE ?
                    OR p.Apellidos LIKE ?
                    OR (p.Nombre + ' ' + p.Apellidos) LIKE ?
                    OR t.NombreTratamiento LIKE ?
                    OR t.Estado LIKE ?
                    OR CAST(t.IdTratamiento AS VARCHAR(20)) LIKE ?
            """
            cursor.execute(
                sql + " ORDER BY t.IdTratamiento DESC",
                (patron,) * 6
            )
        else:
            cursor.execute(sql + " ORDER BY t.IdTratamiento DESC")

        return cursor.fetchall()
    finally:
        conexion.close()


def obtener_sesiones(id_tratamiento):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT
                s.IdSesion,
                s.FechaSesion,
                p.NombreProcedimiento,
                s.EstadoSesion,
                s.Observaciones
            FROM dbo.SesionTratamiento s
            INNER JOIN dbo.Procedimiento p
                ON p.IdProcedimiento = s.IdProcedimiento
            WHERE s.IdTratamiento = ?
            ORDER BY s.FechaSesion DESC, s.IdSesion DESC
        """, (id_tratamiento,))
        return cursor.fetchall()
    finally:
        conexion.close()


def obtener_procedimientos():
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT IdProcedimiento, NombreProcedimiento
            FROM dbo.Procedimiento
            ORDER BY NombreProcedimiento
        """)
        return cursor.fetchall()
    finally:
        conexion.close()


def obtener_estados_tratamiento():
    return ["Pendiente", "En proceso", "Finalizado", "Cancelado"]


def obtener_estados_sesion():
    return ["Programada", "Realizada", "Cancelada"]


def registrar_tratamiento(
    id_paciente, nombre, descripcion, fecha_inicio, estado
):
    if not nombre.strip():
        raise ValueError("El nombre del tratamiento es obligatorio.")

    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO dbo.Tratamiento
                (IdPaciente, NombreTratamiento, Descripcion,
                 FechaInicio, FechaFin, Estado)
            VALUES (?, ?, ?, ?, NULL, ?)
        """, (
            id_paciente,
            nombre.strip(),
            descripcion.strip() or None,
            fecha_inicio,
            estado
        ))
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def registrar_sesion(
    id_tratamiento, id_procedimiento,
    fecha_sesion, estado, observaciones
):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO dbo.SesionTratamiento
                (IdTratamiento, IdProcedimiento, FechaSesion,
                 Observaciones, EstadoSesion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            id_tratamiento,
            id_procedimiento,
            fecha_sesion,
            observaciones.strip() or None,
            estado
        ))
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def eliminar_tratamiento(id_tratamiento):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM dbo.Tratamiento
            WHERE IdTratamiento = ?
        """, (id_tratamiento,))

        if cursor.rowcount == 0:
            raise ValueError("El tratamiento seleccionado ya no existe.")

        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


# ============================================================
# PANEL DE TRATAMIENTOS
# ============================================================

class PanelTratamientos(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=NEGRO, corner_radius=0)

        self.seleccion_id = None
        self.filas = {}

        self.crear_interfaz()
        self.cargar_tratamientos()

    def boton(self, padre, texto, comando, contorno=False, ancho=130):
        return ctk.CTkButton(
            padre,
            text=texto,
            command=comando,
            width=ancho,
            height=38,
            corner_radius=7,
            fg_color=PANEL if contorno else DORADO,
            hover_color="#0E8F85",
            text_color=DORADO_CLARO if contorno else BLANCO,
            border_color=DORADO,
            border_width=1 if contorno else 0,
            font=("Arial", 11, "bold")
        )

    # --------------------------------------------------------
    # INTERFAZ PRINCIPAL
    # --------------------------------------------------------

    def crear_interfaz(self):
        encabezado = ctk.CTkFrame(
            self, fg_color=PANEL, border_color=DORADO,
            border_width=1, corner_radius=12
        )
        encabezado.pack(fill="x", padx=16, pady=(12, 10))

        ctk.CTkLabel(
            encabezado,
            text="GESTIÓN DE TRATAMIENTOS",
            font=("Georgia", 23, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=18, pady=(14, 3))

        ctk.CTkLabel(
            encabezado,
            text="Administra tratamientos, sesiones y procedimientos asociados.",
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=18, pady=(0, 14))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=16, pady=(0, 8))

        self.buscar_var = ctk.StringVar()

        self.buscar_entry = ctk.CTkEntry(
            barra,
            textvariable=self.buscar_var,
            placeholder_text="Buscar por paciente, tratamiento, estado o ID...",
            height=38,
            fg_color=PANEL,
            text_color=TEXTO,
            border_color=DORADO,
            placeholder_text_color="#6A9690"
        )
        self.buscar_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 7)
        )
        self.buscar_entry.bind(
            "<KeyRelease>", lambda evento: self.cargar_tratamientos()
        )

        self.boton(
            barra, "Actualizar", self.cargar_tratamientos,
            contorno=True, ancho=100
        ).pack(side="left", padx=4)

        self.boton(
            barra, "+ Nuevo tratamiento", self.nuevo_tratamiento, ancho=165
        ).pack(side="left", padx=4)

        self.total_label = ctk.CTkLabel(
            self,
            text="Tratamientos encontrados: 0",
            font=("Arial", 12, "bold"),
            text_color=TEXTO
        )
        self.total_label.pack(anchor="w", padx=20, pady=(5, 8))

        self.tabla_contenedor = ctk.CTkFrame(
            self, fg_color=PANEL, border_color=BORDE,
            border_width=1, corner_radius=10
        )
        self.tabla_contenedor.pack(
            fill="both", expand=True, padx=16, pady=(0, 8)
        )

        self.crear_tabla()

        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(fill="x", padx=16, pady=(0, 12))

        self.boton(
            acciones, "Registrar sesión", self.nueva_sesion, ancho=150
        ).pack(side="left", padx=(0, 7))

        self.boton(
            acciones, "Ver sesiones", self.ver_sesiones,
            contorno=True, ancho=135
        ).pack(side="left", padx=7)

        self.boton(
            acciones, "Eliminar", self.eliminar_seleccionado,
            contorno=True, ancho=100
        ).pack(side="left", padx=7)

        ctk.CTkLabel(
            acciones,
            text="SONRISA SANA  |  Gestión dental",
            text_color=DORADO,
            font=("Arial", 10)
        ).pack(side="right", padx=5)

    # --------------------------------------------------------
    # TABLA DE TRATAMIENTOS
    # --------------------------------------------------------

    def crear_tabla(self):
        self.tabla_contenedor.grid_columnconfigure(0, weight=1)
        self.tabla_contenedor.grid_rowconfigure(1, weight=1)

        encabezados = [
            ("id", "ID", 55),
            ("paciente", "Paciente", 165),
            ("nombre", "Tratamiento", 165),
            ("inicio", "Fecha de inicio", 110),
            ("fin", "Fecha de fin", 110),
            ("estado", "Estado", 110),
            ("descripcion", "Descripción", 200)
        ]
        self.columnas = encabezados

        cabecera = ctk.CTkFrame(
            self.tabla_contenedor, fg_color="#DDF3EF", corner_radius=4
        )
        cabecera.grid(row=0, column=0, sticky="ew", padx=7, pady=(7, 0))

        for indice, (clave, titulo, ancho) in enumerate(encabezados):
            cabecera.grid_columnconfigure(indice, weight=1, minsize=ancho)

            ctk.CTkLabel(
                cabecera,
                text=titulo,
                font=("Arial", 10, "bold"),
                text_color=DORADO_CLARO,
                anchor="center"
            ).grid(row=0, column=indice, sticky="ew", padx=3, pady=9)

        self.lista_filas = ctk.CTkScrollableFrame(
            self.tabla_contenedor,
            fg_color=PANEL_CLARO,
            corner_radius=4,
            scrollbar_button_color=BORDE,
            scrollbar_button_hover_color=DORADO
        )
        self.lista_filas.grid(
            row=1, column=0, sticky="nsew", padx=7, pady=(0, 7)
        )

        for indice, (_, _, ancho) in enumerate(encabezados):
            self.lista_filas.grid_columnconfigure(
                indice, weight=1, minsize=ancho
            )

    def mostrar_filas(self, filas):
        for widget in self.lista_filas.winfo_children():
            widget.destroy()

        self.filas.clear()
        self.seleccion_id = None

        for numero, fila in enumerate(filas):
            valores = list(fila)
            id_tratamiento = int(valores[0])

            valores[3] = valores[3].strftime("%Y-%m-%d") if valores[3] else ""
            valores[4] = valores[4].strftime("%Y-%m-%d") if valores[4] else ""
            valores[5] = valores[5] or ""
            valores[6] = valores[6] or ""

            color_fila = PANEL_CLARO if numero % 2 == 0 else NEGRO

            fila_frame = ctk.CTkFrame(
                self.lista_filas, fg_color=color_fila, corner_radius=3
            )
            fila_frame.grid(
                row=numero, column=0, columnspan=7, sticky="ew", pady=1
            )

            for indice, (_, _, ancho) in enumerate(self.columnas):
                fila_frame.grid_columnconfigure(indice, weight=1, minsize=ancho)

            for indice, valor in enumerate(valores):
                etiqueta = ctk.CTkLabel(
                    fila_frame,
                    text=str(valor) if valor is not None else "",
                    text_color=TEXTO,
                    font=("Arial", 10),
                    anchor="center",
                    wraplength=self.columnas[indice][2] - 10
                )
                etiqueta.grid(
                    row=0, column=indice, sticky="ew", padx=3, pady=9
                )
                etiqueta.bind(
                    "<Button-1>",
                    lambda evento, ident=id_tratamiento: self.seleccionar_fila(ident)
                )

            fila_frame.bind(
                "<Button-1>",
                lambda evento, ident=id_tratamiento: self.seleccionar_fila(ident)
            )

            self.filas[id_tratamiento] = fila_frame

        self.total_label.configure(
            text=f"Tratamientos encontrados: {len(filas)}"
        )

    def seleccionar_fila(self, id_tratamiento):
        self.seleccion_id = id_tratamiento

        for ident, frame in self.filas.items():
            frame.configure(
                fg_color=SELECCION if ident == id_tratamiento else PANEL_CLARO
            )

    # --------------------------------------------------------
    # ELIMINAR TRATAMIENTO
    # --------------------------------------------------------

    def eliminar_seleccionado(self):
        ventana = self.winfo_toplevel()
        id_tratamiento = self.seleccion_id

        if id_tratamiento is None:
            messagebox.showwarning(
                "Selecciona un tratamiento",
                "Primero selecciona una fila de la tabla.",
                parent=ventana
            )
            return

        confirmar = messagebox.askyesno(
            "Eliminar tratamiento",
            f"¿Deseas eliminar definitivamente el tratamiento #{id_tratamiento}?",
            parent=ventana,
            default="no"
        )

        if not confirmar:
            return

        try:
            eliminar_tratamiento(id_tratamiento)

        except ValueError as error:
            messagebox.showwarning(
                "Tratamiento no disponible", str(error), parent=ventana
            )
            self.cargar_tratamientos()
            return

        except Exception as error:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar el tratamiento #{id_tratamiento}.\n\n{error}",
                parent=ventana
            )
            return

        self.cargar_tratamientos()
        messagebox.showinfo(
            "Tratamiento eliminado",
            f"Se eliminó el tratamiento #{id_tratamiento}.",
            parent=ventana
        )

    # --------------------------------------------------------
    # CONSULTAR Y BUSCAR
    # --------------------------------------------------------

    def cargar_tratamientos(self):
        try:
            termino = self.buscar_var.get().strip()
            filas = obtener_tratamientos(termino or None)
            self.mostrar_filas(filas)

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron consultar los tratamientos.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # REGISTRAR TRATAMIENTO
    # --------------------------------------------------------

    def nuevo_tratamiento(self):
        try:
            pacientes = obtener_pacientes()
            estados = obtener_estados_tratamiento()

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos", str(error),
                parent=self.winfo_toplevel()
            )
            return

        if not pacientes:
            messagebox.showwarning(
                "Sin pacientes",
                "Primero registra un paciente.",
                parent=self.winfo_toplevel()
            )
            return

        ventana = ctk.CTkToplevel(self.winfo_toplevel())
        ventana.title("Nuevo tratamiento | Sonrisa Sana")
        ventana.geometry("540x620")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="REGISTRAR TRATAMIENTO",
            font=("Georgia", 22, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(20, 15))

        formulario = ctk.CTkFrame(
            ventana, fg_color=PANEL, border_width=1,
            border_color=DORADO, corner_radius=12
        )
        formulario.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        def etiqueta(texto):
            ctk.CTkLabel(
                formulario,
                text=texto,
                text_color=TEXTO,
                font=("Arial", 11, "bold")
            ).pack(anchor="w", padx=18, pady=(8, 3))

        opciones = {
            f"{p[0]} | {p[1]} {p[2]}": p[0]
            for p in pacientes
        }

        etiqueta("Paciente *")
        paciente_var = ctk.StringVar(value=next(iter(opciones)))

        ctk.CTkOptionMenu(
            formulario,
            variable=paciente_var,
            values=list(opciones.keys()),
            fg_color=DORADO,
            button_color=DORADO_CLARO,
            button_hover_color="#0E8F85",
            text_color=BLANCO,
            dropdown_fg_color=PANEL,
            dropdown_text_color=TEXTO
        ).pack(fill="x", padx=18)

        campos = {}

        for titulo, clave, ejemplo in [
            ("Nombre del tratamiento *", "nombre", "Ejemplo: Limpieza dental"),
            ("Fecha de inicio (AAAA-MM-DD) *", "fecha", "AAAA-MM-DD"),
            ("Descripción (opcional)", "descripcion", "Detalles del tratamiento")
        ]:
            etiqueta(titulo)
            entrada = ctk.CTkEntry(
                formulario,
                height=35,
                fg_color=PANEL_CLARO,
                text_color=TEXTO,
                border_color=DORADO,
                placeholder_text=ejemplo,
                placeholder_text_color="#6A9690"
            )
            entrada.pack(fill="x", padx=18)
            campos[clave] = entrada

        campos["fecha"].insert(0, date.today().isoformat())

        etiqueta("Estado del tratamiento *")
        estado_var = ctk.StringVar(value=estados[0])

        ctk.CTkOptionMenu(
            formulario,
            variable=estado_var,
            values=estados,
            fg_color=DORADO,
            button_color=DORADO_CLARO,
            button_hover_color="#0E8F85",
            text_color=BLANCO,
            dropdown_fg_color=PANEL,
            dropdown_text_color=TEXTO
        ).pack(fill="x", padx=18)

        def guardar():
            nombre = campos["nombre"].get().strip()
            descripcion = campos["descripcion"].get().strip()

            if not nombre:
                messagebox.showwarning(
                    "Dato obligatorio",
                    "Escribe el nombre del tratamiento.",
                    parent=ventana
                )
                return

            try:
                fecha_inicio = date.fromisoformat(campos["fecha"].get().strip())
            except ValueError:
                messagebox.showwarning(
                    "Fecha inválida",
                    "Escribe una fecha válida con el formato AAAA-MM-DD.",
                    parent=ventana
                )
                return

            try:
                registrar_tratamiento(
                    opciones[paciente_var.get()], nombre,
                    descripcion, fecha_inicio, estado_var.get()
                )

                messagebox.showinfo(
                    "Sonrisa Sana",
                    "Tratamiento registrado correctamente.",
                    parent=ventana
                )
                ventana.destroy()
                self.cargar_tratamientos()

            except Exception as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No se pudo registrar el tratamiento.\n\n{error}",
                    parent=ventana
                )

        self.boton(
            formulario, "GUARDAR TRATAMIENTO", guardar, ancho=220
        ).pack(fill="x", padx=18, pady=(15, 8))

        self.boton(
            formulario, "Cancelar", ventana.destroy, contorno=True, ancho=220
        ).pack(fill="x", padx=18, pady=(0, 14))

    # --------------------------------------------------------
    # VER SESIONES
    # --------------------------------------------------------

    def ver_sesiones(self):
        if self.seleccion_id is None:
            messagebox.showwarning(
                "Selecciona un tratamiento",
                "Selecciona una fila de la tabla primero.",
                parent=self.winfo_toplevel()
            )
            return

        try:
            sesiones = obtener_sesiones(self.seleccion_id)

        except Exception as error:
            messagebox.showerror(
                "Error de consulta", str(error), parent=self.winfo_toplevel()
            )
            return

        ventana = ctk.CTkToplevel(self.winfo_toplevel())
        ventana.title("Sesiones del tratamiento")
        ventana.geometry("950x480")
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())

        ctk.CTkLabel(
            ventana,
            text=f"SESIONES DEL TRATAMIENTO #{self.seleccion_id}",
            font=("Georgia", 20, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=16)

        tabla = ctk.CTkScrollableFrame(
            ventana,
            fg_color=PANEL_CLARO,
            scrollbar_button_color=BORDE,
            scrollbar_button_hover_color=DORADO
        )
        tabla.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        titulos = ["ID", "Fecha", "Procedimiento", "Estado", "Observaciones"]
        anchos = [55, 115, 210, 120, 330]

        for i, titulo in enumerate(titulos):
            tabla.grid_columnconfigure(i, weight=1, minsize=anchos[i])
            ctk.CTkLabel(
                tabla,
                text=titulo,
                text_color=DORADO_CLARO,
                font=("Arial", 10, "bold"),
                fg_color="#DDF3EF"
            ).grid(row=0, column=i, sticky="ew", padx=1, pady=1)

        for numero, sesion in enumerate(sesiones, start=1):
            fecha = sesion[1].strftime("%Y-%m-%d") if sesion[1] else ""

            valores = [
                sesion[0], fecha, sesion[2], sesion[3], sesion[4] or ""
            ]

            for i, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    text_color=TEXTO,
                    fg_color=PANEL if numero % 2 else PANEL_CLARO,
                    font=("Arial", 10),
                    wraplength=anchos[i] - 10
                ).grid(row=numero, column=i, sticky="ew", padx=1, pady=1)

        if not sesiones:
            ctk.CTkLabel(
                tabla,
                text="Este tratamiento todavía no tiene sesiones registradas.",
                text_color=TEXTO
            ).grid(row=1, column=0, columnspan=5, pady=25)

    # --------------------------------------------------------
    # REGISTRAR SESIÓN
    # --------------------------------------------------------

    def nueva_sesion(self):
        if self.seleccion_id is None:
            messagebox.showwarning(
                "Selecciona un tratamiento",
                "Selecciona el tratamiento al que deseas agregar la sesión.",
                parent=self.winfo_toplevel()
            )
            return

        try:
            procedimientos = obtener_procedimientos()
            estados = obtener_estados_sesion()

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos", str(error),
                parent=self.winfo_toplevel()
            )
            return

        if not procedimientos:
            messagebox.showwarning(
                "Sin procedimientos",
                "No hay procedimientos registrados en la base de datos.",
                parent=self.winfo_toplevel()
            )
            return

        ventana = ctk.CTkToplevel(self.winfo_toplevel())
        ventana.title("Registrar sesión")
        ventana.geometry("560x570")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="REGISTRAR SESIÓN",
            font=("Georgia", 22, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(20, 15))

        formulario = ctk.CTkFrame(
            ventana, fg_color=PANEL, border_width=1,
            border_color=DORADO, corner_radius=12
        )
        formulario.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        def etiqueta(texto):
            ctk.CTkLabel(
                formulario,
                text=texto,
                text_color=TEXTO,
                font=("Arial", 11, "bold")
            ).pack(anchor="w", padx=18, pady=(9, 3))

        mapa = {f"{p[0]} | {p[1]}": p[0] for p in procedimientos}

        etiqueta("Procedimiento *")
        procedimiento_var = ctk.StringVar(value=next(iter(mapa)))

        ctk.CTkOptionMenu(
            formulario,
            variable=procedimiento_var,
            values=list(mapa.keys()),
            fg_color=DORADO,
            button_color=DORADO_CLARO,
            button_hover_color="#0E8F85",
            text_color=BLANCO,
            dropdown_fg_color=PANEL,
            dropdown_text_color=TEXTO
        ).pack(fill="x", padx=18)

        etiqueta("Fecha de la sesión (AAAA-MM-DD) *")
        fecha_entry = ctk.CTkEntry(
            formulario,
            height=35,
            fg_color=PANEL_CLARO,
            text_color=TEXTO,
            border_color=DORADO,
            placeholder_text="AAAA-MM-DD"
        )
        fecha_entry.pack(fill="x", padx=18)
        fecha_entry.insert(0, date.today().isoformat())

        etiqueta("Estado de la sesión *")
        estado_var = ctk.StringVar(value=estados[0])

        ctk.CTkOptionMenu(
            formulario,
            variable=estado_var,
            values=estados,
            fg_color=DORADO,
            button_color=DORADO_CLARO,
            button_hover_color="#0E8F85",
            text_color=BLANCO,
            dropdown_fg_color=PANEL,
            dropdown_text_color=TEXTO
        ).pack(fill="x", padx=18)

        etiqueta("Observaciones (opcional)")
        observaciones = ctk.CTkTextbox(
            formulario,
            height=70,
            fg_color=PANEL_CLARO,
            text_color=TEXTO,
            border_color=DORADO,
            border_width=1
        )
        observaciones.pack(fill="x", padx=18)

        def guardar():
            try:
                fecha_sesion = date.fromisoformat(fecha_entry.get().strip())

                if fecha_sesion > date.today():
                    raise ValueError("La fecha de la sesión no puede ser futura.")

            except ValueError as error:
                messagebox.showwarning(
                    "Fecha inválida",
                    f"{error}\nUsa el formato AAAA-MM-DD.",
                    parent=ventana
                )
                return

            try:
                registrar_sesion(
                    self.seleccion_id,
                    mapa[procedimiento_var.get()],
                    fecha_sesion,
                    estado_var.get(),
                    observaciones.get("1.0", "end").strip()
                )

                messagebox.showinfo(
                    "Sonrisa Sana",
                    "Sesión registrada correctamente.",
                    parent=ventana
                )
                ventana.destroy()

            except Exception as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No se pudo registrar la sesión.\n\n{error}",
                    parent=ventana
                )

        self.boton(
            formulario, "GUARDAR SESIÓN", guardar, ancho=220
        ).pack(fill="x", padx=18, pady=(12, 7))

        self.boton(
            formulario, "Cancelar", ventana.destroy, contorno=True, ancho=220
        ).pack(fill="x", padx=18, pady=(0, 12))


# ============================================================
# EJECUCIÓN INDEPENDIENTE PARA PRUEBAS
# ============================================================

if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Tratamientos")
    ventana.geometry("1250x750")
    ventana.minsize(1000, 620)
    ventana.configure(fg_color=NEGRO)

    panel = PanelTratamientos(ventana)
    panel.pack(fill="both", expand=True)

    ventana.mainloop()