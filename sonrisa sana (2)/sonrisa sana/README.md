
# 🦷 SONRISA SANA
## Sistema Integral de Gestión Dental

**Ingeniería de Software | Unidad 3 | Equipo 5**

Sonrisa Sana es un sistema de escritorio desarrollado en Python para administrar las actividades de un consultorio dental. Permite gestionar pacientes, citas, tratamientos, sesiones clínicas y procedimientos odontológicos, utilizando una base de datos Microsoft SQL Server.

El proyecto cuenta con interfaces diferenciadas para recepcionista, odontóloga y paciente, con funciones de consulta, registro y seguimiento según las responsabilidades de cada usuario.

---

## 1. Información general

| Dato | Descripción |
|---|---|
| Proyecto | Consultorio Dental Sonrisa Sana |
| Asignatura | Ingeniería de Software |
| Institución | Instituto Tecnológico de Zacatepec |
| Equipo | 5 |
| Integrante | Kevin Damián Fiscal García |
| Integrante | Marco Antonio Góngora García |
| Lenguaje | Python |
| Interfaz gráfica | CustomTkinter |
| Base de datos | Microsoft SQL Server |
| Administrador de BD | SQL Server Management Studio |
| Tecnología de conexión | pyodbc |
| Control de versiones | Git y GitHub |
| Sistema utilizado | Windows 11 |

**Repositorio:**

https://github.com/marco21091016-tech/SONRISA-SANA

---

## 2. Problemática

El Consultorio Dental Sonrisa Sana necesita organizar de manera eficiente la información de pacientes, las citas odontológicas y el seguimiento de los tratamientos.

La administración manual de estos procesos puede ocasionar dificultades para actualizar información, localizar expedientes, consultar horarios, controlar cancelaciones y conocer el estado de los tratamientos.

También resulta necesario facilitar el intercambio de información entre la recepcionista, las odontólogas y los pacientes, evitando la dispersión de registros.

Para atender esta problemática, se desarrolló un sistema de escritorio conectado a una base de datos relacional que centraliza la información del consultorio.

---

## 3. Objetivo general

Desarrollar e integrar un sistema de gestión dental que permita administrar pacientes, citas, tratamientos, procedimientos y sesiones odontológicas mediante una aplicación de escritorio conectada a Microsoft SQL Server, facilitando el registro, la consulta, la actualización y el seguimiento de la información.

### Objetivos específicos

1. Implementar una interfaz gráfica intuitiva para gestionar información odontológica.
2. Registrar y consultar los datos de los pacientes.
3. Administrar citas y sus estados.
4. Facilitar la consulta de agendas y tratamientos.
5. Registrar sesiones y procedimientos clínicos.
6. Proporcionar un portal de consulta para los pacientes.
7. Diferenciar las funcionalidades de los usuarios.
8. Almacenar la información mediante SQL Server.
9. Comprobar las operaciones utilizando consultas SQL.
10. Documentar el proyecto mediante GitHub.

---

## 4. Tecnologías utilizadas

### Python

Lenguaje de programación utilizado para desarrollar la lógica, los formularios y las operaciones del sistema.

### CustomTkinter

Biblioteca utilizada para diseñar la interfaz gráfica de escritorio, incluyendo ventanas, botones, formularios y paneles.

### Microsoft SQL Server

Sistema gestor de base de datos relacional utilizado para almacenar la información del consultorio.

### SQL Server Management Studio (SSMS)

Herramienta utilizada para administrar la base de datos, ejecutar consultas SQL y verificar los registros.

### pyodbc

Biblioteca de Python utilizada para comunicarse con Microsoft SQL Server mediante un controlador ODBC.

### Git y GitHub

Herramientas utilizadas para almacenar el código fuente, mantener un historial de cambios y compartir el proyecto.

### Visual Studio Code

Editor utilizado para desarrollar, ejecutar y revisar los archivos Python.

---

# 5. Funcionalidades del sistema

## 5.1. Inicio de sesión

El sistema dispone de una pantalla de inicio de sesión donde los usuarios ingresan sus credenciales.

Después de una autenticación exitosa, se identifica el rol del usuario y se abre su panel correspondiente.

Los perfiles implementados son:

