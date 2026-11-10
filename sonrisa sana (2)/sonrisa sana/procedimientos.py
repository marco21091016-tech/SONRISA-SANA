import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation

from conexion import conectar


# ============================================================
# CONFIGURACIÓN VISUAL: SONRISA SANA
# ============================================================

NEGRO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
DORADO = "#159F95"          # Turquesa principal
DORADO_CLARO = "#087F78"    # Turquesa oscuro
TEXTO = "#263B3A"
BLANCO = "#FFFFFF"
SELECCION = "#BFEDE6"
BORDE = "#B8DED8"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# CONVERSIÓN Y VALIDACIÓN DE COSTOS
# ============================================================

def convertir_costo(texto):
    """
    Acepta ejemplos como:
    2000, 2000.00, 2,000, 2,000.00,
    2.000,00 y 2000,50.
    """
    texto = texto.strip().replace(" ", "").replace("$", "")

    if not texto:
        raise ValueError("Debes ingresar el costo.")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")

    elif "," in texto:
        partes = texto.split(",")

        if len(partes) == 2 and len(partes[1]) == 3:
            texto = "".join(partes)
        elif len(partes) == 2 and len(partes[1]) in (1, 2):
            texto = partes[0] + "." + partes[1]
        else:
            raise ValueError("El formato del costo no es válido.")

    try:
        costo = Decimal(texto)
    except InvalidOperation:
        raise ValueError(
            "El costo no tiene un formato válido.\n"
            "Ejemplos: 2000, 2000.00 o 2,000.00"
        )

    if not costo.is_finite() or costo <= 0:
        raise ValueError("El costo debe ser mayor que cero.")

    if costo.as_tuple().exponent < -2:
        raise ValueError("El costo admite como máximo dos decimales.")

    return costo.quantize(Decimal("0.01"))


# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def obtener_procedimientos(termino=None):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        consulta = """
            SELECT
                IdProcedimiento,
                NombreProcedimiento,
                Descripcion,
                Costo
            FROM dbo.Procedimiento
        """

        if termino:
            patron = f"%{termino}%"
            consulta += """
                WHERE NombreProcedimiento LIKE ?
                   OR Descripcion LIKE ?
                   OR CAST(IdProcedimiento AS VARCHAR(20)) LIKE ?
            """
            parametros = (patron, patron, patron)
        else:
            parametros = ()

        consulta += " ORDER BY NombreProcedimiento"

        cursor.execute(consulta, parametros)
        return cursor.fetchall()

    finally:
        conexion.close()


def registrar_procedimiento(nombre, descripcion, costo):
    if not nombre.strip():
        raise ValueError("El nombre del procedimiento es obligatorio.")

    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO dbo.Procedimiento
                (NombreProcedimiento, Descripcion, Costo)
            VALUES (?, ?, ?)
        """, (
            nombre.strip(),
            descripcion.strip() or None,
            costo
        ))
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def eliminar_procedimiento(id_procedimiento):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM dbo.Procedimiento
            WHERE IdProcedimiento = ?
        """, (id_procedimiento,))

        if cursor.rowcount == 0:
            raise ValueError("El procedimiento seleccionado ya no existe.")

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ============================================================
# PANEL DE PROCEDIMIENTOS
# ============================================================

class PanelProcedimientos(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=NEGRO, corner_radius=0)

        self.procedimientos = {}
        self.seleccion_id = None

        self.crear_interfaz()
        self.cargar_procedimientos()

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
            text="GESTIÓN DE PROCEDIMIENTOS",
            font=("Georgia", 23, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=18, pady=(14, 3))

        ctk.CTkLabel(
            encabezado,
            text="Consulta y administra el catálogo de procedimientos dentales.",
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=18, pady=(0, 14))

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=16, pady=(0, 8))

        self.buscar_var = ctk.StringVar()
        self.buscar_entry = ctk.CTkEntry(
            barra,
            textvariable=self.buscar_var,
            placeholder_text="Buscar por nombre, descripción o ID...",
            height=38,
            fg_color=PANEL,
            text_color=TEXTO,
            border_color=DORADO,
            placeholder_text_color="#6A9690"
        )
        self.buscar_entry.pack(side="left", fill="x", expand=True, padx=(0, 7))
        self.buscar_entry.bind(
            "<Return>", lambda evento: self.buscar_procedimientos()
        )

        self.boton(
            barra, "Buscar", self.buscar_procedimientos,
            contorno=True, ancho=95
        ).pack(side="left", padx=4)

        self.boton(
            barra, "Mostrar todos", self.cargar_procedimientos,
            contorno=True, ancho=115
        ).pack(side="left", padx=4)

        self.boton(
            barra, "+ Nuevo procedimiento", self.nuevo_procedimiento, ancho=175
        ).pack(side="left", padx=4)

        self.boton(
            barra, "Eliminar", self.eliminar_seleccionado,
            contorno=True, ancho=90
        ).pack(side="left", padx=4)

        self.total_label = ctk.CTkLabel(
            self,
            text="Procedimientos encontrados: 0",
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

        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            pie,
            text="Selecciona un procedimiento para ver sus detalles.",
            font=("Arial", 11),
            text_color=TEXTO
        ).pack(side="left")

        ctk.CTkLabel(
            pie,
            text="SONRISA SANA  |  Catálogo dental",
            font=("Arial", 10),
            text_color=DORADO
        ).pack(side="right")

    # --------------------------------------------------------
    # TABLA
    # --------------------------------------------------------

    def crear_tabla(self):
        self.tabla_contenedor.grid_columnconfigure(0, weight=1)
        self.tabla_contenedor.grid_rowconfigure(1, weight=1)

        self.columnas = [
            ("id", "ID", 75),
            ("nombre", "Procedimiento", 240),
            ("descripcion", "Descripción", 420),
            ("costo", "Costo", 140)
        ]

        cabecera = ctk.CTkFrame(
            self.tabla_contenedor, fg_color="#DDF3EF", corner_radius=4
        )
        cabecera.grid(row=0, column=0, sticky="ew", padx=7, pady=(7, 0))

        for indice, (_, titulo, ancho) in enumerate(self.columnas):
            cabecera.grid_columnconfigure(indice, weight=1, minsize=ancho)

            ctk.CTkLabel(
                cabecera,
                text=titulo,
                font=("Arial", 11, "bold"),
                text_color=DORADO_CLARO,
                anchor="center"
            ).grid(row=0, column=indice, sticky="ew", padx=4, pady=10)

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

        for indice, (_, _, ancho) in enumerate(self.columnas):
            self.lista_filas.grid_columnconfigure(indice, weight=1, minsize=ancho)

    def mostrar_filas(self, filas):
        for widget in self.lista_filas.winfo_children():
            widget.destroy()

        self.procedimientos.clear()
        self.seleccion_id = None

        for numero, fila in enumerate(filas):
            id_procedimiento = int(fila[0])
            costo = (
                f"${Decimal(str(fila[3])):,.2f}"
                if fila[3] is not None
                else "$0.00"
            )

            valores = [
                id_procedimiento,
                fila[1] or "",
                fila[2] or "",
                costo
            ]

            color_fila = PANEL_CLARO if numero % 2 == 0 else NEGRO

            fila_frame = ctk.CTkFrame(
                self.lista_filas, fg_color=color_fila, corner_radius=3
            )
            fila_frame.grid(
                row=numero, column=0, columnspan=len(self.columnas),
                sticky="ew", pady=1
            )

            for indice, (_, _, ancho) in enumerate(self.columnas):
                fila_frame.grid_columnconfigure(indice, weight=1, minsize=ancho)

            self.procedimientos[id_procedimiento] = {
                "id": id_procedimiento,
                "nombre": fila[1] or "",
                "descripcion": fila[2] or "",
                "costo": costo
            }

            fila_frame.bind(
                "<Button-1>",
                lambda evento, ident=id_procedimiento: self.seleccionar_fila(ident)
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
                    row=0, column=indice, sticky="ew", padx=4, pady=11
                )
                etiqueta.bind(
                    "<Button-1>",
                    lambda evento, ident=id_procedimiento: self.seleccionar_fila(ident)
                )

        self.total_label.configure(
            text=f"Procedimientos encontrados: {len(filas)}"
        )

    def seleccionar_fila(self, id_procedimiento):
        self.seleccion_id = id_procedimiento

        for widget in self.lista_filas.winfo_children():
            widget.configure(fg_color=PANEL_CLARO)

        for widget in self.lista_filas.winfo_children():
            etiquetas = widget.winfo_children()

            if etiquetas:
                texto_id = etiquetas[0].cget("text")

                if str(texto_id) == str(id_procedimiento):
                    widget.configure(fg_color=SELECCION)
                    break

    # --------------------------------------------------------
    # ELIMINAR PROCEDIMIENTO
    # --------------------------------------------------------

    def eliminar_seleccionado(self):
        ventana = self.winfo_toplevel()
        id_procedimiento = self.seleccion_id

        if id_procedimiento is None:
            messagebox.showwarning(
                "Selecciona un procedimiento",
                "Primero selecciona una fila de la tabla.",
                parent=ventana
            )
            return

        nombre = self.procedimientos[id_procedimiento]["nombre"]
        confirmar = messagebox.askyesno(
            "Eliminar procedimiento",
            f"¿Deseas eliminar definitivamente «{nombre}» "
            f"(ID {id_procedimiento})?",
            parent=ventana,
            default="no"
        )

        if not confirmar:
            return

        try:
            eliminar_procedimiento(id_procedimiento)

        except ValueError as error:
            messagebox.showwarning(
                "Procedimiento no disponible", str(error), parent=ventana
            )
            self.cargar_procedimientos()
            return

        except Exception as error:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar «{nombre}».\n\n{error}",
                parent=ventana
            )
            return

        self.cargar_procedimientos()
        messagebox.showinfo(
            "Procedimiento eliminado",
            f"Se eliminó «{nombre}» (ID {id_procedimiento}).",
            parent=ventana
        )

    # --------------------------------------------------------
    # CONSULTAR Y BUSCAR
    # --------------------------------------------------------

    def cargar_procedimientos(self):
        try:
            filas = obtener_procedimientos()
            self.mostrar_filas(filas)

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron consultar los procedimientos.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    def buscar_procedimientos(self):
        termino = self.buscar_var.get().strip()

        try:
            filas = obtener_procedimientos(termino or None)
            self.mostrar_filas(filas)

            if termino and not filas:
                messagebox.showinfo(
                    "Sin resultados",
                    f"No se encontraron procedimientos para: {termino}",
                    parent=self.winfo_toplevel()
                )

        except Exception as error:
            messagebox.showerror(
                "Error de búsqueda",
                f"No se pudo completar la búsqueda.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # REGISTRAR PROCEDIMIENTO
    # --------------------------------------------------------

    def nuevo_procedimiento(self):
        ventana = ctk.CTkToplevel(self.winfo_toplevel())
        ventana.title("Nuevo procedimiento | Sonrisa Sana")
        ventana.geometry("540x490")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="REGISTRAR PROCEDIMIENTO",
            font=("Georgia", 22, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(22, 18))

        formulario = ctk.CTkFrame(
            ventana, fg_color=PANEL, border_color=DORADO,
            border_width=1, corner_radius=12
        )
        formulario.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        campos = {}
        definiciones = [
            ("Nombre del procedimiento *", "nombre", "Ejemplo: Limpieza dental"),
            ("Descripción (opcional)", "descripcion", "Detalles del procedimiento"),
            ("Costo *", "costo", "Ejemplo: 2000 o 2,000.00")
        ]

        for titulo, clave, ejemplo in definiciones:
            ctk.CTkLabel(
                formulario,
                text=titulo,
                text_color=TEXTO,
                font=("Arial", 11, "bold")
            ).pack(anchor="w", padx=20, pady=(9, 3))

            campo = ctk.CTkEntry(
                formulario,
                height=36,
                fg_color=PANEL_CLARO,
                text_color=TEXTO,
                border_color=DORADO,
                placeholder_text=ejemplo,
                placeholder_text_color="#6A9690"
            )
            campo.pack(fill="x", padx=20, pady=(0, 4))
            campos[clave] = campo

        def guardar():
            nombre = campos["nombre"].get().strip()
            descripcion = campos["descripcion"].get().strip()
            costo_texto = campos["costo"].get().strip()

            if not nombre or not costo_texto:
                messagebox.showwarning(
                    "Datos obligatorios",
                    "Completa el nombre y el costo.",
                    parent=ventana
                )
                return

            try:
                costo = convertir_costo(costo_texto)

            except ValueError as error:
                messagebox.showwarning("Costo inválido", str(error), parent=ventana)
                return

            try:
                registrar_procedimiento(nombre, descripcion, costo)

                messagebox.showinfo(
                    "Sonrisa Sana",
                    "Procedimiento registrado correctamente.",
                    parent=ventana
                )
                ventana.destroy()
                self.cargar_procedimientos()

            except Exception as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No se pudo registrar el procedimiento.\n\n{error}",
                    parent=ventana
                )

        self.boton(
            formulario, "GUARDAR PROCEDIMIENTO", guardar, ancho=220
        ).pack(fill="x", padx=20, pady=(15, 7))

        self.boton(
            formulario, "Cancelar", ventana.destroy, contorno=True, ancho=220
        ).pack(fill="x", padx=20, pady=(0, 14))


# ============================================================
# EJECUCIÓN INDEPENDIENTE PARA PRUEBAS
# ============================================================

if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Procedimientos")
    ventana.geometry("1250x750")
    ventana.minsize(1000, 620)
    ventana.configure(fg_color=NEGRO)

    panel = PanelProcedimientos(ventana)
    panel.pack(fill="both", expand=True)

    ventana.mainloop()