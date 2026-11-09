-- =====================================================================
-- Proyecto Final: Estacionamiento Público
-- Script de creación de la base de datos (MariaDB / XAMPP)
-- =====================================================================
DROP DATABASE IF EXISTS estacionamiento;
CREATE DATABASE estacionamiento
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
USE estacionamiento;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- USUARIOS: quienes entran al sistema (admin / cobrador)
-- password guarda el hash SHA-256 en hexadecimal (64 caracteres)
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
  id_usuario  INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre      VARCHAR(100) NOT NULL,
  usuario     VARCHAR(30)  NOT NULL,
  password    CHAR(64)     NOT NULL,
  rol         ENUM('admin','cobrador') NOT NULL DEFAULT 'cobrador',
  activo      TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id_usuario),
  UNIQUE KEY uq_usuarios_usuario (usuario)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- CLIENTES
-- tipo_cliente se actualiza automáticamente por número de visitas
-- ---------------------------------------------------------------------
CREATE TABLE clientes (
  id_cliente     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre         VARCHAR(100) NOT NULL,
  telefono       VARCHAR(20)  NULL,
  tipo_cliente   ENUM('frecuente','paso') NOT NULL DEFAULT 'paso',
  fecha_registro DATE         NOT NULL DEFAULT (CURRENT_DATE),
  PRIMARY KEY (id_cliente)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- VEHICULOS: cada vehículo pertenece a un cliente
-- ---------------------------------------------------------------------
CREATE TABLE vehiculos (
  matricula  VARCHAR(15)  NOT NULL,
  id_cliente INT UNSIGNED NOT NULL,
  marca      VARCHAR(40)  NULL,
  modelo     VARCHAR(40)  NULL,
  color      VARCHAR(30)  NULL,
  PRIMARY KEY (matricula),
  KEY idx_vehiculos_cliente (id_cliente),
  CONSTRAINT fk_vehiculos_cliente
    FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- SERVICIOS: cada entrada/salida de un vehículo
-- fecha_salida es NULL mientras el vehículo sigue dentro
-- ---------------------------------------------------------------------
CREATE TABLE servicios (
  id_servicio   INT UNSIGNED NOT NULL AUTO_INCREMENT,
  matricula     VARCHAR(15)  NOT NULL,
  id_usuario    INT UNSIGNED NOT NULL,
  fecha_entrada DATETIME     NOT NULL,
  fecha_salida  DATETIME     NULL,
  PRIMARY KEY (id_servicio),
  KEY idx_servicios_matricula (matricula),
  KEY idx_servicios_usuario (id_usuario),
  KEY idx_servicios_entrada (fecha_entrada),
  CONSTRAINT fk_servicios_vehiculo
    FOREIGN KEY (matricula) REFERENCES vehiculos (matricula)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_servicios_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_servicios_fechas
    CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_entrada)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PENSIONES: contrato por periodo para un vehículo
-- ---------------------------------------------------------------------
CREATE TABLE pensiones (
  id_pension   INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  id_cliente   INT UNSIGNED  NOT NULL,
  matricula    VARCHAR(15)   NOT NULL,
  id_usuario   INT UNSIGNED  NOT NULL,
  fecha_inicio DATE          NOT NULL,
  fecha_fin    DATE          NOT NULL,
  monto        DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (id_pension),
  KEY idx_pensiones_cliente (id_cliente),
  KEY idx_pensiones_vehiculo (matricula, fecha_inicio, fecha_fin),
  KEY idx_pensiones_usuario (id_usuario),
  CONSTRAINT fk_pensiones_cliente
    FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_pensiones_vehiculo
    FOREIGN KEY (matricula) REFERENCES vehiculos (matricula)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_pensiones_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_pensiones_fechas CHECK (fecha_fin >= fecha_inicio),
  CONSTRAINT ck_pensiones_monto CHECK (monto >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- COBROS: pago de un servicio por hora O de una pensión (uno solo)
-- UNIQUE en cada FK: un servicio o pensión tiene a lo más un cobro.
-- ---------------------------------------------------------------------
CREATE TABLE cobros (
  id_cobro       INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  id_servicio    INT UNSIGNED  NULL,
  id_pension     INT UNSIGNED  NULL,
  id_usuario     INT UNSIGNED  NOT NULL,
  horas_cobradas DECIMAL(6,2)  NULL,
  monto          DECIMAL(10,2) NOT NULL,
  fecha_cobro    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_cobro),
  UNIQUE KEY uq_cobros_servicio (id_servicio),
  UNIQUE KEY uq_cobros_pension (id_pension),
  KEY idx_cobros_usuario (id_usuario),
  KEY idx_cobros_fecha (fecha_cobro),
  CONSTRAINT fk_cobros_servicio
    FOREIGN KEY (id_servicio) REFERENCES servicios (id_servicio)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_cobros_pension
    FOREIGN KEY (id_pension) REFERENCES pensiones (id_pension)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_cobros_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_cobros_origen CHECK (
    (id_servicio IS NOT NULL AND id_pension IS NULL) OR
    (id_servicio IS NULL AND id_pension IS NOT NULL)
  ),
  CONSTRAINT ck_cobros_monto CHECK (monto >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PRECIOS: tarifa escalonada por tipo de cliente y tramo de horas
-- hora_hasta NULL = "en adelante"
-- ---------------------------------------------------------------------
CREATE TABLE precios (
  id_precio    INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  tipo_cliente ENUM('frecuente','paso') NOT NULL,
  hora_desde   INT UNSIGNED  NOT NULL,
  hora_hasta   INT UNSIGNED  NULL,
  precio_hora  DECIMAL(8,2)  NOT NULL,
  PRIMARY KEY (id_precio),
  UNIQUE KEY uq_precios_tramo (tipo_cliente, hora_desde),
  CONSTRAINT ck_precios_tramo CHECK (hora_hasta IS NULL OR hora_hasta >= hora_desde)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PARAMETROS: valores configurables (clave / valor)
-- ---------------------------------------------------------------------
CREATE TABLE parametros (
  clave VARCHAR(50)  NOT NULL,
  valor VARCHAR(100) NOT NULL,
  PRIMARY KEY (clave)
) ENGINE=InnoDB;

-- =====================================================================
-- DATOS BASE (necesarios para que el sistema funcione)
-- =====================================================================

-- Cliente genérico para los clientes de paso
INSERT INTO clientes (id_cliente, nombre, tipo_cliente)
VALUES (1, 'Público general', 'paso');

-- Tarifa escalonada: primeras 5 h y de la 6ª en adelante
INSERT INTO precios (tipo_cliente, hora_desde, hora_hasta, precio_hora) VALUES
  ('paso',      1, 5,    30.00),
  ('paso',      6, NULL, 25.00),
  ('frecuente', 1, 5,    26.00),
  ('frecuente', 6, NULL, 22.00);

-- Parámetros del cliente frecuente automático (ajustables)
INSERT INTO parametros (clave, valor) VALUES
  ('visitas_para_frecuente', '10'),
  ('periodo_dias_frecuente', '30');

-- Pendientes de decidir en equipo 
-- INSERT INTO parametros (clave, valor) VALUES ('precio_pension_mensual', '0');
-- INSERT INTO parametros (clave, valor) VALUES ('descuento_pension_2anios', '0');