USE SonrisaSana;
GO

SELECT
    TABLE_NAME AS NombreTabla,
    COLUMN_NAME AS NombreColumna,
    DATA_TYPE AS TipoDato
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME, ORDINAL_POSITION;



USE SonrisaSana;
GO

-- =====================================================
-- SONRISA SANA
-- CREACION DE TABLA PARA USUARIOS Y ROLES
-- =====================================================

IF OBJECT_ID('dbo.UsuarioSistema', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.UsuarioSistema
    (
        IdUsuario INT IDENTITY(1,1) PRIMARY KEY,

        NombreUsuario VARCHAR(100) NOT NULL UNIQUE,

        ContrasenaHash VARCHAR(255) NOT NULL,

        Rol VARCHAR(20) NOT NULL,

        IdPaciente INT NULL,

        IdOdontologa INT NULL,

        Activo BIT NOT NULL DEFAULT 1,

        FechaCreacion DATETIME2 NOT NULL
            DEFAULT SYSDATETIME(),

        CONSTRAINT CK_UsuarioSistema_Rol
        CHECK (
            Rol IN (
                'Recepcionista',
                'Odontologa',
                'Paciente'
            )
        ),

        CONSTRAINT CK_UsuarioSistema_Relacion
        CHECK (
            (Rol = 'Recepcionista'
                AND IdPaciente IS NULL
                AND IdOdontologa IS NULL)
            OR
            (Rol = 'Odontologa'
                AND IdPaciente IS NULL
                AND IdOdontologa IS NOT NULL)
            OR
            (Rol = 'Paciente'
                AND IdPaciente IS NOT NULL
                AND IdOdontologa IS NULL)
        ),

        CONSTRAINT FK_UsuarioSistema_Paciente
        FOREIGN KEY (IdPaciente)
        REFERENCES dbo.Paciente(IdPaciente),

        CONSTRAINT FK_UsuarioSistema_Odontologa
        FOREIGN KEY (IdOdontologa)
        REFERENCES dbo.Odontologa(IdOdontologa)
    );

    PRINT 'Tabla UsuarioSistema creada correctamente.';
END
ELSE
BEGIN
    PRINT 'La tabla UsuarioSistema ya existe.';
END;
GO







USE SonrisaSana;
GO

SELECT
    COLUMN_NAME AS Columna,
    DATA_TYPE AS TipoDato
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME = 'UsuarioSistema'
ORDER BY ORDINAL_POSITION;







USE SonrisaSana;
GO

-- Usuarios del sistema
SELECT * FROM dbo.UsuarioSistema;

-- Odontologas registradas
SELECT IdOdontologa, Nombre, Apellidos
FROM dbo.Odontologa;

-- Pacientes registrados
SELECT IdPaciente, Nombre, Apellidos
FROM dbo.Paciente;



USE SonrisaSana;
GO

SELECT
    IdUsuario,
    NombreUsuario,
    Rol,
    Activo,
    FechaCreacion
FROM dbo.UsuarioSistema
WHERE NombreUsuario = 'recepcionista';







USE SonrisaSana;
GO

SELECT
    IdUsuario,
    NombreUsuario,
    Rol,
    IdPaciente,
    IdOdontologa,
    Activo,
    FechaCreacion
FROM dbo.UsuarioSistema
ORDER BY IdUsuario;







USE SonrisaSana;
GO

SELECT
    IdUsuario,
    NombreUsuario,
    Rol,
    IdPaciente,
    IdOdontologa,
    Activo
FROM dbo.UsuarioSistema
ORDER BY IdUsuario;








USE SonrisaSana;
GO

SELECT
    NombreUsuario,
    Rol,
    CASE
        WHEN Activo = 1 THEN 'ACTIVO'
        ELSE 'INACTIVO'
    END AS EstadoCuenta,
    CASE
        WHEN Rol = 'Recepcionista'
             AND IdPaciente IS NULL
             AND IdOdontologa IS NULL
            THEN 'CORRECTO'

        WHEN Rol = 'Paciente'
             AND IdPaciente IS NOT NULL
             AND IdOdontologa IS NULL
            THEN 'CORRECTO'

        WHEN Rol = 'Odontologa'
             AND IdOdontologa IS NOT NULL
             AND IdPaciente IS NULL
            THEN 'CORRECTO'

        ELSE 'REVISAR'
    END AS ValidacionRol
FROM dbo.UsuarioSistema
ORDER BY IdUsuario;
