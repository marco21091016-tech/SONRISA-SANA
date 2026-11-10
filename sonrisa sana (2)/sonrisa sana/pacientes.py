import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import re
import customtkinter as ctk
import pyodbc

from conexion import conectar


# =========================================================
# CONFIGURACIÓN VISUAL: TURQUESA Y BLANCO
# =========================================================

NEGRO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
DORADO = "#159F95"
DORADO_CLARO = "#087F78"
TEXTO = "#263B3A"
BLANCO = "#FFFFFF"
BORDE = "#B8DED8"
SELECCION = "#BFEDE6"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# =========================================================
# CONSULTAS Y OPERACIONES DE BASE DE DATOS
# =========================================================

def consultar_pacientes(busqueda=""):
    sql = """
        SELECT
            IdPaciente,
            Nombre,
            Apellidos,
            FechaNacimiento,
            TelefonoPrincipal,
            Correo,
            FechaRegistro
        FROM dbo.Paciente
    """

    parametros = []

    if busqueda.strip():
        sql += """
            WHERE Nombre LIKE ?
               OR Apellidos LIKE ?
               OR TelefonoPrincipal LIKE ?
               OR Correo LIKE ?
        """
        termino = f"%{busqueda.strip()}%"
        parametros = [termino] * 4

    sql += " ORDER BY Apellidos, Nombre"

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()


def guardar_paciente(datos, id_paciente=None):
    with conectar() as conexion:
        cursor = conexion.cursor()

        if id_paciente is None:
            cursor.execute("""
                INSERT INTO dbo.Paciente
                (
                    Nombre,
                    Apellidos,
                    FechaNacimiento,
                    TelefonoPrincipal,
                    Correo,
                    FechaRegistro
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datos["nombre"],
                datos["apellidos"],
                datos["nacimiento"],
                datos["telefono"],
                datos["correo"],
                date.today()
            ))
        else:
            cursor.execute("""
                UPDATE dbo.Paciente
                SET Nombre = ?,
                    Apellidos = ?,
                    FechaNacimiento = ?,
                    TelefonoPrincipal = ?,
                    Correo = ?
                WHERE IdPaciente = ?
            """, (
                datos["nombre"],
                datos["apellidos"],
                datos["nacimiento"],
                datos["telefono"],
                datos["correo"],
                id_paciente
            ))


def eliminar_paciente(id_paciente):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM dbo.Paciente
            WHERE IdPaciente = ?
        """, (id_paciente,))

        if cursor.rowcount == 0:
            raise ValueError("El paciente seleccionado ya no existe.")

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# =========================================================
# PANEL INTEGRADO DE PACIENTES
# =========================================================