- Recepcionista.
- Odontóloga.
- Paciente.

La aplicación presenta opciones diferentes dependiendo del perfil que inicia sesión.

## 5.2. Portal de la recepcionista

La recepcionista tiene acceso a los módulos administrativos del consultorio.

### Gestión de pacientes

Permite:

- Registrar pacientes.
- Consultar registros existentes.
- Buscar pacientes.
- Modificar información.
- Eliminar registros cuando la operación esté permitida.

### Gestión de citas

Permite:

- Registrar citas odontológicas.
- Asignar un paciente y una odontóloga.
- Seleccionar fecha y horario.
- Indicar el motivo de consulta.
- Registrar el canal de solicitud.
- Consultar citas existentes.
- Reprogramar y cancelar citas.
- Visualizar el estado de la atención.

### Tratamientos

Permite consultar tratamientos registrados y las sesiones asociadas.

### Procedimientos

Dispone de un catálogo de procedimientos odontológicos.

### Odontólogas

Permite consultar la información de las profesionales y visualizar sus estados de atención.

### Teléfonos

Permite administrar información de contacto relacionada con los pacientes.

### Calendario

Presenta una vista para consultar y organizar las citas.

### Usuarios

Incluye funciones para la administración de las cuentas del sistema.

## 5.3. Portal de la odontóloga

Este portal está dirigido al personal clínico.

Sus principales secciones son:

**Mi perfil**

Consulta de información profesional.

**Registrar paciente**

Permite registrar un paciente nuevo y ofrece la opción de continuar con la programación de su primera cita.

**Mis citas**

Muestra las citas asignadas a la odontóloga.

**Tratamientos**

Permite consultar tratamientos asociados a sus pacientes, registrar nuevos tratamientos y modificar sus estados.

**Sesiones y avances**

Permite consultar sesiones de tratamiento y registrar procedimientos, fechas, estados y observaciones clínicas.

**Procedimientos**

Permite consultar el catálogo y registrar nuevos procedimientos con su nombre, descripción y costo.

## 5.4. Portal del paciente

Permite al paciente consultar información relacionada con su atención odontológica.

### Mi perfil

Muestra los datos de la cuenta del paciente.

### Mis citas

Presenta las citas registradas a su nombre, incluyendo fecha, hora, odontóloga, motivo y estado.

### Mis tratamientos

Permite consultar los tratamientos asociados al paciente.

### Mis avances

Presenta las sesiones registradas, los procedimientos realizados y las observaciones correspondientes.

El sistema también muestra el número de sesiones realizadas respecto al total registrado. Este conteo no representa un porcentaje clínico de recuperación.

### Mis recordatorios

Dispone de un asistente de recordatorios dentro del portal.

El objetivo es informar al paciente sobre sus citas próximas, especialmente las programadas para el día siguiente.

Los recordatorios se consultan dentro de la aplicación. No se presenta esta función como envío automático por WhatsApp, SMS o correo electrónico.

---

# 6. Estructura del proyecto

Los archivos principales del sistema se encuentran dentro de la carpeta:

`sonrisa sana (2)/sonrisa sana/`

### Organización

```text
SONRISA-SANA/
└── sonrisa sana (2)/
    └── sonrisa sana/
        ├── README.md
        ├── main.py
        ├── login.py
        ├── autenticacion.py
        ├── conexion.py
        ├── crear_recepcionista.py
        ├── pacientes.py
        ├── citas.py
        ├── tratamientos.py
        ├── procedimientos.py
        ├── odontologas.py
        ├── telefonos.py
        ├── calendario.py
        ├── usuarios.py
        ├── panel_odontologa.py
        ├── panel_paciente.py
        ├── schema.sql
        ├── roles de sonrisa sana.sql
        └── Manual_de_Usuario_Sonrisa_Sana.docx
```

### Descripción de archivos

