-- =====================================================================
-- Proyecto Final: Estacionamiento Público
-- Script 05: Reglas Automáticas e Integridad mediante Triggers (Issue #11)
-- =====================================================================
USE estacionamiento;

DELIMITER $$

-- ---------------------------------------------------------------------
-- 1. tg_evitar_doble_entrada
-- Impide registrar una nueva entrada para un vehículo que ya se
-- encuentra dentro del estacionamiento (con fecha_salida IS NULL).
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS tg_evitar_doble_entrada$$
CREATE TRIGGER tg_evitar_doble_entrada
BEFORE INSERT ON detalle_servicios
FOR EACH ROW
BEGIN
    DECLARE v_abiertos INT DEFAULT 0;

    -- Contar estancias activas para la misma matrícula
    SELECT COUNT(*) INTO v_abiertos
    FROM detalle_servicios
    WHERE matricula = NEW.matricula
      AND fecha_salida IS NULL;

    IF v_abiertos > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El vehículo ya se encuentra dentro del estacionamiento (tiene una entrada abierta sin salida).';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 2. tg_actualizar_cliente_frecuente
-- Al registrarse la fecha_salida de una estancia, cuenta las visitas
-- completadas del cliente en los últimos N días (según la tabla parametros).
-- Si cumple o supera el umbral, se actualiza automáticamente a 'frecuente'.
-- Aplica únicamente para clientes registrados (id_cliente > 1).
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS tg_actualizar_cliente_frecuente$$
CREATE TRIGGER tg_actualizar_cliente_frecuente
AFTER UPDATE ON detalle_servicios
FOR EACH ROW
BEGIN
    DECLARE v_id_cliente        INT;
    DECLARE v_tipo_actual       ENUM('frecuente','paso');
    DECLARE v_visitas_meta      INT DEFAULT 10;
    DECLARE v_dias_periodo      INT DEFAULT 30;
    DECLARE v_visitas_acum      INT DEFAULT 0;

    -- Solo actuar cuando se acaba de registrar la salida
    IF OLD.fecha_salida IS NULL AND NEW.fecha_salida IS NOT NULL THEN
        -- Obtener el cliente dueño del vehículo
        SELECT id_cliente INTO v_id_cliente
        FROM vehiculos
        WHERE matricula = NEW.matricula
        LIMIT 1;

        -- Excluir 'Público general' (id_cliente = 1)
        IF v_id_cliente IS NOT NULL AND v_id_cliente > 1 THEN
            SELECT tipo_cliente INTO v_tipo_actual
            FROM clientes
            WHERE id_cliente = v_id_cliente;

            -- Solo verificar si actualmente es de paso
            IF v_tipo_actual = 'paso' THEN
                -- Obtener parámetros dinámicos de configuración
                SELECT CAST(valor AS UNSIGNED) INTO v_visitas_meta
                FROM parametros
                WHERE clave = 'visitas_para_frecuente'
                LIMIT 1;

                SELECT CAST(valor AS UNSIGNED) INTO v_dias_periodo
                FROM parametros
                WHERE clave = 'periodo_dias_frecuente'
                LIMIT 1;

                -- Contar estancias completadas del cliente dentro del periodo
                SELECT COUNT(*) INTO v_visitas_acum
                FROM detalle_servicios ds
                JOIN vehiculos v ON ds.matricula = v.matricula
                WHERE v.id_cliente = v_id_cliente
                  AND ds.fecha_salida IS NOT NULL
                  AND ds.fecha_salida >= DATE_SUB(NEW.fecha_salida, INTERVAL v_dias_periodo DAY);

                -- Si cumplió el número de visitas en el periodo, promoverlo a frecuente
                IF v_visitas_acum >= v_visitas_meta THEN
                    UPDATE clientes
                    SET tipo_cliente = 'frecuente'
                    WHERE id_cliente = v_id_cliente;
                END IF;
            END IF;
        END IF;
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 3. tg_validar_cobro_estancia
-- Impide generar un cobro para una estancia que aún no tiene
-- registrada su fecha de salida en detalle_servicios.
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS tg_validar_cobro_estancia$$
CREATE TRIGGER tg_validar_cobro_estancia
BEFORE INSERT ON detalle_cobros
FOR EACH ROW
BEGIN
    DECLARE v_salida DATETIME;

    -- Si el cobro corresponde a un servicio de estancia
    IF NEW.id_detalle_servicio IS NOT NULL THEN
        SELECT fecha_salida INTO v_salida
        FROM detalle_servicios
        WHERE id_detalle_servicio = NEW.id_detalle_servicio
        LIMIT 1;

        IF v_salida IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'No se puede cobrar una estancia que no tiene registrada su fecha de salida.';
        END IF;
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 4. tg_validar_fechas_servicio
-- Impide registrar o actualizar una estancia con fecha_salida anterior
-- a la fecha_entrada.
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS tg_validar_fechas_servicio_insert$$
CREATE TRIGGER tg_validar_fechas_servicio_insert
BEFORE INSERT ON detalle_servicios
FOR EACH ROW
BEGIN
    IF NEW.fecha_salida IS NOT NULL AND NEW.fecha_salida < NEW.fecha_entrada THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La fecha de salida no puede ser anterior a la fecha de entrada.';
    END IF;
END$$

DROP TRIGGER IF EXISTS tg_validar_fechas_servicio_update$$
CREATE TRIGGER tg_validar_fechas_servicio_update
BEFORE UPDATE ON detalle_servicios
FOR EACH ROW
BEGIN
    IF NEW.fecha_salida IS NOT NULL AND NEW.fecha_salida < NEW.fecha_entrada THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La fecha de salida no puede ser anterior a la fecha de entrada.';
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 5. tg_validar_cajon_servicio
-- Valida que el cajón asignado a una estancia (detalle_servicios):
--   a) Esté dentro del rango permitido (1 a total_cajones de parametros).
--   b) No esté ocupado por otro vehículo (fecha_salida IS NULL).
--   c) No esté apartado por la pensión vigente de otro vehículo.
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS tg_validar_cajon_servicio_insert$$
CREATE TRIGGER tg_validar_cajon_servicio_insert
BEFORE INSERT ON detalle_servicios
FOR EACH ROW
BEGIN
    DECLARE v_total_cajones     INT DEFAULT 30;
    DECLARE v_ocupado           INT DEFAULT 0;
    DECLARE v_reservado_pension INT DEFAULT 0;

    IF NEW.numero_cajon IS NOT NULL THEN
        -- Obtener total de cajones configurado
        SELECT CAST(valor AS UNSIGNED) INTO v_total_cajones
        FROM parametros
        WHERE clave = 'total_cajones'
        LIMIT 1;

        IF v_total_cajones IS NULL THEN
            SET v_total_cajones = 30;
        END IF;

        -- Regla a: Cajón dentro del rango permitido
        IF NEW.numero_cajon < 1 OR NEW.numero_cajon > v_total_cajones THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El número de cajón está fuera del rango permitido.';
        END IF;

        -- Si la estancia está abierta (vehículo dentro), validar ocupación y pensión
        IF NEW.fecha_salida IS NULL THEN
            -- Regla b: No ocupado por otro vehículo actualmente
            SELECT COUNT(*) INTO v_ocupado
            FROM detalle_servicios
            WHERE numero_cajon = NEW.numero_cajon
              AND fecha_salida IS NULL;

            IF v_ocupado > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El cajón seleccionado ya se encuentra ocupado por otro vehículo.';
            END IF;

            -- Regla c: No apartado por la pensión vigente de otro vehículo
            SELECT COUNT(*) INTO v_reservado_pension
            FROM pensiones
            WHERE numero_cajon = NEW.numero_cajon
              AND DATE(NEW.fecha_entrada) BETWEEN fecha_inicio AND fecha_fin
              AND matricula != NEW.matricula;

            IF v_reservado_pension > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El cajón seleccionado está reservado por una pensión activa de otro vehículo.';
            END IF;
        END IF;
    END IF;
