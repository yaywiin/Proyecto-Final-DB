# Estacionamiento Público

Proyecto final de la materia de Base de Datos (Prof. Ramiro Luperco Coronel). Equipo de 3 personas.

## ¿Qué es?

Un sistema de escritorio para administrar un estacionamiento público. Registra la entrada y la salida de los vehículos, calcula cuánto se debe cobrar según el tiempo de estancia, controla las pensiones y genera reportes de demanda e ingresos.

## Objetivo

Entregar un sistema que cumpla los 10 requisitos del enunciado, con la base de datos bien diseñada (llaves, vistas, triggers) y una interfaz sencilla de usar para el cobrador y el administrador.

## Tecnología

| Parte | Herramienta |
|---|---|
| Base de datos | XAMPP (MariaDB) |
| Lenguaje | Python |
| Interfaz | Tkinter |
| Patrón | MVC (Modelo-Vista-Controlador) |
| Control de versiones | Git (repositorio compartido) |

## Cómo funcionará

### Perfiles

- **Admin:** control operativo de todo el sistema (usuarios, clientes, vehículos, precios, pensiones y reportes).
- **Cobrador:** solo registra vehículos, hora de entrada y salida y datos del cliente.

Ambos entran con usuario y contraseña. La contraseña se guarda como hash SHA-256, nunca en texto plano.

### Clientes

- Por defecto todos entran como **"Público general"** (`cliente_id = 1`) y pagan tarifa normal.
- Quien quiera puede registrarse con sus datos.
- Un cliente registrado se vuelve **frecuente** automáticamente al llegar a cierto número de visitas, y desde entonces paga la tarifa de frecuente.
- Las pensiones solo se pueden contratar con clientes registrados.

### Entrada y salida

1. El cobrador registra la **entrada**: matrícula, datos del vehículo y del cliente, fecha y hora.
2. Al salir, el cobrador registra la **salida** y el sistema calcula el monto.
3. Se guarda el **cobro** con el monto, el tiempo de estancia y el cobrador que lo hizo.

### Tarifa (cajón)

El cobro es **escalonado** y **proporcional** (por minuto).

| Cliente | Primeras 5 horas | De la 6ª hora en adelante |
|---|---|---|
| Normal | $30.00 / h | $25.00 / h |
| Frecuente | $26.00 / h | $22.00 / h |

Ejemplos: 7 h normal = $200.00, 7 h frecuente = $174.00, 7.5 h normal = $212.50.

Si el vehículo tiene una pensión vigente, no se cobra por hora.

### Pensión

Se controla por fecha y por vehículo, y hay descuento para clientes con más de 2 años de pensión. El precio y el porcentaje de descuento todavía están por definir.

### Reportes

| # | Reporte |
|---|---|
| 7 | Entradas y salidas por mes |
| 8 | Meses con mayor demanda por año |
| 9 | Horarios con mayor demanda por año |
| 10 | Ingresos por servicio de acuerdo al año |

## Estructura de la base de datos

Tablas: `Usuarios`, `Clientes`, `Vehiculos`, `Precios`, `Servicios`, `Cobros` y `Pensiones`. El detalle, el diagrama ER y las reglas de integridad están en [Modelo_Datos.md](docs/Modelo_Datos.md).

## Reparto del equipo

| Rol | Responsable | Tareas |
|---|---|---|
| A · Base de datos | Carlos | Script SQL (tablas, llaves, datos de prueba), triggers, vistas de reportes, función de cobro |
| B · Usuarios y catálogos | Cristobal | Login, roles, CRUD de usuarios, clientes y vehículos |
| C · Operación | Yael | Entradas y salidas, cálculo y registro de cobros, pensiones, pantalla de reportes |
| Todos | Equipo | Módulo de conexión a la BD y repositorio Git |

Los roles no son cerrados: nos ayudamos entre todos.

## Estructura de carpetas prevista (MVC)

```
Proyecto Final/
├── README.md
├── docs/           # modelo de datos, forma de trabajo y guía de inicio
├── sql/            # script de tablas, datos de prueba, vistas y triggers
├── modelo/         # acceso a la BD (consultas)
├── vista/          # ventanas Tkinter
├── controlador/    # lógica: login, cálculo de cobros, validaciones
└── main.py         # punto de entrada
```

Es una propuesta y puede cambiar cuando se empiece el código.

## Documentación

| Archivo | Para qué sirve |
|---|---|
| [docs/Modelo_Datos.md](docs/Modelo_Datos.md) | Tablas, columnas, diagrama ER y reglas de integridad |
| [docs/WoW.md](docs/WoW.md) | Cómo trabajamos: ramas, pull requests, revisiones y comunicación |
| [docs/Guia_Inicio.md](docs/Guia_Inicio.md) | Comandos paso a paso: instalar, crear la base, subir cambios y abrir un PR |

## Pasos a seguir

- [x] Definir el stack, el patrón y la tarifa.
- [x] Decidir fracciones de hora, clientes frecuentes, clientes de paso y contraseñas.
- [x] Proponer el modelo de datos ([Modelo_Datos.md](docs/Modelo_Datos.md)).
- [ ] Definir la pensión: modalidad, precio y % de descuento después de 2 años.
- [ ] Definir cuántas visitas hacen frecuente a un cliente.
- [ ] Resolver las dudas con el profesor (abajo).
- [ ] Cerrar el modelo de datos y el diagrama ER.
- [ ] Script SQL: tablas con llaves primarias y foráneas, y datos de prueba.
- [ ] Triggers, vistas de reportes y función de cobro.
- [ ] Módulo de conexión a la BD y estructura MVC en Git.
- [ ] Login y perfiles.
- [ ] CRUD de usuarios, clientes y vehículos.
- [ ] Entradas, salidas y cobros.
- [ ] Pensiones.
- [ ] Pantalla de reportes.
- [ ] Pruebas con datos de ejemplo y entrega.

## Ideas para subir la calificación

- Procedimientos almacenados, vistas y triggers.
- Gráficas de los reportes con matplotlib.
- Sistema de puntos y descuentos para clientes registrados (idea de Cristobal, fuera del diseño base).