| Archivo | Función |
|---|---|
| main.py | Interfaz principal y navegación |
| login.py | Pantalla de inicio de sesión |
| autenticacion.py | Lógica de autenticación |
| conexion.py | Conexión con SQL Server |
| crear_recepcionista.py | Apoyo para crear la cuenta inicial |
| pacientes.py | Administración de pacientes |
| citas.py | Administración de citas |
| tratamientos.py | Gestión de tratamientos y sesiones |
| procedimientos.py | Catálogo de procedimientos |
| odontologas.py | Información de odontólogas |
| telefonos.py | Información de contacto |
| calendario.py | Calendario de citas |
| usuarios.py | Administración de usuarios |
| panel_odontologa.py | Portal de la odontóloga |
| panel_paciente.py | Portal del paciente |
| schema.sql | Script SQL del proyecto |
| roles de sonrisa sana.sql | Script relacionado con roles |
| Manual_de_Usuario_Sonrisa_Sana.docx | Manual de usuario |

---

# 7. Requisitos de instalación

Para ejecutar Sonrisa Sana se necesita:

### Software

1. Windows 11 o un entorno compatible.
2. Python de 64 bits.
3. Visual Studio Code o una terminal.
4. Microsoft SQL Server con soporte de LocalDB, si se utiliza la configuración local del proyecto.
5. SQL Server Management Studio.
6. Microsoft ODBC Driver 18 for SQL Server.
7. Conexión a Internet para descargar inicialmente las herramientas y dependencias.

### Bibliotecas Python

Las principales bibliotecas son:

- customtkinter
- pyodbc

En el entorno de desarrollo del proyecto se utilizó Python 3.14.9, CustomTkinter 6.0.0 y pyodbc 5.3.0.

Se recomienda utilizar versiones compatibles con el código y las dependencias instaladas.

---

# 8. Descargar el proyecto

## Opción A. Descargar desde GitHub

1. Entrar al repositorio:

   https://github.com/marco21091016-tech/SONRISA-SANA

2. Seleccionar el botón **Code**.
3. Elegir **Download ZIP**.
4. Extraer el archivo descargado.
5. Abrir la carpeta que contiene los archivos Python en Visual Studio Code.

## Opción B. Clonar con Git

Abrir una terminal y ejecutar:

```powershell
git clone https://github.com/marco21091016-tech/SONRISA-SANA.git
```

Ingresar a la carpeta del proyecto:

```powershell
cd SONRISA-SANA
cd "sonrisa sana (2)"
cd "sonrisa sana"
```

Comprobar que se encuentra el archivo:

```powershell
dir main.py
```

Si aparece el archivo, se está trabajando desde la carpeta correcta.

---

# 9. Instalación de dependencias

## Paso 1. Comprobar Python

Abrir PowerShell y ejecutar:

```powershell
python --version
```

Si Python está instalado, aparecerá su versión.

## Paso 2. Crear un entorno virtual

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
```

## Paso 3. Activar el entorno

En PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, se puede utilizar el intérprete directamente sin activar el entorno.

## Paso 4. Instalar las bibliotecas

```powershell
python -m pip install customtkinter pyodbc
```

Para reproducir las versiones usadas durante el desarrollo:

```powershell
python -m pip install customtkinter==6.0.0 pyodbc==5.3.0
```

La instalación de estas versiones requiere que sean compatibles con el Python instalado.

## Paso 5. Comprobar dependencias

```powershell
python -m pip show customtkinter
```

```powershell
python -m pip show pyodbc
```

También se puede ejecutar:

```powershell
python -c "import customtkinter, pyodbc; print('Dependencias instaladas correctamente')"
```

Si no aparecen errores, ambas bibliotecas pueden importarse.

---

# 10. Configuración de SQL Server

Sonrisa Sana utiliza una base de datos denominada:

`SonrisaSana`

En el entorno local del equipo se utilizó la instancia:

`(localdb)\MSSQLLocalDB`

## Paso 1. Instalar SQL Server

Se necesita una instalación compatible de SQL Server que incluya o permita utilizar LocalDB.

SQL Server Management Studio es una herramienta de administración, por lo que no sustituye al motor de base de datos.

## Paso 2. Abrir SSMS

Abrir SQL Server Management Studio y conectarse a la instancia:

```text
(localdb)\MSSQLLocalDB
```

Utilizar autenticación de Windows cuando corresponda a la configuración local.

## Paso 3. Preparar la base de datos

Dentro del repositorio se encuentran los archivos:

```text
schema.sql
roles de sonrisa sana.sql
```

Abrir `schema.sql` desde SSMS y revisar el script antes de ejecutarlo.

Se debe comprobar si el archivo crea la base de datos, si requiere que exista previamente y si contiene las tablas y relaciones necesarias.

Si el script requiere una base ya creada, ejecutar previamente:

```sql
IF DB_ID('SonrisaSana') IS NULL
BEGIN
    CREATE DATABASE SonrisaSana;
