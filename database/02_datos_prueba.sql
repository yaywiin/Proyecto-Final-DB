-- =====================================================================
-- Datos de prueba (corre después de 01_tablas.sql)
-- Usuarios de prueba:  admin / admin123   y   cobrador / cobrador123
-- Los precios, servicios base y el cliente "Público general" ya los crea 01_tablas.sql
-- =====================================================================
USE estacionamiento;
SET NAMES utf8mb4;

-- Usuarios (password = SHA-256 en hexadecimal)
INSERT INTO usuarios (id_usuario, nombre, usuario, password, rol) VALUES
  (1, 'Administrador', 'admin',    SHA2('admin123', 256),    'admin'),
  (2, 'Cobrador Uno',  'cobrador', SHA2('cobrador123', 256), 'cobrador');

-- Clientes registrados (el 1 es "Público general")
INSERT INTO clientes (id_cliente, nombre, telefono, tipo_cliente, fecha_registro) VALUES
  (2, 'Ana López',  '5551230001', 'frecuente', '2025-10-01'),
  (3, 'Luis Pérez', '5551230002', 'paso',      '2026-01-15');

-- Vehículos
INSERT INTO vehiculos (matricula, id_cliente, marca, modelo, color) VALUES
  ('ABC1234', 1, 'Nissan',    'Versa',   'Blanco'),
  ('XYZ9876', 1, 'Chevrolet', 'Aveo',    'Rojo'),
  ('JKL4567', 1, 'Volkswagen','Jetta',   'Gris'),
  ('MNP2345', 2, 'Mazda',     'Mazda 3', 'Azul'),
  ('QRS8765', 2, 'Toyota',    'Corolla', 'Negro'),
  ('TUV1122', 3, 'Ford',      'Fiesta',  'Plata');

-- Detalle de servicios (estancias) cerrados, repartidos entre noviembre de 2025 y octubre de 2026
-- id_servicio = 1 corresponde a 'Estancia por hora'
INSERT INTO detalle_servicios (id_detalle_servicio, matricula, id_servicio, id_usuario, fecha_entrada, fecha_salida) VALUES
  (1,  'ABC1234', 1, 2, '2025-11-04 08:10:00', '2025-11-04 09:45:00'),
  (2,  'XYZ9876', 1, 2, '2025-11-04 17:45:00', '2025-11-04 20:45:00'),
  (3,  'MNP2345', 1, 2, '2025-12-02 09:00:00', '2025-12-02 16:00:00'),
  (4,  'ABC1234', 1, 2, '2025-12-15 18:20:00', '2025-12-15 19:35:00'),
  (5,  'QRS8765', 1, 2, '2025-12-15 18:40:00', '2025-12-15 23:40:00'),
  (6,  'JKL4567', 1, 2, '2026-01-08 08:05:00', '2026-01-08 10:15:00'),
  (7,  'TUV1122', 1, 2, '2026-01-20 13:30:00', '2026-01-20 14:15:00'),
  (8,  'MNP2345', 1, 2, '2026-01-21 08:15:00', '2026-01-21 16:45:00'),
  (9,  'XYZ9876', 1, 2, '2026-02-03 17:10:00', '2026-02-03 21:30:00'),
  (10, 'ABC1234', 1, 1, '2026-02-14 12:00:00', '2026-02-14 14:30:00'),
  (11, 'QRS8765', 1, 2, '2026-02-14 08:30:00', '2026-02-14 14:30:00'),
  (12, 'JKL4567', 1, 2, '2026-03-05 18:00:00', '2026-03-05 19:30:00'),
  (13, 'MNP2345', 1, 2, '2026-03-10 08:00:00', '2026-03-10 15:30:00'),
  (14, 'TUV1122', 1, 2, '2026-03-22 15:40:00', '2026-03-22 19:00:00'),
  (15, 'ABC1234', 1, 2, '2026-04-07 08:25:00', '2026-04-07 10:15:00'),
  (16, 'XYZ9876', 1, 2, '2026-04-18 19:05:00', '2026-04-18 20:10:00'),
  (17, 'QRS8765', 1, 2, '2026-05-12 08:50:00', '2026-05-12 15:50:00'),
  (18, 'JKL4567', 1, 2, '2026-05-25 17:30:00', '2026-05-25 21:30:00'),
  (19, 'MNP2345', 1, 2, '2026-06-09 08:10:00', '2026-06-09 13:10:00'),
  (20, 'TUV1122', 1, 2, '2026-06-30 12:15:00', '2026-06-30 13:40:00'),
  (21, 'ABC1234', 1, 2, '2026-07-14 08:40:00', '2026-07-14 11:15:00'),
  (22, 'XYZ9876', 1, 2, '2026-08-04 18:10:00', '2026-08-04 19:50:00'),
  (23, 'QRS8765', 1, 2, '2026-09-16 08:20:00', '2026-09-16 14:40:00'),
  (24, 'JKL4567', 1, 2, '2026-10-06 17:50:00', '2026-10-06 19:55:00'),
  (25, 'MNP2345', 1, 2, '2026-09-22 08:05:00', '2026-09-22 16:05:00'),
  (26, 'ABC1234', 1, 2, '2026-10-28 08:15:00', '2026-10-28 09:25:00');

