import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, datetime, time

from conexion import conectar


# ============================================================
# PALETA DE COLORES: TURQUESA Y BLANCO
# ============================================================

NEGRO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
DORADO = "#159F95"
DORADO_CLARO = "#087F78"
TEXTO = "#263B3A"
BLANCO = "#FFFFFF"
ROJO = "#B83A3A"


# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def obtener_catalogos():
    """Obtiene pacientes, odontólogas y canales disponibles."""
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdPaciente, Nombre, Apellidos
            FROM dbo.Paciente
            ORDER BY Apellidos, Nombre
        """)
        pacientes = cursor.fetchall()

        cursor.execute("""
            SELECT IdOdontologa, Nombre, Apellidos
            FROM dbo.Odontologa
            ORDER BY Apellidos, Nombre
        """)
        odontologas = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT CanalSolicitud
            FROM dbo.Cita
            WHERE CanalSolicitud IS NOT NULL
            ORDER BY CanalSolicitud
        """)
        canales_bd = [
            fila[0] for fila in cursor.fetchall()
            if fila[0]
        ]

        canales = list(dict.fromkeys(
            canales_bd + [
                "Presencial", "Telefono", "Web", "WhatsApp"
            ]
        ))

        return pacientes, odontologas, canales

    finally:
        conexion.close()


def consultar_citas():
    """Devuelve las citas con los nombres del paciente y odontóloga."""
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT
                c.IdCita,
                p.Nombre + ' ' + p.Apellidos AS Paciente,
                o.Nombre + ' ' + o.Apellidos AS Odontologa,
                c.FechaCita,
                c.HoraCita,
                c.Motivo,
                c.CanalSolicitud,
                c.Estado,
                c.MotivoCancelacion
            FROM dbo.Cita AS c
            INNER JOIN dbo.Paciente AS p
                ON c.IdPaciente = p.IdPaciente
            INNER JOIN dbo.Odontologa AS o
                ON c.IdOdontologa = o.IdOdontologa
            ORDER BY c.FechaCita DESC, c.HoraCita DESC
        """)
        return cursor.fetchall()

    finally:
        conexion.close()


def validar_horario_atencion(fecha_cita, hora_cita):
    """Valida la fecha y el horario de atención de la clínica."""
    hoy = date.today()

    if fecha_cita < hoy:
        return False, "No puedes registrar una cita en una fecha pasada."

    if fecha_cita.weekday() == 6:
        return False, "La clínica permanece cerrada los domingos."

    hora_apertura = time(9, 0)
    hora_cierre_manana = time(14, 0)
    hora_apertura_tarde = time(15, 0)
    hora_cierre = time(19, 0)

    horario_manana = (
        hora_apertura <= hora_cita < hora_cierre_manana
    )
    horario_tarde = (
        hora_apertura_tarde <= hora_cita < hora_cierre
    )

    if not (horario_manana or horario_tarde):
        return False, (
            "Horario no disponible.\n\n"
            "Atención de lunes a sábado:\n"
            "09:00 a 14:00 y 15:00 a 19:00."
        )

    return True, ""


def existe_cita_en_horario(
    id_odontologa, fecha_cita, hora_cita, excluir_id=None
):
    """Comprueba si la odontóloga ya tiene una cita en ese horario."""
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT COUNT(*)
            FROM dbo.Cita
            WHERE IdOdontologa = ?
              AND FechaCita = ?
              AND HoraCita = ?
              AND Estado <> 'Cancelada'
        """
        parametros = [id_odontologa, fecha_cita, hora_cita]

        if excluir_id is not None:
            consulta += " AND IdCita <> ?"
            parametros.append(excluir_id)

        cursor.execute(consulta, parametros)
        return cursor.fetchone()[0] > 0

    finally:
        conexion.close()


