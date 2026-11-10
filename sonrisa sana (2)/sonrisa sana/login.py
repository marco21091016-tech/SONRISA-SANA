
import customtkinter as ctk
from tkinter import messagebox

from autenticacion import autenticar_usuario


# ============================================================
# SONRISA SANA - INICIO DE SESION
# ============================================================

FONDO = "#F4FBFA"
PANEL = "#FFFFFF"
PANEL_CLARO = "#EAF7F5"
VERDE = "#159F95"
VERDE_OSCURO = "#087F78"
TEXTO = "#263B3A"
BORDE = "#B8DED8"
BLANCO = "#FFFFFF"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ============================================================
# VENTANA DE INICIO DE SESION
# ============================================================

class VentanaLogin(ctk.CTk):

    def __init__(self, al_iniciar_sesion=None):
        super().__init__()

        self.al_iniciar_sesion = al_iniciar_sesion
        self.usuario_autenticado = None
        self.procesando = False

        self.title("Sonrisa Sana | Inicio de sesion")
        self.geometry("900x650")
        self.minsize(650, 550)
        self.configure(fg_color=FONDO)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_interfaz()

        self.bind("<Return>", self.iniciar_sesion)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    # ========================================================
    # DISEÑO DE LA INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        contenedor = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=20,
            border_width=1,
            border_color=BORDE,
            width=460,
            height=530
        )

        contenedor.grid(
            row=0,
            column=0,
            padx=25,
            pady=30
        )

        contenedor.grid_propagate(False)

        # LOGOTIPO

        ctk.CTkLabel(
            contenedor,
            text="🦷",
            font=("Arial", 55)
        ).pack(pady=(28, 8))

        # NOMBRE DEL SISTEMA

        ctk.CTkLabel(
            contenedor,
            text="SONRISA SANA",
            font=("Georgia", 31, "bold"),
            text_color=VERDE
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            contenedor,
            text="Sistema integral de gestion dental",
            font=("Arial", 13),
            text_color=VERDE_OSCURO
        ).pack(pady=(0, 20))

        ctk.CTkFrame(
            contenedor,
            height=2,
            fg_color=VERDE
        ).pack(
            fill="x",
            padx=35,
            pady=(0, 20)
        )

        # TITULO

        ctk.CTkLabel(
            contenedor,
            text="INICIAR SESION",
            font=("Arial", 17, "bold"),
            text_color=TEXTO
        ).pack(pady=(0, 15))

        # NOMBRE DE USUARIO

        ctk.CTkLabel(
            contenedor,
            text="Nombre de usuario",
            font=("Arial", 12, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=48,
            pady=(0, 5)
        )

        self.entrada_usuario = ctk.CTkEntry(
            contenedor,
            width=365,
            height=43,
            placeholder_text="Escribe tu usuario",
            fg_color=PANEL_CLARO,
            border_color=BORDE,
            text_color=TEXTO,
            corner_radius=8
        )

        self.entrada_usuario.pack(
            padx=48,
            pady=(0, 15)
        )

        # CONTRASEÑA

        ctk.CTkLabel(
            contenedor,
            text="Contraseña",
            font=("Arial", 12, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=48,
            pady=(0, 5)
        )

        self.entrada_contrasena = ctk.CTkEntry(
            contenedor,
            width=365,
            height=43,
            placeholder_text="Escribe tu contraseña",
            show="●",
            fg_color=PANEL_CLARO,
            border_color=BORDE,
            text_color=TEXTO,
            corner_radius=8
        )

        self.entrada_contrasena.pack(
            padx=48,
            pady=(0, 18)
        )

        # BOTON INICIAR SESION

        self.boton_ingresar = ctk.CTkButton(
            contenedor,
            text="INICIAR SESION",
            width=365,
            height=45,
            corner_radius=9,
            fg_color=VERDE,
            hover_color=VERDE_OSCURO,
            text_color=BLANCO,
            font=("Arial", 13, "bold"),
            command=self.iniciar_sesion
        )

        self.boton_ingresar.pack(pady=(0, 15))

        # MENSAJE INFERIOR

        ctk.CTkLabel(
            contenedor,
            text="Acceso exclusivo para usuarios autorizados",
            font=("Arial", 10),
            text_color=VERDE_OSCURO
        ).pack(pady=(0, 10))

        self.after(
            150,
            self.entrada_usuario.focus_set
        )

    # ========================================================
    # VALIDACION DE CREDENCIALES
    # ========================================================

    def iniciar_sesion(self, event=None):

        if self.procesando:
            return

        usuario = self.entrada_usuario.get().strip()
        contrasena = self.entrada_contrasena.get()

        if not usuario or not contrasena:
            messagebox.showwarning(
                "Sonrisa Sana",
                "Debes escribir tu usuario y contraseña.",
                parent=self
            )
            return

        self.procesando = True

        self.boton_ingresar.configure(
            state="disabled",
            text="VERIFICANDO..."
        )

        self.update_idletasks()

        try:
            datos_usuario = autenticar_usuario(
                usuario,
                contrasena
            )

            if datos_usuario is None:
                messagebox.showerror(
                    "Acceso denegado",
                    "Usuario o contraseña incorrectos, "
                    "o cuenta desactivada.",
                    parent=self
                )

                self.entrada_contrasena.delete(0, "end")
                self.entrada_contrasena.focus_set()
                return

            # SESION VALIDADA

            self.usuario_autenticado = datos_usuario

            messagebox.showinfo(
                "Sonrisa Sana",
                "Inicio de sesión correcto.\n\n"
                f"Bienvenido: {datos_usuario['nombre_usuario']}\n"
                f"Rol: {datos_usuario['rol']}",
                parent=self
            )

            # SI EXISTE UNA FUNCION PARA ABRIR EL SISTEMA,
            # SE OCULTA EL LOGIN Y SE EJECUTA ESA FUNCION.

            if self.al_iniciar_sesion is not None:

                self.withdraw()

                self.after(
                    100,
                    lambda: self.abrir_sistema(datos_usuario)
                )

            else:
                # PRUEBA INDEPENDIENTE DEL LOGIN
                self.destroy()

        except Exception as error:

            print("ERROR DE AUTENTICACION:", error)

            messagebox.showerror(
                "Error de conexion",
                "No se pudo verificar el acceso.\n\n"
                "Comprueba la conexion con SQL Server.",
                parent=self
            )

        finally:

            if self.winfo_exists():

                self.procesando = False

                self.boton_ingresar.configure(
                    state="normal",
                    text="INICIAR SESION"
                )

    # ========================================================
    # ABRIR EL SISTEMA PRINCIPAL
    # ========================================================

    def abrir_sistema(self, datos_usuario):

        try:
            if self.al_iniciar_sesion is not None:
                self.al_iniciar_sesion(datos_usuario)

        except Exception as error:

            print("ERROR AL ABRIR EL SISTEMA:", error)

            self.deiconify()

            messagebox.showerror(
                "Sonrisa Sana",
                "No se pudo abrir la interfaz principal.\n\n"
                "Revisa la terminal de VS Code.",
                parent=self
            )

    # ========================================================
    # REGRESAR A LA PANTALLA DE LOGIN
    # ========================================================

    def regresar_login(self):

        self.usuario_autenticado = None
        self.procesando = False

        self.entrada_usuario.delete(0, "end")
        self.entrada_contrasena.delete(0, "end")

        self.boton_ingresar.configure(
            state="normal",
            text="INICIAR SESION"
        )

        self.deiconify()
        self.lift()
        self.entrada_usuario.focus_set()

    # ========================================================
    # CERRAR APLICACION
    # ========================================================

    def cerrar_aplicacion(self):

        self.usuario_autenticado = None
        self.destroy()


# ============================================================
# EJECUCION INDEPENDIENTE
# ============================================================

if __name__ == "__main__":

    login = VentanaLogin()
    login.mainloop()
