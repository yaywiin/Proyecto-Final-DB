# Estacionamiento Público

Proyecto final de la materia de Base de Datos (Prof. Ramiro Luperco Coronel). Equipo de 3 personas.

## ¿Qué es?

Un sistema de escritorio para administrar un estacionamiento público. Registra la entrada y la salida de los vehículos, asigna un cajón a cada uno y muestra el croquis del estacionamiento, calcula cuánto se debe cobrar según el tiempo de estancia, controla las pensiones y genera reportes de demanda e ingresos.

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

- **Admin:** control operativo de todo el sistema (usuarios, clientes, vehículos, pensiones y reportes).
- **Cobrador:** solo opera: registra entradas y salidas (con su cobro), consulta el croquis y atiende clientes y vehículos. No ve Usuarios, Pensiones ni Reportes.

Ambos entran con usuario y contraseña. La contraseña se guarda como hash SHA-256, nunca en texto plano.

### Clientes

- Por defecto todos entran como **"Público general"** (`cliente_id = 1`) y pagan tarifa normal.
- Quien quiera puede registrarse con su nombre y teléfono.
- Un cliente registrado se vuelve **frecuente** automáticamente al llegar a 10 visitas en 30 días (un trigger de la base lo hace), y desde entonces paga la tarifa de frecuente.
- Las pensiones solo se pueden contratar con clientes registrados.

### Entrada y salida

1. El cobrador registra la **entrada** con la matrícula y el cajón. Si el vehículo es nuevo, también captura cliente, marca, modelo y color. La fecha y la hora se guardan solas.
2. Al salir, el cobrador registra la **salida**, el sistema calcula el monto y el cajón queda libre.
3. Se guarda el **cobro** con el monto y el cobrador que lo hizo.

### Cajones y croquis

- El estacionamiento tiene **20 cajones**, en 4 filas de 5. Las dos cantidades viven en la tabla `parametros` (`total_cajones` y `cajones_por_fila`).
- El selector de cajón permite escribir y solo lista los disponibles.
- Una pensión **aparta su cajón** durante todo el periodo, aunque el vehículo no esté, y el vehículo pensionado entra a ese cajón. Si está dentro al contratar una pensión que empieza ya, se aparta el cajón que ocupa.
- El módulo **Estacionamiento** dibuja el croquis: verde libre, rojo ocupado y morado pensión. Al pasar el cursor se ven los datos del cajón, y "Actualizar" vuelve a leer la base.

### Tarifa (cajón)

El cobro es **escalonado** y **proporcional** (por minuto).

| Cliente | Primeras 5 horas | De la 6ª hora en adelante |
|---|---|---|
| Normal | $30.00 / h | $25.00 / h |
| Frecuente | $26.00 / h | $22.00 / h |

Ejemplos: 7 h normal = $200.00, 7 h frecuente = $174.00, 7.5 h normal = $212.50.

Si el vehículo tiene una pensión vigente, no se cobra por hora.

### Pensión

Se controla por fecha y por vehículo, y solo la contrata el administrador, con clientes registrados. Se contrata por meses completos: **$1,200.00 por mes**, con **10% de descuento** si el cliente tiene más de 2 años desde su primera pensión. El precio y el descuento viven en la tabla `parametros`, así que se cambian sin tocar el programa. Un vehículo con pensión vigente sale con cobro de $0.00 y no se permiten pensiones que se traslapen.

### Reportes

| # | Reporte |
|---|---|
| 7 | Entradas y salidas por mes |
| 8 | Meses con mayor demanda por año |
| 9 | Horarios con mayor demanda por año |
| 10 | Ingresos por servicio de acuerdo al año |

## Estructura de la base de datos

Tablas: `usuarios`, `clientes`, `vehiculos`, `servicios` (catálogo), `detalle_servicios` (entradas y salidas), `pensiones`, `cobros` (recibo), `detalle_cobros` (desglose), `precios` y `parametros`. Además hay 4 vistas para los reportes, funciones y un procedimiento de cobro, y 9 triggers. El detalle, el diagrama ER y las reglas de integridad están en [Modelo_Datos.md](docs/Modelo_Datos.md).

