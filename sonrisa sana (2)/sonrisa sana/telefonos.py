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
BORDE = "#B8DED8"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# CONSULTAS A LA BASE DE DATOS
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


def obtener_telefonos(termino=None):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        consulta = """
            SELECT
                tp.IdTelefono,
                tp.IdPaciente,
                p.Nombre,
                p.Apellidos,
                tp.NumeroTelefono,
                tp.TipoTelefono
            FROM dbo.Telefono_Paciente AS tp
            INNER JOIN dbo.Paciente AS p
                ON p.IdPaciente = tp.IdPaciente
        """
        parametros = ()

        if termino:
            patron = f"%{termino}%"
            consulta += """
                WHERE p.Nombre LIKE ?
                   OR p.Apellidos LIKE ?
                   OR CONCAT(p.Nombre, ' ', p.Apellidos) LIKE ?
                   OR tp.NumeroTelefono LIKE ?
                   OR tp.TipoTelefono LIKE ?
                   OR CAST(tp.IdTelefono AS VARCHAR(20)) LIKE ?
                   OR CAST(tp.IdPaciente AS VARCHAR(20)) LIKE ?
            """
            parametros = (patron,) * 7

        consulta += """
            ORDER BY p.Apellidos, p.Nombre, tp.IdTelefono
        """

        cursor.execute(consulta, parametros)
        return cursor.fetchall()

    finally:
        conexion.close()


def registrar_telefono(id_paciente, numero, tipo):
    numero = numero.strip()

    if not numero:
        raise ValueError("Debes escribir el número telefónico.")

    if not re.fullmatch(r"[0-9]+", numero):
        raise ValueError("El teléfono debe contener solamente dígitos.")

    if tipo not in ("Trabajo", "Casa", "Personal"):
        raise ValueError("Selecciona un tipo de teléfono válido.")

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        # Comprobar que no exista el mismo número para ese paciente.
        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.Telefono_Paciente
            WHERE IdPaciente = ?
              AND NumeroTelefono = ?
        """, (id_paciente, numero))

        if cursor.fetchone()[0] > 0:
            raise ValueError(
                "Este número ya está registrado para "
                "el paciente seleccionado."
            )

        cursor.execute("""
            INSERT INTO dbo.Telefono_Paciente
                (IdPaciente, NumeroTelefono, TipoTelefono)
            VALUES (?, ?, ?)
        """, (id_paciente, numero, tipo))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def eliminar_telefono(id_telefono):
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM dbo.Telefono_Paciente
            WHERE IdTelefono = ?
        """, (id_telefono,))

        if cursor.rowcount == 0:
            raise ValueError("El teléfono seleccionado ya no existe.")

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ============================================================
# PANEL DE TELÉFONOS
# ============================================================