END$$

DROP TRIGGER IF EXISTS tg_validar_cajon_servicio_update$$
CREATE TRIGGER tg_validar_cajon_servicio_update
BEFORE UPDATE ON detalle_servicios
FOR EACH ROW
BEGIN
    DECLARE v_total_cajones     INT DEFAULT 30;
    DECLARE v_ocupado           INT DEFAULT 0;
    DECLARE v_reservado_pension INT DEFAULT 0;

    IF NEW.numero_cajon IS NOT NULL THEN
        -- Obtener total de cajones configurado
        SELECT CAST(valor AS UNSIGNED) INTO v_total_cajones
        FROM parametros
        WHERE clave = 'total_cajones'
        LIMIT 1;

        IF v_total_cajones IS NULL THEN
            SET v_total_cajones = 30;
        END IF;

        -- Regla a: Cajón dentro del rango permitido
        IF NEW.numero_cajon < 1 OR NEW.numero_cajon > v_total_cajones THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El número de cajón está fuera del rango permitido.';
        END IF;

        -- Si la estancia sigue abierta (sin salida), validar ocupación y pensión
        IF NEW.fecha_salida IS NULL THEN
            -- Regla b: No ocupado por otro registro activo distinto
            SELECT COUNT(*) INTO v_ocupado
            FROM detalle_servicios
            WHERE numero_cajon = NEW.numero_cajon
              AND fecha_salida IS NULL
              AND id_detalle_servicio != NEW.id_detalle_servicio;

            IF v_ocupado > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El cajón seleccionado ya se encuentra ocupado por otro vehículo.';
            END IF;

            -- Regla c: No apartado por la pensión vigente de otro vehículo
            SELECT COUNT(*) INTO v_reservado_pension
            FROM pensiones
            WHERE numero_cajon = NEW.numero_cajon
              AND DATE(NEW.fecha_entrada) BETWEEN fecha_inicio AND fecha_fin
              AND matricula != NEW.matricula;

            IF v_reservado_pension > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El cajón seleccionado está reservado por una pensión activa de otro vehículo.';
            END IF;
        END IF;
    END IF;