## Reparto del equipo

| Rol | Responsable | Tareas |
|---|---|---|
| A · Base de datos | Carlos | Script SQL (tablas, llaves, datos de prueba), triggers, vistas de reportes, función de cobro |
| B · Usuarios y catálogos | Cristobal | Login, roles, CRUD de usuarios, clientes y vehículos |
| C · Operación | Yael | Entradas y salidas, cálculo y registro de cobros, pensiones, pantalla de reportes |
| Todos | Equipo | Módulo de conexión a la BD y repositorio Git |

Los roles no son cerrados: nos ayudamos entre todos.

## Estructura de carpetas (MVC)

```
Proyecto Final/
├── README.md
├── docs/           # modelo de datos, forma de trabajo, guía de inicio y guion de la demo
├── database/       # 01 tablas, 02 datos de prueba, 03 cobro, 04 vistas, 05 triggers
├── requirements.txt
└── app/
    ├── main.py            # comprueba la conexión
    ├── config.example.py  # plantilla de configuración (config.py no se sube)
    ├── modelo/            # acceso a la BD; conexion.py abre la conexión
    ├── vista/             # ventanas Tkinter (login, menú, entradas y salidas, croquis, pensiones, reportes, usuarios, clientes y vehículos)
    └── controlador/       # reglas y validaciones de cada módulo
```

## Cómo ejecutarlo

1. Enciende MySQL en XAMPP.
2. Crea la base y sus datos con los scripts de `database/` (ver [docs/Guia_Inicio.md](docs/Guia_Inicio.md)). Si tenías una base anterior a los cajones, vuelve a correrlos.
3. Abre la app: `python -m app.vista.login_vista`.
4. Entra con `admin` / `admin123` (administrador) o `cobrador` / `cobrador123`.

El recorrido completo de la demo está en [docs/Guia_Demo.md](docs/Guia_Demo.md).

## Documentación

| Archivo | Para qué sirve |
|---|---|
| [docs/Modelo_Datos.md](docs/Modelo_Datos.md) | Tablas, columnas, diagrama ER y reglas de integridad |
| [docs/WoW.md](docs/WoW.md) | Cómo trabajamos: ramas, pull requests, revisiones y comunicación |
| [docs/Guia_Inicio.md](docs/Guia_Inicio.md) | Comandos paso a paso: instalar, crear la base, subir cambios y abrir un PR |
| [docs/Guia_Demo.md](docs/Guia_Demo.md) | Guion de la demo: qué mostrar, en qué orden y qué debe pasar |

## Pasos a seguir

- [x] Definir el stack, el patrón y la tarifa.
- [x] Decidir fracciones de hora, clientes frecuentes, clientes de paso y contraseñas.
- [x] Proponer y cerrar el modelo de datos ([Modelo_Datos.md](docs/Modelo_Datos.md)).
- [x] Definir la pensión: por meses, $1,200.00 y 10% de descuento después de 2 años.
- [x] Definir cuántas visitas hacen frecuente a un cliente: 10 en 30 días.
- [x] Script SQL: tablas con llaves, datos de prueba, función de cobro, vistas y triggers.
- [x] Módulo de conexión a la BD y estructura MVC en Git.
- [x] Login y perfiles.
- [x] CRUD de usuarios, clientes y vehículos.
- [x] Entradas, salidas y cobros.
- [x] Pensiones.
- [x] Pantalla de reportes.
- [x] Pruebas con datos de ejemplo.
- [x] Correcciones del profesor: número de cajón y croquis del estacionamiento.
- [ ] Resolver con el profesor qué significa "por cada 5 horas" para clientes frecuentes (hoy se aplica la tarifa escalonada de $26 y $22).
- [ ] Ensayo de la demo y entrega.

## Ideas para subir la calificación

- Procedimientos almacenados, vistas y triggers.
- Gráficas de los reportes con matplotlib.
- Sistema de puntos y descuentos para clientes registrados (idea de Cristobal, fuera del diseño base).