END;
GO
```

Después ejecutar el script de estructura correspondiente.

El archivo `roles de sonrisa sana.sql` debe revisarse antes de utilizarlo para identificar sus dependencias, cambios y datos de inicialización.

**Importante:** no ejecutar scripts de creación o reinicialización sobre una base de datos con información que deba conservarse sin realizar primero un respaldo.

## Paso 4. Comprobar la base de datos

Ejecutar:

```sql
USE SonrisaSana;
GO

SELECT name
FROM sys.tables
ORDER BY name;
```

Entre las tablas principales del modelo desarrollado se encuentran:

- Paciente
- Cita
- Tratamiento
- Procedimiento
- Odontóloga
- TeléfonoPaciente
- SesionTratamiento

También pueden existir tablas adicionales relacionadas con usuarios, autenticación y estados del sistema.

---

# 11. Configuración de la conexión Python–SQL Server

La conexión está centralizada en:

`conexion.py`

En el entorno de desarrollo se utilizó:

| Parámetro | Valor |
|---|---|
| Servidor | (localdb)\MSSQLLocalDB |
| Base de datos | SonrisaSana |
| Controlador | ODBC Driver 18 for SQL Server |
| Autenticación | Windows |
| Biblioteca | pyodbc |

Un ejemplo de configuración local equivalente es:

```python
import pyodbc

SERVIDOR = r"(localdb)\MSSQLLocalDB"
BASE_DATOS = "SonrisaSana"
CONTROLADOR = "ODBC Driver 18 for SQL Server"