def registrar_cita(
    id_paciente, id_odontologa, fecha_cita,
    hora_cita, motivo, canal
):
    """Registra una cita nueva."""
    if not motivo.strip():
        raise ValueError("Escribe el motivo de la cita.")

    if not canal:
        raise ValueError("Selecciona el canal de solicitud.")

    valido, mensaje = validar_horario_atencion(
        fecha_cita, hora_cita
    )
    if not valido:
        raise ValueError(mensaje)

    if existe_cita_en_horario(
        id_odontologa, fecha_cita, hora_cita
    ):
        raise ValueError(
            "La odontóloga ya tiene una cita en esa fecha y hora."
        )

    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO dbo.Cita
                (IdPaciente, IdOdontologa, FechaCita, HoraCita,
                 Motivo, CanalSolicitud, Estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            id_paciente,
            id_odontologa,
            fecha_cita,
            hora_cita,
            motivo.strip(),
            canal,
            "Pendiente"
        ))
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def reprogramar_cita(id_cita, fecha_cita, hora_cita):
    """Cambia la fecha y hora de una cita existente."""
    valido, mensaje = validar_horario_atencion(
        fecha_cita, hora_cita
    )
    if not valido:
        raise ValueError(mensaje)

    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT IdOdontologa, Estado
            FROM dbo.Cita
            WHERE IdCita = ?
        """, (id_cita,))
        cita = cursor.fetchone()

        if not cita:
            raise ValueError("No se encontró la cita seleccionada.")

        id_odontologa, estado = cita

        if estado == "Cancelada":
            raise ValueError(
                "No se puede reprogramar una cita cancelada."
            )

        if existe_cita_en_horario(
            id_odontologa,
            fecha_cita,
            hora_cita,
            excluir_id=id_cita
        ):
            raise ValueError(
                "La odontóloga ya tiene una cita en esa fecha y hora."
            )

        cursor.execute("""
            UPDATE dbo.Cita
            SET FechaCita = ?, HoraCita = ?
            WHERE IdCita = ?
        """, (fecha_cita, hora_cita, id_cita))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def cancelar_cita(id_cita, motivo_cancelacion):
    """Cancela una cita y guarda el motivo."""
    if not motivo_cancelacion.strip():
        raise ValueError(
            "Debes indicar el motivo de cancelación."
        )

    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT Estado
            FROM dbo.Cita
            WHERE IdCita = ?
        """, (id_cita,))
        resultado = cursor.fetchone()

        if not resultado:
            raise ValueError(
                "No se encontró la cita seleccionada."
            )

        if resultado[0] == "Cancelada":
            raise ValueError("Esta cita ya está cancelada.")

        cursor.execute("""
            UPDATE dbo.Cita
            SET Estado = ?, MotivoCancelacion = ?
            WHERE IdCita = ?
        """, (
            "Cancelada",
            motivo_cancelacion.strip(),
            id_cita
        ))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def eliminar_cita(id_cita):
    """Elimina de SQL Server la cita indicada por su ID."""
    conexion = conectar()

    try:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM dbo.Cita
            WHERE IdCita = ?
        """, (id_cita,))

        if cursor.rowcount == 0:
            raise ValueError("La cita seleccionada ya no existe.")

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ============================================================
# PANEL DE CITAS
# ============================================================

class PanelCitas(ctk.CTkFrame):
    """Panel de citas integrado dentro de la ventana principal."""

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=NEGRO,
            corner_radius=0
        )

        self.pack_propagate(False)
        self.crear_interfaz()
        self.filtrar_citas()

    def crear_interfaz(self):
        encabezado = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=14,
            border_width=1,
            border_color=DORADO
        )
        encabezado.pack(
            fill="x", padx=16, pady=(12, 10)
        )

        ctk.CTkLabel(
            encabezado,
            text="GESTIÓN DE CITAS",
            font=("Arial", 24, "bold"),
            text_color=DORADO_CLARO
        ).pack(anchor="w", padx=18, pady=(14, 2))

        ctk.CTkLabel(
            encabezado,
            text="Agenda, reprograma y administra las citas dentales.",
            font=("Arial", 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=18, pady=(0, 14))

        barra = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        barra.pack(
            fill="x", padx=16, pady=(0, 10)
        )

        self.busqueda = ctk.CTkEntry(
            barra,
            placeholder_text=(
                "Buscar por paciente, odontóloga, motivo o estado..."
            ),
            height=38,
            fg_color=PANEL_CLARO,
            border_color=DORADO,
            text_color=TEXTO
        )
        self.busqueda.pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        self.busqueda.bind(
            "<KeyRelease>",
            lambda evento: self.filtrar_citas()
        )

        ctk.CTkButton(
            barra,
            text="Actualizar",
            width=105,
            height=38,
            fg_color=PANEL_CLARO,
            hover_color="#D7F1ED",
            border_width=1,
            border_color=DORADO,
            text_color=DORADO_CLARO,
            command=self.filtrar_citas
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            barra,
            text="+ Nueva cita",
            width=120,
            height=38,
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color=BLANCO,
            font=("Arial", 12, "bold"),
            command=self.formulario_nueva_cita
        ).pack(side="left", padx=4)

        tabla_frame = ctk.CTkFrame(
            self, fg_color=PANEL, corner_radius=12
        )
        tabla_frame.pack(
            fill="both", expand=True, padx=16, pady=(0, 10)
        )

        estilo = ttk.Style()
        estilo.configure(
            "Citas.Treeview",
            background=PANEL_CLARO,
            foreground=TEXTO,
            fieldbackground=PANEL_CLARO,
            rowheight=30,
            font=("Arial", 10)
        )
        estilo.configure(
            "Citas.Treeview.Heading",
            background="#EAF7F5",
            foreground=DORADO_CLARO,
            font=("Arial", 10, "bold")
        )
        estilo.map(
            "Citas.Treeview",
            background=[("selected", "#BFEDE6")],
            foreground=[("selected", TEXTO)]
        )

        columnas = (
            "id", "paciente", "odontologa", "fecha",
            "hora", "motivo", "canal", "estado"
        )

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            style="Citas.Treeview"
        )

        encabezados = {
            "id": "ID",
            "paciente": "Paciente",
            "odontologa": "Odontóloga",
            "fecha": "Fecha",
            "hora": "Hora",
            "motivo": "Motivo",
            "canal": "Canal",
            "estado": "Estado"
        }

        anchos = {
            "id": 48,
            "paciente": 155,
            "odontologa": 155,
            "fecha": 90,
            "hora": 75,
            "motivo": 180,
            "canal": 90,
            "estado": 95
        }

        for columna in columnas:
            self.tabla.heading(
                columna, text=encabezados[columna]
            )
            self.tabla.column(
                columna,
                width=anchos[columna],
                minwidth=45,
                anchor="center"
            )

        scroll_y = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tabla.yview
        )
        scroll_x = ttk.Scrollbar(
            tabla_frame,
            orient="horizontal",
            command=self.tabla.xview
        )

        self.tabla.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        self.tabla.grid(
            row=0, column=0, sticky="nsew",
            padx=(10, 0), pady=(10, 0)
        )
        scroll_y.grid(
            row=0, column=1, sticky="ns",
            pady=(10, 0), padx=(0, 10)
        )
        scroll_x.grid(
            row=1, column=0, sticky="ew",
            padx=(10, 0), pady=(0, 10)
        )

        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        acciones = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        acciones.pack(
            fill="x", padx=16, pady=(0, 14)
        )

        ctk.CTkButton(
            acciones,
            text="Reprogramar cita",
            fg_color=PANEL_CLARO,
            hover_color="#D7F1ED",
            border_width=1,
            border_color=DORADO,
            text_color=DORADO_CLARO,
            command=self.accion_reprogramar
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            acciones,
            text="Cancelar cita",
            fg_color="#FBEAEA",
            hover_color="#F5DADA",
            border_width=1,
            border_color=ROJO,
            text_color=ROJO,
            command=self.accion_cancelar
        ).pack(side="left")

        ctk.CTkButton(
            acciones,
            text="Eliminar",
            fg_color=ROJO,
            hover_color="#983030",
            text_color=BLANCO,
            command=self.accion_eliminar
        ).pack(side="left", padx=(8, 0))

        self.etiqueta_total = ctk.CTkLabel(
            acciones,
            text="",
            text_color=TEXTO,
            font=("Arial", 11)
        )
        self.etiqueta_total.pack(
            side="right", padx=6
        )

    # --------------------------------------------------------
    # CONSULTAR Y FILTRAR CITAS
    # --------------------------------------------------------

    def filtrar_citas(self):
        try:
            citas = consultar_citas()
            termino = self.busqueda.get().strip().lower()

            for elemento in self.tabla.get_children():
                self.tabla.delete(elemento)

            total = 0

            for cita in citas:
                (
                    id_cita, paciente, odontologa, fecha,
                    hora, motivo, canal, estado,
                    motivo_cancelacion
                ) = cita

                fecha_texto = (
                    fecha.strftime("%Y-%m-%d") if fecha else ""
                )
                hora_texto = str(hora)[:5] if hora else ""

                valores = (
                    id_cita,
                    paciente,
                    odontologa,
                    fecha_texto,
                    hora_texto,
                    motivo or "",
                    canal or "",
                    estado or ""
                )

                texto_busqueda = " ".join(
                    str(valor) for valor in valores
                ).lower()

                if termino and termino not in texto_busqueda:
                    continue

                etiqueta = (
                    "cancelada"
                    if estado == "Cancelada"
                    else "normal"
                )

                self.tabla.insert(
                    "", "end",
                    values=valores,
                    tags=(etiqueta,)
                )
                total += 1

            self.tabla.tag_configure(
                "cancelada", foreground=ROJO
            )
            self.tabla.tag_configure(
                "normal", foreground=TEXTO
            )
            self.etiqueta_total.configure(
                text=f"Citas mostradas: {total}"
            )

        except Exception as error:
            messagebox.showerror(
                "Error al consultar citas",
                f"No fue posible cargar las citas.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # OBTENER ID DE LA CITA SELECCIONADA
    # --------------------------------------------------------

    def obtener_id_seleccionado(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Selecciona una cita",
                "Primero selecciona una cita de la tabla.",
                parent=self.winfo_toplevel()
            )
            return None

        valores = self.tabla.item(
            seleccion[0], "values"
        )
        return int(valores[0])

    # --------------------------------------------------------
    # REGISTRAR UNA NUEVA CITA
    # --------------------------------------------------------

    def formulario_nueva_cita(self):
        try:
            pacientes, odontologas, canales = obtener_catalogos()

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los catálogos.\n\n{error}",
                parent=self.winfo_toplevel()
            )
            return

        if not pacientes:
            messagebox.showwarning(
                "Sin pacientes",
                "Primero registra al menos un paciente.",
                parent=self.winfo_toplevel()
            )
            return

        if not odontologas:
            messagebox.showwarning(
                "Sin odontólogas",
                "Primero registra al menos una odontóloga.",
                parent=self.winfo_toplevel()
            )
            return

        ventana = ctk.CTkToplevel(
            self.winfo_toplevel()
        )
        ventana.title("Registrar nueva cita")
        ventana.geometry("560x650")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="REGISTRAR NUEVA CITA",
            font=("Arial", 22, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(18, 14))

        formulario = ctk.CTkFrame(
            ventana,
            fg_color=PANEL,
            corner_radius=12,
            border_width=1,
            border_color=DORADO
        )
        formulario.pack(
            fill="both", expand=True,
            padx=18, pady=(0, 18)
        )

        def etiqueta(texto):
            ctk.CTkLabel(
                formulario,
                text=texto,
                text_color=TEXTO,
                font=("Arial", 11, "bold")
            ).pack(
                anchor="w", padx=18, pady=(9, 3)
            )

        def entrada(placeholder):
            control = ctk.CTkEntry(
                formulario,
                placeholder_text=placeholder,
                height=36,
                fg_color=PANEL_CLARO,
                border_color=DORADO,
                text_color=TEXTO
            )
            control.pack(fill="x", padx=18)
            return control

        etiqueta("Paciente")

        mapa_pacientes = {
            f"{p[1]} {p[2]} (ID {p[0]})": p[0]
            for p in pacientes
        }

        selector_paciente = ctk.CTkComboBox(
            formulario,
            values=list(mapa_pacientes.keys()),
            height=36,
            fg_color=PANEL_CLARO,
            border_color=DORADO,
            button_color=DORADO,
            text_color=TEXTO,
            dropdown_fg_color=PANEL_CLARO,
            dropdown_text_color=TEXTO
        )
        selector_paciente.pack(fill="x", padx=18)
        selector_paciente.set(
            list(mapa_pacientes.keys())[0]
        )

        etiqueta("Odontóloga")

        mapa_odontologas = {
            f"{o[1]} {o[2]} (ID {o[0]})": o[0]
            for o in odontologas
        }

        selector_odontologa = ctk.CTkComboBox(
            formulario,
            values=list(mapa_odontologas.keys()),
            height=36,
            fg_color=PANEL_CLARO,
            border_color=DORADO,
            button_color=DORADO,
            text_color=TEXTO,
            dropdown_fg_color=PANEL_CLARO,
            dropdown_text_color=TEXTO
        )
        selector_odontologa.pack(fill="x", padx=18)
        selector_odontologa.set(
            list(mapa_odontologas.keys())[0]
        )

        etiqueta("Fecha (AAAA-MM-DD)")
        campo_fecha = entrada("Ejemplo: 2026-10-25")
        campo_fecha.insert(0, date.today().isoformat())

        etiqueta("Hora (HH:MM, formato de 24 horas)")
        campo_hora = entrada("Ejemplo: 10:30")

        etiqueta("Motivo de la cita")
        campo_motivo = entrada(
            "Describe el motivo de la consulta"
        )

        etiqueta("Canal de solicitud")
        selector_canal = ctk.CTkComboBox(
            formulario,
            values=canales,
            height=36,
            fg_color=PANEL_CLARO,
            border_color=DORADO,
            button_color=DORADO,
            text_color=TEXTO,
            dropdown_fg_color=PANEL_CLARO,
            dropdown_text_color=TEXTO
        )
        selector_canal.pack(fill="x", padx=18)

        if canales:
            selector_canal.set(canales[0])

        def guardar():
            try:
                paciente_texto = selector_paciente.get()
                odontologa_texto = selector_odontologa.get()

                if paciente_texto not in mapa_pacientes:
                    raise ValueError(
                        "Selecciona un paciente válido."
                    )

                if odontologa_texto not in mapa_odontologas:
                    raise ValueError(
                        "Selecciona una odontóloga válida."
                    )

                fecha_cita = datetime.strptime(
                    campo_fecha.get().strip(),
                    "%Y-%m-%d"
                ).date()

                hora_cita = datetime.strptime(
                    campo_hora.get().strip(),
                    "%H:%M"
                ).time()

                registrar_cita(
                    mapa_pacientes[paciente_texto],
                    mapa_odontologas[odontologa_texto],
                    fecha_cita,
                    hora_cita,
                    campo_motivo.get(),
                    selector_canal.get()
                )

                messagebox.showinfo(
                    "Cita registrada",
                    "La cita se registró correctamente.",
                    parent=ventana
                )

                ventana.destroy()
                self.filtrar_citas()

            except ValueError as error:
                messagebox.showwarning(
                    "Revisa los datos",
                    str(error),
                    parent=ventana
                )

            except Exception as error:
                messagebox.showerror(
                    "Error al registrar",
                    f"No se pudo registrar la cita.\n\n{error}",
                    parent=ventana
                )

        ctk.CTkButton(
            formulario,
            text="GUARDAR CITA",
            height=40,
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color=BLANCO,
            font=("Arial", 12, "bold"),
            command=guardar
        ).pack(
            fill="x", padx=18, pady=16
        )

    # --------------------------------------------------------
    # REPROGRAMAR UNA CITA
    # --------------------------------------------------------

    def accion_reprogramar(self):
        id_cita = self.obtener_id_seleccionado()

        if id_cita is None:
            return

        seleccion = self.tabla.selection()[0]
        valores = self.tabla.item(
            seleccion, "values"
        )

        if valores[7] == "Cancelada":
            messagebox.showwarning(
                "Cita cancelada",
                "No se puede reprogramar una cita cancelada.",
                parent=self.winfo_toplevel()
            )
            return

        ventana = ctk.CTkToplevel(
            self.winfo_toplevel()
        )
        ventana.title("Reprogramar cita")
        ventana.geometry("430x330")
        ventana.resizable(False, False)
        ventana.configure(fg_color=NEGRO)
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text=f"REPROGRAMAR CITA #{id_cita}",
            font=("Arial", 19, "bold"),
            text_color=DORADO_CLARO
        ).pack(pady=(22, 18))

        ctk.CTkLabel(
            ventana,
            text="Nueva fecha (AAAA-MM-DD)",
            text_color=TEXTO
        ).pack(anchor="w", padx=28)

        campo_fecha = ctk.CTkEntry(
            ventana,
            height=38,
            fg_color=PANEL_CLARO,
            border_color=DORADO,
            text_color=TEXTO
        )
        campo_fecha.pack(
            fill="x", padx=28, pady=(5, 12)
        )
        campo_fecha.insert(0, str(valores[3]))

        ctk.CTkLabel(
            ventana,
            text="Nueva hora (HH:MM)",
            text_color=TEXTO
        ).pack(anchor="w", padx=28)

        campo_hora = ctk.CTkEntry(
            ventana,
            height=38,
            fg_color=PANEL_CLARO,
            border_color=DORADO,
            text_color=TEXTO
        )
        campo_hora.pack(
            fill="x", padx=28, pady=(5, 15)
        )
        campo_hora.insert(0, str(valores[4])[:5])

        def guardar_cambios():
            try:
                fecha_cita = datetime.strptime(
                    campo_fecha.get().strip(),
                    "%Y-%m-%d"
                ).date()

                hora_cita = datetime.strptime(
                    campo_hora.get().strip(),
                    "%H:%M"
                ).time()

                reprogramar_cita(
                    id_cita, fecha_cita, hora_cita
                )

                messagebox.showinfo(
                    "Cita reprogramada",
                    "La cita se reprogramó correctamente.",
                    parent=ventana
                )

                ventana.destroy()
                self.filtrar_citas()

            except ValueError as error:
                messagebox.showwarning(
                    "Revisa los datos",
                    str(error),
                    parent=ventana
                )

            except Exception as error:
                messagebox.showerror(
                    "Error",
                    f"No se pudo reprogramar.\n\n{error}",
                    parent=ventana
                )

        ctk.CTkButton(
            ventana,
            text="GUARDAR CAMBIOS",
            height=40,
            fg_color=DORADO,
            hover_color=DORADO_CLARO,
            text_color=BLANCO,
            command=guardar_cambios
        ).pack(
            fill="x", padx=28, pady=(0, 18)
        )

    # --------------------------------------------------------
    # CANCELAR UNA CITA
    # --------------------------------------------------------

    def accion_cancelar(self):
        id_cita = self.obtener_id_seleccionado()

        if id_cita is None:
            return

        seleccion = self.tabla.selection()[0]
        valores = self.tabla.item(
            seleccion, "values"
        )

        if valores[7] == "Cancelada":
            messagebox.showwarning(
                "Cita cancelada",
                "La cita seleccionada ya está cancelada.",
                parent=self.winfo_toplevel()
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar cancelación",
            f"¿Deseas cancelar la cita #{id_cita} de {valores[1]}?",
            parent=self.winfo_toplevel()
        )

        if not confirmar:
            return

        motivo = simpledialog.askstring(
            "Motivo de cancelación",
            "Escribe el motivo de la cancelación:",
            parent=self.winfo_toplevel()
        )

        if motivo is None:
            return

        try:
            cancelar_cita(id_cita, motivo)

            messagebox.showinfo(
                "Cita cancelada",
                "La cita se canceló correctamente.",
                parent=self.winfo_toplevel()
            )

            self.filtrar_citas()

        except ValueError as error:
            messagebox.showwarning(
                "Revisa los datos",
                str(error),
                parent=self.winfo_toplevel()
            )

        except Exception as error:
            messagebox.showerror(
                "Error al cancelar",
                f"No se pudo cancelar la cita.\n\n{error}",
                parent=self.winfo_toplevel()
            )

    # --------------------------------------------------------
    # ELIMINAR UNA CITA
    # --------------------------------------------------------

    def accion_eliminar(self):
        if len(self.tabla.selection()) > 1:
            messagebox.showwarning(
                "Selecciona una cita",
                "Selecciona una sola cita para eliminar.",
                parent=self.winfo_toplevel()
            )
            return

        id_cita = self.obtener_id_seleccionado()
        if id_cita is None:
            return

        seleccion = self.tabla.selection()[0]
        valores = self.tabla.item(seleccion, "values")

        confirmar = messagebox.askyesno(
            "Eliminar cita",
            f"¿Deseas eliminar definitivamente la cita #{id_cita} "
            f"de {valores[1]} del {valores[3]} a las {valores[4]}?",
            parent=self.winfo_toplevel(),
            default="no"
        )

        if not confirmar:
            return

        try:
            eliminar_cita(id_cita)

        except ValueError as error:
            messagebox.showwarning(
                "Cita no disponible",
                str(error),
                parent=self.winfo_toplevel()
            )
            self.filtrar_citas()
            return

        except Exception as error:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar la cita.\n\n{error}",
                parent=self.winfo_toplevel()
            )
            return

        self.filtrar_citas()
        messagebox.showinfo(
            "Cita eliminada",
            f"Se eliminó la cita #{id_cita}.",
            parent=self.winfo_toplevel()
        )


# ============================================================
# EJECUCIÓN INDEPENDIENTE PARA PRUEBAS
# ============================================================

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    ventana = ctk.CTk()
    ventana.title("Sonrisa Sana | Gestión de citas")
    ventana.geometry("1250x720")
    ventana.configure(fg_color=NEGRO)

    panel = PanelCitas(ventana)
    panel.pack(fill="both", expand=True)

    ventana.mainloop()