END$$

-- ---------------------------------------------------------------------
-- 6. tg_validar_cajon_pension
-- Valida que el cajón asignado a una pensión:
--   a) Esté dentro del rango permitido (1 a total_cajones de parametros).
--   b) No se traslape con otra pensión en el mismo cajón.
--   c) No esté ocupado actualmente por otro vehículo si la pensión está vigente hoy.
-- ---------------------------------------------------------------------
DROP TRIGGER IF EXISTS tg_validar_cajon_pension_insert$$
CREATE TRIGGER tg_validar_cajon_pension_insert
BEFORE INSERT ON pensiones
FOR EACH ROW
BEGIN
    DECLARE v_total_cajones INT DEFAULT 30;
    DECLARE v_traslape      INT DEFAULT 0;
    DECLARE v_ocupado       INT DEFAULT 0;

    IF NEW.numero_cajon IS NOT NULL THEN
        -- Obtener total de cajones configurado
        SELECT CAST(valor AS UNSIGNED) INTO v_total_cajones
        FROM parametros
        WHERE clave = 'total_cajones'
        LIMIT 1;

        IF v_total_cajones IS NULL THEN
            SET v_total_cajones = 30;
        END IF;

        -- Regla a: Cajón dentro del rango permitido
        IF NEW.numero_cajon < 1 OR NEW.numero_cajon > v_total_cajones THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El número de cajón está fuera del rango permitido.';
        END IF;

        -- Regla b: No traslape con otra pensión en las mismas fechas
        SELECT COUNT(*) INTO v_traslape
        FROM pensiones
        WHERE numero_cajon = NEW.numero_cajon
          AND fecha_inicio <= NEW.fecha_fin
          AND fecha_fin >= NEW.fecha_inicio;

        IF v_traslape > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El cajón seleccionado ya está reservado por otra pensión en ese periodo.';
        END IF;

        -- Regla c: Si la pensión cubre hoy, no debe estar ocupado por otro vehículo
        IF CURRENT_DATE BETWEEN NEW.fecha_inicio AND NEW.fecha_fin THEN
            SELECT COUNT(*) INTO v_ocupado
            FROM detalle_servicios
            WHERE numero_cajon = NEW.numero_cajon
              AND fecha_salida IS NULL
              AND matricula != NEW.matricula;

            IF v_ocupado > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El cajón seleccionado se encuentra actualmente ocupado por otro vehículo.';
            END IF;
        END IF;
    END IF;
END$$

DROP TRIGGER IF EXISTS tg_validar_cajon_pension_update$$
CREATE TRIGGER tg_validar_cajon_pension_update
BEFORE UPDATE ON pensiones
FOR EACH ROW
BEGIN
    DECLARE v_total_cajones INT DEFAULT 30;
    DECLARE v_traslape      INT DEFAULT 0;
    DECLARE v_ocupado       INT DEFAULT 0;

    IF NEW.numero_cajon IS NOT NULL THEN
        -- Obtener total de cajones configurado
        SELECT CAST(valor AS UNSIGNED) INTO v_total_cajones
        FROM parametros
        WHERE clave = 'total_cajones'
        LIMIT 1;

        IF v_total_cajones IS NULL THEN
            SET v_total_cajones = 30;
        END IF;

        -- Regla a: Cajón dentro del rango permitido
        IF NEW.numero_cajon < 1 OR NEW.numero_cajon > v_total_cajones THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El número de cajón está fuera del rango permitido.';
        END IF;

        -- Regla b: No traslape con otra pensión (excluyendo este mismo registro)
        SELECT COUNT(*) INTO v_traslape
        FROM pensiones
        WHERE numero_cajon = NEW.numero_cajon
          AND fecha_inicio <= NEW.fecha_fin
          AND fecha_fin >= NEW.fecha_inicio
          AND id_pension != NEW.id_pension;

        IF v_traslape > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El cajón seleccionado ya está reservado por otra pensión en ese periodo.';
        END IF;

        -- Regla c: Si la pensión cubre hoy, no debe estar ocupado por otro vehículo
        IF CURRENT_DATE BETWEEN NEW.fecha_inicio AND NEW.fecha_fin THEN
            SELECT COUNT(*) INTO v_ocupado
            FROM detalle_servicios
            WHERE numero_cajon = NEW.numero_cajon
              AND fecha_salida IS NULL
              AND matricula != NEW.matricula;

            IF v_ocupado > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El cajón seleccionado se encuentra actualmente ocupado por otro vehículo.';
            END IF;
        END IF;
    END IF;
END$$

DELIMITER ;
