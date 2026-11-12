-- =====================================================================
-- Proyecto Final: Estacionamiento Público
-- Script 03: Función y Procedimiento de Cobro (Issue #6)
-- Tarifa escalonada, proporcional por minuto y validación de pensión.
-- =====================================================================
USE estacionamiento;

DELIMITER $$

-- ---------------------------------------------------------------------
-- 1. fn_calcular_cobro_horas
-- Calcula el importe según el número de horas y tipo de cliente
-- aplicando la tarifa escalonada (tramo 1: <= 5h, tramo 2: > 5h).
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_calcular_cobro_horas$$
CREATE FUNCTION fn_calcular_cobro_horas(
    p_horas DECIMAL(10,4),
    p_tipo_cliente ENUM('frecuente','paso')
)
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_precio_t1 DECIMAL(8,2) DEFAULT 0.00;
    DECLARE v_precio_t2 DECIMAL(8,2) DEFAULT 0.00;
    DECLARE v_horas_t1  DECIMAL(10,4) DEFAULT 0.0000;
    DECLARE v_horas_t2  DECIMAL(10,4) DEFAULT 0.0000;
    DECLARE v_total     DECIMAL(10,2) DEFAULT 0.00;

    -- Si las horas son nulas, cero o negativas, no hay cobro
    IF p_horas IS NULL OR p_horas <= 0 THEN
        RETURN 0.00;
    END IF;

    -- Obtener tarifa del tramo 1 (primeras 5 horas)
    SELECT precio_hora INTO v_precio_t1
    FROM precios
    WHERE tipo_cliente = p_tipo_cliente AND hora_hasta = 5
    LIMIT 1;

    -- Obtener tarifa del tramo 2 (de la 6ª hora en adelante)
    SELECT precio_hora INTO v_precio_t2
    FROM precios
    WHERE tipo_cliente = p_tipo_cliente AND hora_hasta IS NULL
    LIMIT 1;

    -- Cálculo escalonado y proporcional
    SET v_horas_t1 = LEAST(p_horas, 5.0);
    SET v_horas_t2 = GREATEST(p_horas - 5.0, 0.0);
    SET v_total = (v_horas_t1 * v_precio_t1) + (v_horas_t2 * v_precio_t2);

    RETURN ROUND(v_total, 2);
END$$

-- ---------------------------------------------------------------------
-- 2. fn_tiene_pension_vigente
-- Retorna 1 si el vehículo tiene una pensión vigente para la fecha indicada,
-- o 0 en caso contrario.
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_tiene_pension_vigente$$
CREATE FUNCTION fn_tiene_pension_vigente(
    p_matricula VARCHAR(15),
    p_fecha DATETIME
)
RETURNS TINYINT(1)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_count INT DEFAULT 0;

    IF p_matricula IS NULL OR p_fecha IS NULL THEN
        RETURN 0;
    END IF;

    SELECT COUNT(*) INTO v_count
    FROM pensiones
    WHERE matricula = p_matricula
      AND DATE(p_fecha) BETWEEN fecha_inicio AND fecha_fin;

    IF v_count > 0 THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 3. fn_calcular_cobro_servicio
-- Retorna el monto a cobrar por un servicio registrado en detalle_servicios.
-- Si p_fecha_salida es NULL, usa la fecha_salida registrada o NOW().
-- Si el vehículo tiene pensión vigente, retorna 0.00.
-- ---------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_calcular_cobro_servicio$$
CREATE FUNCTION fn_calcular_cobro_servicio(
    p_id_detalle_servicio INT,
    p_fecha_salida DATETIME
)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_matricula     VARCHAR(15);
    DECLARE v_fecha_entrada DATETIME;
    DECLARE v_fecha_salida  DATETIME;
    DECLARE v_tipo_cliente  ENUM('frecuente','paso');
    DECLARE v_minutos       INT;
    DECLARE v_horas         DECIMAL(10,4);

    -- Consultar los datos de la estancia del vehículo
    SELECT ds.matricula, ds.fecha_entrada, COALESCE(p_fecha_salida, ds.fecha_salida, NOW()), c.tipo_cliente
    INTO v_matricula, v_fecha_entrada, v_fecha_salida, v_tipo_cliente
    FROM detalle_servicios ds
    JOIN vehiculos v ON ds.matricula = v.matricula
    JOIN clientes c ON v.id_cliente = c.id_cliente
    WHERE ds.id_detalle_servicio = p_id_detalle_servicio
    LIMIT 1;

    -- Si no existe el registro o la salida es previa a la entrada
    IF v_matricula IS NULL OR v_fecha_salida < v_fecha_entrada THEN
        RETURN 0.00;
    END IF;

    -- Si el vehículo cuenta con pensión vigente en la fecha de salida, no se cobra estancia
    IF fn_tiene_pension_vigente(v_matricula, v_fecha_salida) = 1 THEN
        RETURN 0.00;
    END IF;

    -- Cálculo de minutos y horas
    SET v_minutos = TIMESTAMPDIFF(MINUTE, v_fecha_entrada, v_fecha_salida);
    SET v_horas = v_minutos / 60.0;

    RETURN fn_calcular_cobro_horas(v_horas, v_tipo_cliente);
END$$

-- ---------------------------------------------------------------------
-- 4. sp_calcular_cobro_servicio
-- Procedimiento almacenado para consumir cómodamente desde Python.
-- Devuelve un conjunto de resultados con todo el desglose:
-- id_detalle_servicio, matricula, cliente, minutos, horas_cobradas,
-- tiene_pension, monto y motivo.
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_calcular_cobro_servicio$$
CREATE PROCEDURE sp_calcular_cobro_servicio(
    IN p_id_detalle_servicio INT,
    IN p_fecha_salida DATETIME
)
BEGIN
    DECLARE v_matricula     VARCHAR(15);
    DECLARE v_id_cliente    INT;
    DECLARE v_nombre_cliente VARCHAR(100);
    DECLARE v_tipo_cliente  ENUM('frecuente','paso');
    DECLARE v_fecha_entrada DATETIME;
    DECLARE v_fecha_salida  DATETIME;
    DECLARE v_minutos       INT DEFAULT 0;
    DECLARE v_horas         DECIMAL(10,4) DEFAULT 0.0000;
    DECLARE v_horas_redondeadas DECIMAL(6,2) DEFAULT 0.00;
    DECLARE v_tiene_pension TINYINT(1) DEFAULT 0;
    DECLARE v_monto         DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_motivo        VARCHAR(100) DEFAULT '';

    -- Consultar información del servicio, vehículo y cliente
    SELECT ds.matricula, ds.fecha_entrada, COALESCE(p_fecha_salida, ds.fecha_salida, NOW()),
           c.id_cliente, c.nombre, c.tipo_cliente
    INTO v_matricula, v_fecha_entrada, v_fecha_salida,
         v_id_cliente, v_nombre_cliente, v_tipo_cliente
    FROM detalle_servicios ds
    JOIN vehiculos v ON ds.matricula = v.matricula
    JOIN clientes c ON v.id_cliente = c.id_cliente
    WHERE ds.id_detalle_servicio = p_id_detalle_servicio
    LIMIT 1;

    IF v_matricula IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El servicio especificado no existe.';
    END IF;

    IF v_fecha_salida < v_fecha_entrada THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La fecha de salida no puede ser anterior a la de entrada.';
    END IF;

    -- Validar pensión y calcular tiempo
    SET v_tiene_pension = fn_tiene_pension_vigente(v_matricula, v_fecha_salida);
    SET v_minutos = TIMESTAMPDIFF(MINUTE, v_fecha_entrada, v_fecha_salida);
    SET v_horas = v_minutos / 60.0;
    SET v_horas_redondeadas = ROUND(v_horas, 2);

    IF v_tiene_pension = 1 THEN
        SET v_monto = 0.00;
        SET v_motivo = 'Pensión vigente ($0.00)';
    ELSE
        SET v_monto = fn_calcular_cobro_horas(v_horas, v_tipo_cliente);
        IF v_tipo_cliente = 'frecuente' THEN
            SET v_motivo = 'Tarifa frecuente';
        ELSE
            SET v_motivo = 'Tarifa normal (paso)';
        END IF;
    END IF;

    -- Devolver conjunto de resultados
    SELECT 
        p_id_detalle_servicio AS id_detalle_servicio,
        v_matricula           AS matricula,
        v_id_cliente          AS id_cliente,
        v_nombre_cliente      AS cliente,
        v_tipo_cliente        AS tipo_cliente,
        v_fecha_entrada       AS fecha_entrada,
        v_fecha_salida        AS fecha_salida,
        v_minutos             AS minutos_estancia,
        v_horas_redondeadas   AS horas_cobradas,
        v_tiene_pension       AS tiene_pension,
        v_monto               AS monto,
        v_motivo              AS motivo;
END$$

DELIMITER ;

-- =====================================================================
-- CASOS DE PRUEBA (Criterios de aceptación del Issue #6 y README)
-- =====================================================================
-- 1. 7 h cliente de paso     -> Esperado: $200.00
-- 2. 7 h cliente frecuente   -> Esperado: $174.00
-- 3. 7.5 h cliente de paso   -> Esperado: $212.50
-- =====================================================================
SELECT 
    '7h paso' AS caso,
    fn_calcular_cobro_horas(7.0, 'paso') AS obtenido,
    200.00 AS esperado,
    IF(fn_calcular_cobro_horas(7.0, 'paso') = 200.00, 'CORRECTO', 'FALLÓ') AS estado
UNION ALL
SELECT 
    '7h frecuente' AS caso,
    fn_calcular_cobro_horas(7.0, 'frecuente') AS obtenido,
    174.00 AS esperado,
    IF(fn_calcular_cobro_horas(7.0, 'frecuente') = 174.00, 'CORRECTO', 'FALLÓ') AS estado
UNION ALL
SELECT 
    '7.5h paso' AS caso,
    fn_calcular_cobro_horas(7.5, 'paso') AS obtenido,
    212.50 AS esperado,
    IF(fn_calcular_cobro_horas(7.5, 'paso') = 212.50, 'CORRECTO', 'FALLÓ') AS estado;