-- Un servicio que sigue dentro del estacionamiento (sin salida)
INSERT INTO detalle_servicios (id_detalle_servicio, matricula, id_servicio, id_usuario, fecha_entrada, fecha_salida) VALUES
  (27, 'JKL4567', 1, 2, '2026-11-09 08:00:00', NULL);

-- Pensión de prueba (el precio es un valor provisional, falta decidirlo en equipo)
INSERT INTO pensiones (id_pension, id_cliente, matricula, id_usuario, fecha_inicio, fecha_fin, monto) VALUES
  (1, 2, 'MNP2345', 1, '2026-10-01', '2026-10-31', 1200.00);

-- Cobros (recibos maestros)
INSERT INTO cobros (id_cobro, id_usuario, monto_total, fecha_cobro) VALUES
  (1,  2, 47.50,   '2025-11-04 09:45:00'),
  (2,  2, 90.00,   '2025-11-04 20:45:00'),
  (3,  2, 174.00,  '2025-12-02 16:00:00'),
  (4,  2, 37.50,   '2025-12-15 19:35:00'),
  (5,  2, 130.00,  '2025-12-15 23:40:00'),
  (6,  2, 65.00,   '2026-01-08 10:15:00'),
  (7,  2, 22.50,   '2026-01-20 14:15:00'),
  (8,  2, 207.00,  '2026-01-21 16:45:00'),
  (9,  2, 130.00,  '2026-02-03 21:30:00'),
  (10, 1, 75.00,   '2026-02-14 14:30:00'),
  (11, 2, 152.00,  '2026-02-14 14:30:00'),
  (12, 2, 45.00,   '2026-03-05 19:30:00'),
  (13, 2, 185.00,  '2026-03-10 15:30:00'),
  (14, 2, 100.00,  '2026-03-22 19:00:00'),
  (15, 2, 55.00,   '2026-04-07 10:15:00'),
  (16, 2, 32.50,   '2026-04-18 20:10:00'),
  (17, 2, 174.00,  '2026-05-12 15:50:00'),
  (18, 2, 120.00,  '2026-05-25 21:30:00'),
  (19, 2, 130.00,  '2026-06-09 13:10:00'),
  (20, 2, 42.50,   '2026-06-30 13:40:00'),
  (21, 2, 77.50,   '2026-07-14 11:15:00'),
  (22, 2, 50.00,   '2026-08-04 19:50:00'),
  (23, 2, 159.33,  '2026-09-16 14:40:00'),
  (24, 2, 62.50,   '2026-10-06 19:55:00'),
  (25, 2, 196.00,  '2026-09-22 16:05:00'),
  (26, 2, 35.00,   '2026-10-28 09:25:00'),
  (27, 1, 1200.00, '2026-10-01 09:00:00');

-- Detalle de cobros (desglose por vehículo y concepto)
INSERT INTO detalle_cobros (id_detalle_cobro, id_cobro, matricula, id_detalle_servicio, id_pension, horas_cobradas, monto) VALUES
  (1,  1,  'ABC1234', 1,    NULL, 1.58, 47.50),
  (2,  2,  'XYZ9876', 2,    NULL, 3.0,  90.00),
  (3,  3,  'MNP2345', 3,    NULL, 7.0,  174.00),
  (4,  4,  'ABC1234', 4,    NULL, 1.25, 37.50),
  (5,  5,  'QRS8765', 5,    NULL, 5.0,  130.00),
  (6,  6,  'JKL4567', 6,    NULL, 2.17, 65.00),
  (7,  7,  'TUV1122', 7,    NULL, 0.75, 22.50),
  (8,  8,  'MNP2345', 8,    NULL, 8.5,  207.00),
  (9,  9,  'XYZ9876', 9,    NULL, 4.33, 130.00),
  (10, 10, 'ABC1234', 10,   NULL, 2.5,  75.00),
  (11, 11, 'QRS8765', 11,   NULL, 6.0,  152.00),
  (12, 12, 'JKL4567', 12,   NULL, 1.5,  45.00),
  (13, 13, 'MNP2345', 13,   NULL, 7.5,  185.00),
  (14, 14, 'TUV1122', 14,   NULL, 3.33, 100.00),
  (15, 15, 'ABC1234', 15,   NULL, 1.83, 55.00),
  (16, 16, 'XYZ9876', 16,   NULL, 1.08, 32.50),
  (17, 17, 'QRS8765', 17,   NULL, 7.0,  174.00),
  (18, 18, 'JKL4567', 18,   NULL, 4.0,  120.00),
  (19, 19, 'MNP2345', 19,   NULL, 5.0,  130.00),
  (20, 20, 'TUV1122', 20,   NULL, 1.42, 42.50),
  (21, 21, 'ABC1234', 21,   NULL, 2.58, 77.50),
  (22, 22, 'XYZ9876', 22,   NULL, 1.67, 50.00),
  (23, 23, 'QRS8765', 23,   NULL, 6.33, 159.33),
  (24, 24, 'JKL4567', 24,   NULL, 2.08, 62.50),
  (25, 25, 'MNP2345', 25,   NULL, 8.0,  196.00),
  (26, 26, 'ABC1234', 26,   NULL, 1.17, 35.00),
  (27, 27, 'MNP2345', NULL, 1,    NULL, 1200.00);