class PanelPacientes(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=NEGRO,
            corner_radius=0,
            **kwargs
        )

        self.pack_propagate(False)
        self.crear_interfaz()
        self.cargar_pacientes()

    # -----------------------------------------------------
    # INTERFAZ
    # -----------------------------------------------------

    def crear_interfaz(self):
        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDE
        )
        encabezado.pack(fill="x", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            encabezado,
            text="PACIENTES",
            font=("Georgia", 27, "bold"),
            text_color=DORADO
        ).pack(anchor="w", padx=22, pady=(15, 2))

        ctk.CTkLabel(
            encabezado,
            text="REGISTRO, CONSULTA Y ADMINISTRACIÓN DE PACIENTES",
            font=("Arial", 12, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=24, pady=(0, 15))

        # Barra de búsqueda
        barra = ctk.CTkFrame(self, fg_color=NEGRO)
        barra.pack(fill="x", padx=16, pady=(0, 10))

        self.entrada_busqueda = ctk.CTkEntry(
            barra,
            placeholder_text="Buscar por nombre, apellidos, teléfono o correo...",
            height=40,
            fg_color=PANEL,
            border_color=BORDE,
            text_color=TEXTO,
            placeholder_text_color=DORADO_CLARO
        )
        self.entrada_busqueda.pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self.entrada_busqueda.bind("<Return>", lambda event: self.buscar())

        ctk.CTkButton(
            barra,
            text="Buscar",
            width=100,
            height=40,
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color=BLANCO,
            command=self.buscar
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            barra,
            text="Mostrar todos",
            width=120,
            height=40,
            fg_color=PANEL,
            hover_color=PANEL_CLARO,
            text_color=DORADO_CLARO,
            border_width=1,
            border_color=BORDE,
            command=self.mostrar_todos
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            barra,
            text="+ Nuevo paciente",
            width=145,
            height=40,
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color=BLANCO,
            command=self.abrir_nuevo
        ).pack(side="left", padx=(8, 0))

        self.etiqueta_total = ctk.CTkLabel(
            self,
            text="Pacientes encontrados: 0",
            font=("Arial", 14, "bold"),
            text_color=DORADO_CLARO
        )
        self.etiqueta_total.pack(anchor="w", padx=20, pady=(0, 8))

        # Tabla
        contenedor = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            border_width=1,
            border_color=BORDE,
            corner_radius=8
        )
        contenedor.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        columnas = (
            "ID", "Nombre", "Apellidos", "Nacimiento",
            "Teléfono", "Correo", "Registro"
        )

        estilo = ttk.Style()

        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Pacientes.Treeview",
            background=PANEL,
            foreground=TEXTO,
            fieldbackground=PANEL,
            rowheight=34,
            borderwidth=0,
            font=("Arial", 10)
        )
        estilo.configure(
            "Pacientes.Treeview.Heading",
            background=PANEL_CLARO,
            foreground=DORADO_CLARO,
            font=("Arial", 10, "bold"),
            relief="flat"
        )
        estilo.map(
            "Pacientes.Treeview",
            background=[("selected", SELECCION)],
            foreground=[("selected", TEXTO)]
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=columnas,
            show="headings",
            style="Pacientes.Treeview"
        )

        anchos = (65, 130, 165, 115, 130, 240, 115)

        for columna, ancho in zip(columnas, anchos):
            self.tabla.heading(columna, text=columna)
            self.tabla.column(
                columna, width=ancho, minwidth=65, anchor="center"
            )

        scroll_y = ttk.Scrollbar(
            contenedor, orient="vertical", command=self.tabla.yview
        )
        scroll_x = ttk.Scrollbar(
            contenedor, orient="horizontal", command=self.tabla.xview
        )
        self.tabla.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        self.tabla.bind(
            "<Double-1>", lambda event: self.editar_seleccionado()
        )

        # Barra inferior
        inferior = ctk.CTkFrame(self, fg_color=NEGRO)
        inferior.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkButton(
            inferior,
            text="Editar paciente seleccionado",
            height=36,
            fg_color=PANEL,
            hover_color=PANEL_CLARO,
            text_color=DORADO_CLARO,
            border_width=1,
            border_color=BORDE,
            command=self.editar_seleccionado
        ).pack(side="left")

        ctk.CTkButton(
            inferior,
            text="Eliminar",
            height=36,
            fg_color=PANEL,
            hover_color=PANEL_CLARO,
            text_color=DORADO_CLARO,
            border_width=1,
            border_color=BORDE,
            command=self.eliminar_seleccionado
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            inferior,
            text="Información almacenada en SonrisaSana",
            text_color=DORADO_CLARO,
            font=("Arial", 11)
        ).pack(side="right", padx=5)

    # -----------------------------------------------------
    # BÚSQUEDA Y CONSULTA
    # -----------------------------------------------------

    def buscar(self):
        self.cargar_pacientes(self.entrada_busqueda.get())

    def mostrar_todos(self):
        self.entrada_busqueda.delete(0, "end")
        self.cargar_pacientes()

    def cargar_pacientes(self, busqueda=""):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            pacientes = consultar_pacientes(busqueda)

            for paciente in pacientes:
                valores = [
                    "" if valor is None else str(valor)
                    for valor in paciente
                ]
                self.tabla.insert("", "end", values=valores)

            self.etiqueta_total.configure(
                text=f"Pacientes encontrados: {len(pacientes)}"
            )

        except pyodbc.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron consultar los pacientes.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # -----------------------------------------------------
    # ELIMINAR PACIENTE
    # -----------------------------------------------------

    def eliminar_seleccionado(self):
        seleccion = self.tabla.selection()
        ventana = self.winfo_toplevel()

        if len(seleccion) != 1:
            messagebox.showwarning(
                "Selecciona un paciente",
                "Selecciona una sola fila de la tabla para eliminarla.",
                parent=ventana
            )
            return

        valores = self.tabla.item(seleccion[0], "values")
        id_paciente = int(valores[0])
        nombre_completo = f"{valores[1]} {valores[2]}"

        confirmar = messagebox.askyesno(
            "Eliminar paciente",
            f"¿Deseas eliminar definitivamente a {nombre_completo} "
            f"(ID {id_paciente})?",
            parent=ventana,
            default="no"
        )

        if not confirmar:
            return

        try:
            eliminar_paciente(id_paciente)

        except ValueError as error:
            messagebox.showwarning(
                "Paciente no disponible", str(error), parent=ventana
            )
            self.buscar()
            return

        except pyodbc.IntegrityError as error:
            messagebox.showerror(
                "No se pudo eliminar el paciente",
                f"SQL Server impidió eliminar a {nombre_completo}. "
                "Revisa si tiene citas, tratamientos u otros registros "
                f"vinculados.\n\n{error}",
                parent=ventana
            )
            return

        except pyodbc.Error as error:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar al paciente.\n\n{error}",
                parent=ventana
            )
            return

        self.buscar()
        messagebox.showinfo(
            "Paciente eliminado",
            f"Se eliminó a {nombre_completo} (ID {id_paciente}).",
            parent=ventana
        )

    # -----------------------------------------------------
    # FORMULARIOS
    # -----------------------------------------------------

    def abrir_nuevo(self):
        self.abrir_formulario()

    def editar_seleccionado(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Selecciona un paciente",
                "Selecciona primero una fila de la tabla.",
                parent=self.winfo_toplevel()
            )
            return

        valores = self.tabla.item(seleccion[0], "values")

        self.abrir_formulario(
            id_paciente=int(valores[0]),
            valores=valores
        )

    def abrir_formulario(self, id_paciente=None, valores=None):
        formulario = ctk.CTkToplevel(self.winfo_toplevel())

        formulario.title(
            "Editar paciente" if id_paciente else "Nuevo paciente"
        )
        formulario.geometry("520x570")
        formulario.resizable(False, False)
        formulario.configure(fg_color=NEGRO)
        formulario.transient(self.winfo_toplevel())
        formulario.grab_set()

        ctk.CTkLabel(
            formulario,
            text="EDITAR PACIENTE" if id_paciente else "REGISTRAR PACIENTE",
            font=("Georgia", 22, "bold"),
            text_color=DORADO
        ).pack(pady=(22, 16))

        campos = [
            ("Nombre *", "nombre"),
            ("Apellidos *", "apellidos"),
            ("Fecha de nacimiento (AAAA-MM-DD)", "nacimiento"),
            ("Teléfono principal *", "telefono"),
            ("Correo electrónico (opcional)", "correo")
        ]
        entradas = {}

        for etiqueta, clave in campos:
            ctk.CTkLabel(
                formulario,
                text=etiqueta,
                text_color=DORADO_CLARO,
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=35, pady=(6, 2))

            entrada = ctk.CTkEntry(
                formulario,
                height=35,
                fg_color=PANEL,
                border_color=BORDE,
                text_color=TEXTO,
                placeholder_text_color=DORADO_CLARO
            )
            entrada.pack(fill="x", padx=35)
            entradas[clave] = entrada

        if valores:
            valores_iniciales = {
                "nombre": valores[1],
                "apellidos": valores[2],
                "nacimiento": valores[3],
                "telefono": valores[4],
                "correo": valores[5]
            }

            for clave, valor in valores_iniciales.items():
                if valor is not None:
                    entradas[clave].insert(0, str(valor))

        def guardar():
            nombre = entradas["nombre"].get().strip()
            apellidos = entradas["apellidos"].get().strip()
            nacimiento_texto = entradas["nacimiento"].get().strip()
            telefono = entradas["telefono"].get().strip()
            correo = entradas["correo"].get().strip()

            if not nombre or not apellidos or not telefono:
                messagebox.showwarning(
                    "Datos obligatorios",
                    "Completa nombre, apellidos y teléfono.",
                    parent=formulario
                )
                return

            nacimiento = None

            if nacimiento_texto:
                try:
                    nacimiento = date.fromisoformat(nacimiento_texto)

                    if nacimiento > date.today():
                        raise ValueError

                except ValueError:
                    messagebox.showwarning(
                        "Fecha inválida",
                        "Usa AAAA-MM-DD y una fecha que no sea futura.",
                        parent=formulario
                    )
                    return

            if correo and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
                messagebox.showwarning(
                    "Correo inválido",
                    "Revisa el formato del correo electrónico.",
                    parent=formulario
                )
                return

            datos = {
                "nombre": nombre,
                "apellidos": apellidos,
                "nacimiento": nacimiento,
                "telefono": telefono,
                "correo": correo or None
            }

            try:
                guardar_paciente(datos, id_paciente)

                messagebox.showinfo(
                    "Sonrisa Sana",
                    "Paciente guardado correctamente.",
                    parent=formulario
                )
                formulario.destroy()
                self.cargar_pacientes(self.entrada_busqueda.get())

            except pyodbc.IntegrityError as error:
                messagebox.showerror(
                    "Datos duplicados o inválidos",
                    "SQL Server rechazó el registro. Comprueba "
                    "que el correo no esté registrado y que los "
                    f"datos cumplan las reglas de la base de datos.\n\n{error}",
                    parent=formulario
                )

            except pyodbc.Error as error:
                messagebox.showerror(
                    "Error al guardar", str(error), parent=formulario
                )

        ctk.CTkButton(
            formulario,
            text="Guardar paciente",
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color=BLANCO,
            height=40,
            command=guardar
        ).pack(fill="x", padx=35, pady=(20, 8))

        ctk.CTkButton(
            formulario,
            text="Cancelar",
            fg_color=PANEL,
            hover_color=PANEL_CLARO,
            text_color=DORADO_CLARO,
            border_color=BORDE,
            border_width=1,
            height=35,
            command=formulario.destroy
        ).pack(fill="x", padx=35, pady=(0, 18))


# =========================================================
# EJECUCIÓN INDIVIDUAL PARA PRUEBAS
# =========================================================

if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Gestión de pacientes")
    ventana.geometry("1250x720")
    ventana.minsize(1000, 580)
    ventana.configure(fg_color=NEGRO)

    panel = PanelPacientes(ventana)
    panel.pack(fill="both", expand=True)

    ventana.mainloop()