CADENA_CONEXION = (
    f"DRIVER={{{CONTROLADOR}}};"
    f"SERVER={SERVIDOR};"
    f"DATABASE={BASE_DATOS};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def conectar():
    return pyodbc.connect(
        CADENA_CONEXION,
        timeout=5
    )
```

Este ejemplo describe la configuración utilizada durante el desarrollo. La implementación incluida en `conexion.py` es la referencia para ejecutar la versión publicada.

### Consideraciones de seguridad

- No publicar contraseñas.
- No guardar credenciales privadas en el repositorio.
- No utilizar credenciales reales como datos de ejemplo.
- No compartir bases de datos con información privada de pacientes.
- Utilizar autenticación y permisos apropiados para cada entorno.
- Evitar modificar la configuración de conexión sin comprobar su efecto sobre los módulos.

La opción `TrustServerCertificate=yes` corresponde al entorno local de desarrollo y no sustituye una configuración segura de certificados para producción.

---

# 12. Comprobar la conexión

Abrir una terminal desde la carpeta del proyecto.

Ejecutar:

```powershell
python conexion.py
```

Si el archivo incluye la prueba directa de conexión, mostrará el resultado correspondiente.

También se puede verificar la conectividad ejecutando desde PowerShell:

```powershell
python -c "from conexion import conectar; c=conectar(); print('Conexion exitosa'); c.close()"
```

Esta comprobación importa la función `conectar()` y abre una conexión real a la base de datos.

**Importante:** obtener una conexión exitosa no demuestra por sí solo que las operaciones de la aplicación funcionen. Se deben comprobar registros, consultas y modificaciones.

---

# 13. Ejecutar Sonrisa Sana

## Paso 1. Abrir Visual Studio Code

Abrir la carpeta donde se encuentran `main.py` y los módulos del proyecto.

## Paso 2. Abrir una terminal

En Visual Studio Code seleccionar:

**Terminal > Nueva terminal**

## Paso 3. Instalar dependencias si aún no están disponibles

```powershell
python -m pip install customtkinter pyodbc
```

## Paso 4. Ejecutar la aplicación

```powershell
python main.py
```

Se abrirá la interfaz del sistema según la configuración implementada.

## Paso 5. Iniciar sesión

Ingresar las credenciales de una cuenta previamente registrada y autorizada.

Dependiendo del rol, el sistema permitirá acceder al panel correspondiente.

### Cuenta inicial

El proyecto incluye `crear_recepcionista.py`, relacionado con la creación de una cuenta de recepcionista.

Antes de ejecutarlo, revisar su código y verificar que no contenga credenciales predefinidas inseguras ni vuelva a crear usuarios existentes.

Las contraseñas deberán establecerse localmente y mantenerse fuera del repositorio.

---

# 14. Operación y verificación de la base de datos

Una de las características principales del sistema es que registra información real en SQL Server.

Durante las pruebas de integración se verificaron operaciones realizadas desde la interfaz gráfica.

## Prueba 1. Registro de pacientes

Desde el módulo Pacientes se registró un paciente de prueba.

La aplicación mostró:

`Paciente guardado correctamente`

Posteriormente, el registro pudo localizarse en SQL Server con el identificador 1010.

Consulta:

```sql
USE SonrisaSana;
GO

SELECT *
FROM dbo.Paciente
WHERE IdPaciente = 1010;
```

La prueba comprobó la persistencia de la información del paciente.

## Prueba 2. Registro de citas

Se registró una cita de prueba para el paciente con ID 1010.

Datos utilizados:

| Campo | Valor |
|---|---|
| ID de cita | 1007 |
| ID de paciente | 1010 |
| ID de odontóloga | 1002 |
| Fecha | 2026-11-14 |
| Hora | 10:30 |
| Motivo | Ortodoncia |
| Canal | Presencial |
| Estado | Pendiente |

La aplicación confirmó el registro y la cita apareció en la agenda.

Consulta de verificación:

```sql
USE SonrisaSana;
GO

SELECT *
FROM dbo.Cita
WHERE IdCita = 1007;
```

La consulta devolvió el registro esperado.

## Prueba 3. Registro de sesiones

Desde el módulo de tratamientos se registró una sesión.

Datos comprobados:

| Campo | Valor |
|---|---|
| ID de sesión | 1005 |
| ID de tratamiento | 1006 |
| ID de procedimiento | 2 |
| Fecha | 2026-11-13 |
| Estado | Realizada |

Consulta:

```sql
USE SonrisaSana;
GO

SELECT *
FROM dbo.SesionTratamiento
WHERE IdTratamiento = 1006;
```

La sesión apareció en la base de datos y coincidió con la información capturada desde la interfaz.

## Prueba 4. Registro de procedimientos

Desde el Portal de la Odontóloga se registró un nuevo procedimiento.

Datos comprobados:

| Campo | Valor |
|---|---|
| ID | 1003 |
| Nombre | Brackets |
| Costo | 15000.00 |

La aplicación mostró el mensaje:

`Procedimiento registrado correctamente`

Después, el registro apareció en el catálogo.

Consulta:

```sql
USE SonrisaSana;
GO

SELECT *
FROM dbo.Procedimiento
WHERE IdProcedimiento = 1003;
```

La consulta confirmó que el procedimiento se almacenó en SQL Server.

**Nota:** estos identificadores pertenecen al entorno utilizado durante las pruebas. En una instalación nueva pueden generarse identificadores diferentes.

---

# 15. Relación con los requisitos funcionales

El sistema se desarrolló tomando como referencia los requisitos funcionales establecidos durante las unidades anteriores.

| Requisito | Descripción |
|---|---|
| RF-01 | Registrar solicitudes de cita |
| RF-02 | Consultar disponibilidad |
| RF-03 | Registrar citas |
| RF-04 | Consultar citas |
| RF-05 | Confirmar citas |
| RF-06 | Proporcionar recordatorios |
| RF-07 | Reprogramar citas |
| RF-08 | Cancelar citas |
| RF-09 | Registrar inasistencias |
| RF-10 | Registrar sesiones |
| RF-11 | Registrar procedimientos |
| RF-12 | Consultar información según el usuario autorizado |
| RF-13 | Consultar citas del paciente |
| RF-14 | Consultar avance de tratamientos |

La implementación y el grado de validación de cada requisito se documentan en la evidencia U3-E2 del proyecto.

La existencia de una pantalla o de un botón no se considera por sí sola una prueba suficiente de cumplimiento.

---

# 16. Respaldo y recuperación

La base de datos contiene información fundamental para el funcionamiento del sistema.

Por ello, se recomienda crear respaldos periódicos y conservar copias del código fuente.

## 16.1. Respaldo de la base de datos

Existen dos opciones:

### Opción A. Respaldo .bak

Cuando se utiliza una edición e instancia compatibles de SQL Server, se puede crear un respaldo desde SSMS mediante las opciones de copia de seguridad.

Debe verificarse que la instancia utilizada permita ejecutar esa operación y que la ruta de destino sea accesible para el servicio.

### Opción B. Script SQL

Desde SSMS se pueden generar scripts para recrear objetos de la base de datos.

Si se necesita conservar también la información de prueba, se deben incluir los datos según las opciones disponibles.

Un script que únicamente contiene sentencias `CREATE TABLE` no constituye un respaldo completo de los registros almacenados.

## 16.2. Respaldo del código fuente

GitHub conserva el código publicado y su historial de cambios.

Para guardar una copia adicional:

1. Abrir el repositorio.
2. Seleccionar **Code**.
3. Elegir **Download ZIP**.
4. Guardar la copia en una ubicación segura.

## 16.3. Recuperación

En caso de una falla:

1. Recuperar los archivos del proyecto.
2. Instalar Python y sus dependencias.
3. Preparar o restaurar SQL Server.
4. Recuperar la estructura y los datos desde el respaldo correspondiente.
5. Revisar `conexion.py`.
6. Ejecutar `main.py`.
7. Realizar pruebas de registro y consulta.

---

# 17. Problemas frecuentes y soluciones

## Error: No module named customtkinter

Instalar la biblioteca:

```powershell
python -m pip install customtkinter
```

## Error: No module named pyodbc

Ejecutar:

```powershell
python -m pip install pyodbc
```

## Error: Data source name not found

Comprobar que Microsoft ODBC Driver 18 for SQL Server esté instalado.

Para revisar los controladores detectados por Python:

```powershell
python -c "import pyodbc; print(pyodbc.drivers())"
```

Verificar que el controlador indicado en `conexion.py` exista en el equipo.

## Error: Cannot open database SonrisaSana

Comprobar que la base de datos esté creada y que el usuario de Windows tenga permisos sobre ella.

En SSMS:

```sql
SELECT name
FROM sys.databases
WHERE name = 'SonrisaSana';
```

## Error de conexión con LocalDB

Verificar que LocalDB esté instalado y que la instancia configurada exista.

Se puede comprobar desde la terminal:

```powershell
sqllocaldb info
```

Si la instancia `MSSQLLocalDB` existe pero está detenida, se puede intentar iniciarla:

```powershell
sqllocaldb start MSSQLLocalDB
```

## La aplicación abre, pero no aparecen registros

Comprobar:

- Que Python se conecte a la base correcta.
- Que las tablas existan.
- Que los registros hayan sido guardados.
- Que no se esté utilizando otra instancia de SQL Server.
- Que el usuario tenga permisos de consulta.

## Error por archivo no encontrado

Comprobar que la terminal esté abierta en la carpeta que contiene `main.py`.

## Inicio de sesión incorrecto

Revisar que la cuenta exista, que esté habilitada y que las credenciales ingresadas sean correctas.

No se deben publicar contraseñas para resolver este problema.

---

# 18. Pruebas y validación del sistema

Durante el desarrollo se realizaron pruebas funcionales sobre los principales módulos.

Las verificaciones documentadas incluyen:

- Acceso al sistema como recepcionista.
- Consulta del panel principal.
- Registro de pacientes.
- Consulta de registros de pacientes.
- Registro de citas.
- Consulta de citas.
- Registro de sesiones de tratamiento.
- Consulta de tratamientos y avances.
- Registro de procedimientos desde el portal de odontóloga.
- Consulta de citas asignadas a la odontóloga.
- Consulta de citas desde el portal del paciente.
- Consulta de tratamientos y avances desde el portal del paciente.
- Verificación de registros directamente en SQL Server.

Las pruebas se realizaron utilizando registros de ejemplo en el entorno académico.

Las operaciones verificadas en SQL Server incluyen pacientes, citas, sesiones y procedimientos.

Las pruebas positivas de notificaciones para el día siguiente, restricciones de acceso entre cuentas diferentes y otros casos especiales deben validarse de forma independiente.

---

# 19. Seguridad y buenas prácticas

Para proteger el sistema y la información:

1. Evitar publicar contraseñas.
2. Utilizar cuentas individuales.
3. Mantener los permisos según el rol.
4. No publicar expedientes reales de pacientes.
5. Usar datos ficticios en las demostraciones.
6. Realizar respaldos periódicos.
7. Conservar el historial de cambios.
8. Evitar subir archivos temporales de Python.
9. Revisar los scripts antes de ejecutarlos.
10. No compartir configuraciones privadas de producción.

Se recomienda utilizar un archivo `.gitignore` con las siguientes reglas:

```gitignore
__pycache__/
*.pyc
.venv/
venv/
.env
.env.*
!.env.example
.vscode/
*.bak
*.log
```

Estos elementos permiten excluir archivos temporales, entornos virtuales y archivos que podrían contener información sensible.

---

# 20. Participación del equipo

## Kevin Damián Fiscal García

Actividades desarrolladas:

- Desarrollo de la interfaz gráfica.
- Integración de módulos Python.
- Configuración de conexión con SQL Server.
- Implementación y pruebas de operaciones de la aplicación.
- Verificación de registros mediante consultas SQL.
- Corrección de errores de funcionamiento.
- Pruebas de integración entre interfaz y base de datos.

## Marco Antonio Góngora García

Actividades desarrolladas:

- Participación en la documentación del proyecto.
- Elaboración y organización de entregables académicos.
- Apoyo en los documentos de análisis y diseño.
- Participación en la organización de requisitos y modelos del sistema.
- Integración de documentación asociada al proyecto.

Las contribuciones individuales deberán respaldarse mediante archivos, documentos, versiones o commits que permitan identificarlas.

El historial disponible en GitHub puede consultarse desde la opción **History** del repositorio.

---

# 21. Limitaciones y mejoras futuras

Aunque el sistema dispone de funcionalidades operativas, se identifican oportunidades de mejora:

- Ampliar las pruebas de permisos entre roles.
- Mejorar las validaciones de horarios disponibles.
- Comprobar todos los escenarios de reprogramación y cancelación.
- Fortalecer los mecanismos de recuperación de contraseñas.
- Probar los recordatorios de citas del día siguiente en diferentes escenarios.
- Mejorar los mensajes de error.
- Automatizar los respaldos de la base de datos.
- Ampliar las pruebas funcionales.
- Mejorar la documentación de despliegue.
- Evaluar una futura versión web o móvil.

---

# 22. Conclusión

El desarrollo de Sonrisa Sana permitió aplicar conocimientos de Ingeniería de Software mediante la construcción de una aplicación de escritorio conectada a una base de datos relacional.

Durante el proyecto se integraron componentes de interfaz gráfica, programación en Python, acceso a datos mediante pyodbc y almacenamiento persistente en Microsoft SQL Server.

Las pruebas realizadas permitieron comprobar operaciones de registro y consulta de pacientes, citas, sesiones de tratamiento y procedimientos odontológicos, así como el funcionamiento de interfaces diferenciadas para recepcionista, odontóloga y paciente.

El proyecto también fortaleció las competencias de análisis de requisitos, diseño de software, organización de código, documentación, resolución de problemas y trabajo colaborativo.

Sonrisa Sana constituye una base funcional para la administración de un consultorio dental y puede continuar mejorándose mediante pruebas, nuevas funcionalidades y medidas adicionales de seguridad.

---

## Equipo de desarrollo

**Equipo 5 — Ingeniería de Software**

- Kevin Damián Fiscal García.
- Marco Antonio Góngora García.

**Proyecto:** Consultorio Dental Sonrisa Sana.

**Repositorio:** https://github.com/marco21091016-tech/SONRISA-SANA

**Fecha de documentación:** 13 de noviembre de 2026.
