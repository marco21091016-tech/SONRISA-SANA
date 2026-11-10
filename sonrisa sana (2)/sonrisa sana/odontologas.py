import re
import customtkinter as ctk
from tkinter import messagebox
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

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def obtener_odontologas(termino=None):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        consulta = """
            SELECT
                IdOdontologa,
                Nombre,
                Apellidos,
                Especialidad,
                Telefono,
                Correo
            FROM dbo.Odontologa
        """
        parametros = ()

        if termino:
            patron = f"%{termino}%"
            consulta += """
                WHERE Nombre LIKE ?
                   OR Apellidos LIKE ?
                   OR CONCAT(Nombre, ' ', Apellidos) LIKE ?
                   OR Especialidad LIKE ?
                   OR Telefono LIKE ?
                   OR Correo LIKE ?
                   OR CAST(IdOdontologa AS VARCHAR(20)) LIKE ?
            """
            parametros = (patron,) * 7

        consulta += " ORDER BY Apellidos, Nombre"
        cursor.execute(consulta, parametros)
        return cursor.fetchall()

    finally:
        conexion.close()


def registrar_odontologa(nombre, apellidos, especialidad, telefono, correo):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO dbo.Odontologa
                (Nombre, Apellidos, Especialidad, Telefono, Correo)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nombre.strip(),
            apellidos.strip(),
            especialidad.strip(),
            telefono.strip(),
            correo.strip() or None
        ))
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def eliminar_odontologa(id_odontologa):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM dbo.Odontologa
            WHERE IdOdontologa = ?
        """, (id_odontologa,))

        if cursor.rowcount == 0:
            raise ValueError("La odontóloga seleccionada ya no existe.")

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ============================================================
# PANEL INTEGRADO EN MAIN.PY
# ============================================================

class PanelOdontologas(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=NEGRO, corner_radius=0)

        self.seleccion_id = None
        self.filas = {}

        self.crear_interfaz()
        self.cargar_odontologas()

    # --------------------------------------------------------
    # BOTONES
    # --------------------------------------------------------

    def boton(self, padre, texto, comando, contorno=False, ancho=130):
        return ctk.CTkButton(
            padre,
            text=texto,
            command=comando,
            width=ancho,
            height=38,
            corner_radius=7,
            fg_color=PANEL_CLARO if contorno else DORADO,
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
            text="GESTIÓN DE ODONTÓLOGAS",
            font=("Georgia", 23, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=18, pady=(14, 3))

        ctk.CTkLabel(
            encabezado,
            text="Consulta y administra los datos de las profesionales dentales.",
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=18, pady=(0, 14))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=16, pady=(0, 8))

        self.buscar_var = ctk.StringVar()
        self.buscar_entry = ctk.CTkEntry(
            barra,
            textvariable=self.buscar_var,
            placeholder_text="Buscar por nombre, especialidad, teléfono, correo o ID...",
            height=38,
            fg_color=PANEL_CLARO,
            text_color=TEXTO,
            border_color=DORADO,
            placeholder_text_color="#6A9690"
        )
        self.buscar_entry.pack(side="left", fill="x", expand=True, padx=(0, 7))
        self.buscar_entry.bind(
            "<Return>", lambda evento: self.buscar_odontologas()
        )

        self.boton(
            barra, "Buscar", self.buscar_odontologas, contorno=True, ancho=90
        ).pack(side="left", padx=4)

        self.boton(
            barra, "Mostrar todas", self.cargar_odontologas,
            contorno=True, ancho=115
        ).pack(side="left", padx=4)

        self.boton(
            barra, "+ Nueva odontóloga", self.nueva_odontologa, ancho=165
        ).pack(side="left", padx=4)

        self.boton(
            barra, "Eliminar", self.accion_eliminar, contorno=True, ancho=90
        ).pack(side="left", padx=4)

        self.total_label = ctk.CTkLabel(
            self,
            text="Odontólogas encontradas: 0",
            font=("Arial", 12, "bold"),
            text_color=TEXTO
        )
        self.total_label.pack(anchor="w", padx=20, pady=(5, 8))

        self.tabla_contenedor = ctk.CTkFrame(
            self, fg_color=PANEL, border_color="#B8DED8",
            border_width=1, corner_radius=10
        )
        self.tabla_contenedor.pack(
            fill="both", expand=True, padx=16, pady=(0, 8)
        )

        self.crear_tabla()

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=16, pady=(0, 12))

        self.detalle_label = ctk.CTkLabel(
            pie,
            text="Selecciona una odontóloga para ver sus datos.",
            font=("Arial", 11),
            text_color=TEXTO
        )
        self.detalle_label.pack(side="left")

        ctk.CTkLabel(
            pie,
            text="SONRISA SANA  |  Gestión de odontólogas",
            text_color=DORADO,
            font=("Arial", 10)
        ).pack(side="right")

    # --------------------------------------------------------
    # TABLA DE ODONTÓLOGAS
    # --------------------------------------------------------

    def crear_tabla(self):
        self.tabla_contenedor.grid_columnconfigure(0, weight=1)
        self.tabla_contenedor.grid_rowconfigure(1, weight=1)

        self.columnas = [
            ("id", "ID", 65),
            ("nombre", "Nombre", 145),
            ("apellidos", "Apellidos", 175),
            ("especialidad", "Especialidad", 170),
            ("telefono", "Teléfono", 135),
            ("correo", "Correo electrónico", 220)
        ]

        cabecera = ctk.CTkFrame(
            self.tabla_contenedor, fg_color="#DDF3EF", corner_radius=4
        )
        cabecera.grid(
            row=0, column=0, sticky="ew", padx=(7, 0), pady=(7, 0)
        )

        for indice, (clave, titulo, ancho) in enumerate(self.columnas):
            cabecera.grid_columnconfigure(indice, weight=1, minsize=ancho)

            ctk.CTkLabel(
                cabecera,
                text=titulo,
                font=("Arial", 10, "bold"),
                text_color=DORADO_CLARO,
                anchor="center"
            ).grid(row=0, column=indice, sticky="ew", padx=3, pady=10)

        self.lista_filas = ctk.CTkScrollableFrame(
            self.tabla_contenedor,
            fg_color=PANEL_CLARO,
            corner_radius=4,
            scrollbar_button_color="#B8DED8",
            scrollbar_button_hover_color=DORADO
        )
        self.lista_filas.grid(
            row=1, column=0, sticky="nsew", padx=(7, 0), pady=(0, 7)
        )

        for indice, (_, _, ancho) in enumerate(self.columnas):
            self.lista_filas.grid_columnconfigure(
                indice, weight=1, minsize=ancho
            )

    # --------------------------------------------------------
    # MOSTRAR REGISTROS
    # --------------------------------------------------------

    def mostrar_filas(self, filas):
        for widget in self.lista_filas.winfo_children():
            widget.destroy()

        self.filas.clear()
        self.seleccion_id = None
        self.detalle_label.configure(
            text="Selecciona una odontóloga para ver sus datos."
        )

        for numero, fila in enumerate(filas):
            id_odontologa = int(fila[0])

            valores = [
                fila[0],
                fila[1] or "",
                fila[2] or "",
                fila[3] or "",
                fila[4] or "",
                fila[5] or ""
            ]

            color_fila = PANEL_CLARO if numero % 2 == 0 else "#F4FBFA"

            fila_frame = ctk.CTkFrame(
                self.lista_filas, fg_color=color_fila, corner_radius=3
            )
            fila_frame.grid(
                row=numero, column=0, columnspan=len(self.columnas),
                sticky="ew", pady=1
            )

            for indice, (_, _, ancho) in enumerate(self.columnas):
                fila_frame.grid_columnconfigure(
                    indice, weight=1, minsize=ancho
                )

            self.filas[id_odontologa] = {
                "frame": fila_frame,
                "color": color_fila,
                "datos": valores
            }

            fila_frame.bind(
                "<Button-1>",
                lambda evento, ident=id_odontologa: self.seleccionar_fila(ident)
            )

            for indice, valor in enumerate(valores):
                etiqueta = ctk.CTkLabel(
                    fila_frame,
                    text=str(valor),
                    text_color=TEXTO,
                    font=("Arial", 10),
                    anchor="center",
                    wraplength=self.columnas[indice][2] - 12
                )
                etiqueta.grid(
                    row=0, column=indice, sticky="ew", padx=3, pady=11
                )
                etiqueta.bind(
                    "<Button-1>",
                    lambda evento, ident=id_odontologa: self.seleccionar_fila(ident)
                )

        self.total_label.configure(
            text=f"Odontólogas encontradas: {len(filas)}"
        )

    # --------------------------------------------------------
    # SELECCIONAR UNA ODONTÓLOGA
    # --------------------------------------------------------

    def seleccionar_fila(self, id_odontologa):
        self.seleccion_id = id_odontologa

        for ident, informacion in self.filas.items():
            informacion["frame"].configure(
                fg_color=SELECCION if ident == id_odontologa else informacion["color"]
            )

        datos = self.filas[id_odontologa]["datos"]
        self.detalle_label.configure(
            text=(
                f"Seleccionada: {datos[1]} {datos[2]} "
                f"| Especialidad: {datos[3]}"
            )
        )

    # --------------------------------------------------------
    # ELIMINAR ODONTÓLOGA
    # --------------------------------------------------------

    def accion_eliminar(self):
        ventana = self.winfo_toplevel()
        id_odontologa = self.seleccion_id

        if id_odontologa is None:
            messagebox.showwarning(
                "Selecciona una odontóloga",
                "Primero selecciona una odontóloga de la tabla.",
                parent=ventana
            )
            return

        datos = self.filas[id_odontologa]["datos"]
        confirmar = messagebox.askyesno(
            "Eliminar odontóloga",
            f"¿Deseas eliminar definitivamente a {datos[1]} {datos[2]} "
            f"(ID {id_odontologa})?",
            parent=ventana,
            default="no"
        )

        if not confirmar:
            return

        try:
            eliminar_odontologa(id_odontologa)

        except ValueError as error:
            messagebox.showwarning(
                "Registro no disponible", str(error), parent=ventana
            )
            self.cargar_odontologas()
            return

        except Exception as error:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar a {datos[1]} {datos[2]}.\n\n{error}",
                parent=ventana
            )
            return

        self.cargar_odontologas()
        messagebox.showinfo(
            "Odontóloga eliminada",
            f"Se eliminó a {datos[1]} {datos[2]} (ID {id_odontologa}).",
            parent=ventana
        )

    # --------------------------------------------------------
    # CONSULTAR Y BUSCAR
    # --------------------------------------------------------

    def cargar_odontologas(self):
        try:
            filas = obtener_odontologas()
            self.mostrar_filas(filas)

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron consultar las odontólogas.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    def buscar_odontologas(self):
        termino = self.buscar_var.get().strip()

        try:
            filas = obtener_odontologas(termino or None)
            self.mostrar_filas(filas)

            if termino and not filas:
                messagebox.showinfo(
                    "Sin resultados",
                    f"No se encontraron odontólogas para: {termino}",
                    parent=self.winfo_toplevel()
                )

        except Exception as error:
            messagebox.showerror(
                "Error de búsqueda",
                f"No se pudo completar la búsqueda.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # REGISTRAR ODONTÓLOGA
    # --------------------------------------------------------

    def nueva_odontologa(self):
        ventana = ctk.CTkToplevel(self.winfo_toplevel())
        ventana.title("Nueva odontóloga | Sonrisa Sana")
        ventana.geometry("540x630")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="REGISTRAR ODONTÓLOGA",
            font=("Georgia", 22, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(20, 14))

        formulario = ctk.CTkFrame(
            ventana, fg_color=PANEL, border_color=DORADO,
            border_width=1, corner_radius=12
        )
        formulario.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        campos = {}
        definiciones = [
            ("Nombre *", "nombre", "Nombre(s)"),
            ("Apellidos *", "apellidos", "Apellidos"),
            ("Especialidad *", "especialidad", "Especialidad dental"),
            ("Teléfono *", "telefono", "Número telefónico"),
            ("Correo electrónico (opcional)", "correo", "correo@ejemplo.com")
        ]

        for titulo, clave, ejemplo in definiciones:
            ctk.CTkLabel(
                formulario,
                text=titulo,
                text_color=TEXTO,
                font=("Arial", 11, "bold")
            ).pack(anchor="w", padx=20, pady=(7, 3))

            campo = ctk.CTkEntry(
                formulario,
                height=35,
                fg_color=PANEL_CLARO,
                text_color=TEXTO,
                border_color=DORADO,
                placeholder_text=ejemplo,
                placeholder_text_color="#6A9690"
            )
            campo.pack(fill="x", padx=20, pady=(0, 2))
            campos[clave] = campo

        def guardar():
            nombre = campos["nombre"].get().strip()
            apellidos = campos["apellidos"].get().strip()
            especialidad = campos["especialidad"].get().strip()
            telefono = campos["telefono"].get().strip()
            correo = campos["correo"].get().strip()

            if not all([nombre, apellidos, especialidad, telefono]):
                messagebox.showwarning(
                    "Datos obligatorios",
                    "Completa nombre, apellidos, especialidad y teléfono.",
                    parent=ventana
                )
                return

            if not re.fullmatch(r"[0-9+\-\s()]{7,20}", telefono):
                messagebox.showwarning(
                    "Teléfono inválido",
                    "Usa entre 7 y 20 caracteres: números y, si lo necesitas, "
                    "+, espacios, paréntesis o guiones.",
                    parent=ventana
                )
                return

            if correo and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
                messagebox.showwarning(
                    "Correo inválido",
                    "Escribe un correo válido o deja el campo vacío.",
                    parent=ventana
                )
                return

            try:
                registrar_odontologa(
                    nombre, apellidos, especialidad, telefono, correo
                )

                messagebox.showinfo(
                    "Sonrisa Sana",
                    "Odontóloga registrada correctamente.",
                    parent=ventana
                )
                ventana.destroy()
                self.cargar_odontologas()

            except Exception as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No se pudo registrar la odontóloga.\n\n{error}",
                    parent=ventana
                )

        self.boton(
            formulario, "GUARDAR ODONTÓLOGA", guardar, ancho=220
        ).pack(fill="x", padx=20, pady=(13, 7))

        self.boton(
            formulario, "Cancelar", ventana.destroy, contorno=True, ancho=220
        ).pack(fill="x", padx=20, pady=(0, 12))


# ============================================================
# EJECUCIÓN INDEPENDIENTE PARA PRUEBAS
# ============================================================

if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Odontólogas")
    ventana.geometry("1250x750")
    ventana.minsize(1000, 620)
    ventana.configure(fg_color=NEGRO)

    panel = PanelOdontologas(ventana)
    panel.pack(fill="both", expand=True)

    ventana.mainloop()