class PanelTelefonos(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=NEGRO, corner_radius=0)

        self.filas = {}
        self.seleccion_id = None

        self.crear_interfaz()
        self.cargar_telefonos()

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
    # INTERFAZ
    # --------------------------------------------------------

    def crear_interfaz(self):
        encabezado = ctk.CTkFrame(
            self, fg_color=PANEL, border_color=DORADO,
            border_width=1, corner_radius=12
        )
        encabezado.pack(fill="x", padx=16, pady=(12, 10))

        ctk.CTkLabel(
            encabezado,
            text="GESTIÓN DE TELÉFONOS",
            font=("Georgia", 23, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=18, pady=(14, 3))

        ctk.CTkLabel(
            encabezado,
            text="Administra los números de contacto asociados a cada paciente.",
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=18, pady=(0, 14))

        # Barra de búsqueda y acciones.
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=16, pady=(0, 8))

        self.buscar_var = ctk.StringVar()

        self.buscar_entry = ctk.CTkEntry(
            barra,
            textvariable=self.buscar_var,
            placeholder_text="Buscar por paciente, teléfono, tipo o ID...",
            height=38,
            fg_color=PANEL,
            text_color=TEXTO,
            border_color=DORADO,
            placeholder_text_color="#6A9690"
        )
        self.buscar_entry.pack(side="left", fill="x", expand=True, padx=(0, 7))
        self.buscar_entry.bind(
            "<Return>", lambda evento: self.buscar_telefonos()
        )

        self.boton(
            barra, "Buscar", self.buscar_telefonos, contorno=True, ancho=90
        ).pack(side="left", padx=4)

        self.boton(
            barra, "Mostrar todos", self.cargar_telefonos,
            contorno=True, ancho=115
        ).pack(side="left", padx=4)

        self.boton(
            barra, "+ Nuevo teléfono", self.nuevo_telefono, ancho=155
        ).pack(side="left", padx=4)

        self.boton(
            barra, "Eliminar", self.eliminar_seleccionado,
            contorno=True, ancho=90
        ).pack(side="left", padx=4)

        self.total_label = ctk.CTkLabel(
            self,
            text="Teléfonos encontrados: 0",
            font=("Arial", 12, "bold"),
            text_color=TEXTO
        )
        self.total_label.pack(anchor="w", padx=20, pady=(5, 8))

        # Contenedor de la tabla.
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

        self.detalle_label = ctk.CTkLabel(
            pie,
            text="Selecciona un teléfono para ver sus datos.",
            font=("Arial", 11),
            text_color=TEXTO
        )
        self.detalle_label.pack(side="left")

        ctk.CTkLabel(
            pie,
            text="SONRISA SANA  |  Contacto de pacientes",
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
            ("id", "ID teléfono", 85),
            ("id_paciente", "ID paciente", 95),
            ("paciente", "Paciente", 230),
            ("numero", "Número telefónico", 180),
            ("tipo", "Tipo", 140)
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
                font=("Arial", 10, "bold"),
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
            self.lista_filas.grid_columnconfigure(
                indice, weight=1, minsize=ancho
            )

    def mostrar_filas(self, filas):
        for widget in self.lista_filas.winfo_children():
            widget.destroy()

        self.filas.clear()
        self.seleccion_id = None
        self.detalle_label.configure(
            text="Selecciona un teléfono para ver sus datos."
        )

        for numero_fila, fila in enumerate(filas):
            id_telefono = int(fila[0])
            paciente = f"{fila[2] or ''} {fila[3] or ''}".strip()

            valores = [
                fila[0],
                fila[1],
                paciente,
                fila[4] or "",
                fila[5] or ""
            ]

            color_fila = PANEL_CLARO if numero_fila % 2 == 0 else NEGRO
            fila_frame = ctk.CTkFrame(
                self.lista_filas, fg_color=color_fila, corner_radius=3
            )
            fila_frame.grid(
                row=numero_fila, column=0, columnspan=len(self.columnas),
                sticky="ew", pady=1
            )

            for indice, (_, _, ancho) in enumerate(self.columnas):
                fila_frame.grid_columnconfigure(indice, weight=1, minsize=ancho)

            self.filas[id_telefono] = {
                "frame": fila_frame,
                "color": color_fila,
                "datos": valores
            }

            fila_frame.bind(
                "<Button-1>",
                lambda evento, ident=id_telefono: self.seleccionar_fila(ident)
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
                    lambda evento, ident=id_telefono: self.seleccionar_fila(ident)
                )

        self.total_label.configure(
            text=f"Teléfonos encontrados: {len(filas)}"
        )

    def seleccionar_fila(self, id_telefono):
        self.seleccion_id = id_telefono

        for ident, informacion in self.filas.items():
            informacion["frame"].configure(
                fg_color=SELECCION if ident == id_telefono else informacion["color"]
            )

        datos = self.filas[id_telefono]["datos"]
        self.detalle_label.configure(
            text=(
                f"Teléfono seleccionado: {datos[3]} "
                f"| Paciente: {datos[2]} "
                f"| Tipo: {datos[4]}"
            )
        )

    # --------------------------------------------------------
    # ELIMINAR TELÉFONO
    # --------------------------------------------------------

    def eliminar_seleccionado(self):
        ventana = self.winfo_toplevel()
        id_telefono = self.seleccion_id

        if id_telefono is None:
            messagebox.showwarning(
                "Selecciona un teléfono",
                "Primero selecciona una fila de la tabla.",
                parent=ventana
            )
            return

        datos = self.filas[id_telefono]["datos"]
        paciente = datos[2]
        numero = datos[3]

        confirmar = messagebox.askyesno(
            "Eliminar teléfono",
            f"¿Deseas eliminar definitivamente el teléfono {numero} "
            f"de {paciente} (ID teléfono {id_telefono})?",
            parent=ventana,
            default="no"
        )

        if not confirmar:
            return

        try:
            eliminar_telefono(id_telefono)

        except ValueError as error:
            messagebox.showwarning(
                "Teléfono no disponible", str(error), parent=ventana
            )
            self.cargar_telefonos()
            return

        except Exception as error:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar el teléfono {numero}.\n\n{error}",
                parent=ventana
            )
            return

        self.cargar_telefonos()
        messagebox.showinfo(
            "Teléfono eliminado",
            f"Se eliminó el teléfono {numero} de {paciente}.",
            parent=ventana
        )

    # --------------------------------------------------------
    # CONSULTAR Y BUSCAR
    # --------------------------------------------------------

    def cargar_telefonos(self):
        try:
            filas = obtener_telefonos()
            self.mostrar_filas(filas)

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron consultar los teléfonos.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    def buscar_telefonos(self):
        termino = self.buscar_var.get().strip()

        try:
            filas = obtener_telefonos(termino or None)
            self.mostrar_filas(filas)

            if termino and not filas:
                messagebox.showinfo(
                    "Sin resultados",
                    f"No se encontraron teléfonos para: {termino}",
                    parent=self.winfo_toplevel()
                )

        except Exception as error:
            messagebox.showerror(
                "Error de búsqueda",
                f"No se pudo completar la búsqueda.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # REGISTRAR TELÉFONO
    # --------------------------------------------------------

    def nuevo_telefono(self):
        try:
            pacientes = obtener_pacientes()

        except Exception as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudieron consultar los pacientes.\n\n{error}",
                parent=self.winfo_toplevel()
            )
            return

        if not pacientes:
            messagebox.showwarning(
                "Sin pacientes",
                "Primero debes registrar un paciente.",
                parent=self.winfo_toplevel()
            )
            return

        ventana = ctk.CTkToplevel(self.winfo_toplevel())
        ventana.title("Nuevo teléfono | Sonrisa Sana")
        ventana.geometry("540x450")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="REGISTRAR TELÉFONO",
            font=("Georgia", 22, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(22, 18))

        formulario = ctk.CTkFrame(
            ventana, fg_color=PANEL, border_color=DORADO,
            border_width=1, corner_radius=12
        )
        formulario.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        ctk.CTkLabel(
            formulario,
            text="Paciente *",
            text_color=TEXTO,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20, pady=(13, 4))

        opciones = {
            f"{p[0]} | {p[1]} {p[2]}": p[0]
            for p in pacientes
        }
        paciente_var = ctk.StringVar(value=next(iter(opciones)))

        selector = ctk.CTkOptionMenu(
            formulario,
            values=list(opciones.keys()),
            variable=paciente_var,
            height=36,
            fg_color=DORADO,
            button_color=DORADO_CLARO,
            button_hover_color="#0E8F85",
            text_color=BLANCO,
            dropdown_fg_color=PANEL,
            dropdown_text_color=TEXTO
        )
        selector.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(
            formulario,
            text="Número telefónico * (solo dígitos)",
            text_color=TEXTO,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20, pady=(2, 4))

        numero_entry = ctk.CTkEntry(
            formulario,
            height=36,
            placeholder_text="Ejemplo: 7771112233",
            fg_color=PANEL_CLARO,
            text_color=TEXTO,
            border_color=DORADO,
            placeholder_text_color="#6A9690"
        )
        numero_entry.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(
            formulario,
            text="Tipo de teléfono *",
            text_color=TEXTO,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 4))

        tipo_var = ctk.StringVar(value="Personal")
        selector_tipo = ctk.CTkOptionMenu(
            formulario,
            values=["Trabajo", "Casa", "Personal"],
            variable=tipo_var,
            height=36,
            fg_color=DORADO,
            button_color=DORADO_CLARO,
            button_hover_color="#0E8F85",
            text_color=BLANCO,
            dropdown_fg_color=PANEL,
            dropdown_text_color=TEXTO
        )
        selector_tipo.pack(fill="x", padx=20, pady=(0, 12))

        def guardar():
            seleccion = paciente_var.get()
            numero = numero_entry.get().strip()
            tipo = tipo_var.get()

            if seleccion not in opciones:
                messagebox.showwarning(
                    "Paciente inválido",
                    "Selecciona un paciente de la lista.",
                    parent=ventana
                )
                return

            if not numero:
                messagebox.showwarning(
                    "Dato obligatorio",
                    "Escribe el número telefónico.",
                    parent=ventana
                )
                return

            if not re.fullmatch(r"[0-9]+", numero):
                messagebox.showwarning(
                    "Número inválido",
                    "El teléfono debe contener solamente dígitos, "
                    "sin espacios, guiones ni paréntesis.",
                    parent=ventana
                )
                return

            if tipo not in ("Trabajo", "Casa", "Personal"):
                messagebox.showwarning(
                    "Tipo inválido",
                    "Selecciona Trabajo, Casa o Personal.",
                    parent=ventana
                )
                return

            try:
                registrar_telefono(opciones[seleccion], numero, tipo)

                messagebox.showinfo(
                    "Sonrisa Sana",
                    "Teléfono registrado correctamente.",
                    parent=ventana
                )
                ventana.destroy()
                self.cargar_telefonos()

            except ValueError as error:
                messagebox.showwarning(
                    "No se pudo registrar", str(error), parent=ventana
                )

            except Exception as error:
                messagebox.showerror(
                    "Error al guardar",
                    f"No se pudo registrar el teléfono.\n\n{error}",
                    parent=ventana
                )

        self.boton(
            formulario, "GUARDAR TELÉFONO", guardar, ancho=220
        ).pack(fill="x", padx=20, pady=(2, 7))

        self.boton(
            formulario, "Cancelar", ventana.destroy, contorno=True, ancho=220
        ).pack(fill="x", padx=20, pady=(0, 12))


# ============================================================
# EJECUCIÓN INDEPENDIENTE PARA PRUEBAS
# ============================================================

if __name__ == "__main__":
    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Teléfonos")
    ventana.geometry("1250x750")
    ventana.minsize(1000, 620)
    ventana.configure(fg_color=NEGRO)

    panel = PanelTelefonos(ventana)
    panel.pack(fill="both", expand=True)

    ventana.mainloop()