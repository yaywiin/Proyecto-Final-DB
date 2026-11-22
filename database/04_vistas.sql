-- =====================================================================
-- Proyecto Final: Estacionamiento Público
-- Script 04: Vistas de Reportes (Issue #7)
-- Reportes 7 al 10 del sistema listas para consultar y graficar.
-- =====================================================================
USE estacionamiento;

-- ---------------------------------------------------------------------
-- REPORTE 7: Entradas y salidas por mes
-- Agrupa las visitas por año y mes, mostrando el conteo de entradas
-- registradas y el conteo de salidas completadas.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vista_rep_7_entradas_salidas_mes AS
SELECT
    periodos.anio,
    periodos.mes,
    CASE periodos.mes
        WHEN 1 THEN 'Enero'   WHEN 2 THEN 'Febrero'   WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril'   WHEN 5 THEN 'Mayo'      WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio'   WHEN 8 THEN 'Agosto'    WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
    END AS nombre_mes,
    COALESCE(e.total_entradas, 0) AS total_entradas,
    COALESCE(s.total_salidas, 0)  AS total_salidas
FROM (
    SELECT DISTINCT YEAR(fecha_entrada) AS anio, MONTH(fecha_entrada) AS mes
    FROM detalle_servicios
    UNION
    SELECT DISTINCT YEAR(fecha_salida) AS anio, MONTH(fecha_salida) AS mes
    FROM detalle_servicios
    WHERE fecha_salida IS NOT NULL
) AS periodos
LEFT JOIN (
    SELECT 
        YEAR(fecha_entrada) AS anio, 
        MONTH(fecha_entrada) AS mes, 
        COUNT(*) AS total_entradas
    FROM detalle_servicios
    GROUP BY YEAR(fecha_entrada), MONTH(fecha_entrada)
) AS e ON periodos.anio = e.anio AND periodos.mes = e.mes
LEFT JOIN (
    SELECT 
        YEAR(fecha_salida) AS anio, 
        MONTH(fecha_salida) AS mes, 
        COUNT(*) AS total_salidas
    FROM detalle_servicios
    WHERE fecha_salida IS NOT NULL
    GROUP BY YEAR(fecha_salida), MONTH(fecha_salida)
) AS s ON periodos.anio = s.anio AND periodos.mes = s.mes
ORDER BY periodos.anio ASC, periodos.mes ASC;

-- ---------------------------------------------------------------------
-- REPORTE 8: Meses con mayor demanda por año
-- Muestra el número de vehículos atendidos por mes y año,
-- ordenados de mayor a menor afluencia.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vista_rep_8_meses_mayor_demanda AS
SELECT
    YEAR(fecha_entrada) AS anio,
    MONTH(fecha_entrada) AS mes,
    CASE MONTH(fecha_entrada)
        WHEN 1 THEN 'Enero'   WHEN 2 THEN 'Febrero'   WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril'   WHEN 5 THEN 'Mayo'      WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio'   WHEN 8 THEN 'Agosto'    WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
    END AS nombre_mes,
    COUNT(*) AS total_vehiculos
FROM detalle_servicios
GROUP BY YEAR(fecha_entrada), MONTH(fecha_entrada)
ORDER BY anio ASC, total_vehiculos DESC, mes ASC;

-- ---------------------------------------------------------------------
-- REPORTE 9: Horarios con mayor demanda por año
-- Clasifica las entradas por hora del día (0-23 hrs) para identificar
-- las horas pico del estacionamiento en cada año.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vista_rep_9_horarios_mayor_demanda AS
SELECT
    YEAR(fecha_entrada) AS anio,
    HOUR(fecha_entrada) AS hora,
    CONCAT(LPAD(HOUR(fecha_entrada), 2, '0'), ':00 - ', LPAD(HOUR(fecha_entrada), 2, '0'), ':59') AS franja_horaria,
    COUNT(*) AS total_entradas
FROM detalle_servicios
GROUP BY YEAR(fecha_entrada), HOUR(fecha_entrada)
ORDER BY anio ASC, total_entradas DESC, hora ASC;

-- ---------------------------------------------------------------------
-- REPORTE 10: Ingresos por servicio de acuerdo al año
-- Totaliza los ingresos económicos agrupados por año y tipo de servicio
-- ('Estancia por hora' o 'Pensión mensual').
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vista_rep_10_ingresos_por_servicio AS
SELECT
    YEAR(c.fecha_cobro) AS anio,
    COALESCE(s.nombre_servicio, 'Pensión mensual') AS servicio,
    COUNT(dc.id_detalle_cobro) AS total_operaciones,
    SUM(dc.monto) AS total_ingresos
FROM detalle_cobros dc
JOIN cobros c ON dc.id_cobro = c.id_cobro
LEFT JOIN detalle_servicios ds ON dc.id_detalle_servicio = ds.id_detalle_servicio
LEFT JOIN servicios s ON ds.id_servicio = s.id_servicio
GROUP BY YEAR(c.fecha_cobro), COALESCE(s.nombre_servicio, 'Pensión mensual')
ORDER BY anio ASC, total_ingresos DESC;

-- =====================================================================
-- CONSULTAS DE DEMOSTRACIÓN (Para probar con los datos de ejemplo)
-- =====================================================================
-- SELECT * FROM vista_rep_7_entradas_salidas_mes;
-- SELECT * FROM vista_rep_8_meses_mayor_demanda;
-- SELECT * FROM vista_rep_9_horarios_mayor_demanda;
-- SELECT * FROM vista_rep_10_ingresos_por_servicio;
