# Guion de la demo

Recorrido para mostrar el sistema completo en unos 10 minutos. Cada paso dice qué hacer y qué debe pasar.

## Antes de empezar

1. Enciende MySQL en XAMPP.
2. Recrea la base con los datos de prueba (esto borra y vuelve a crear `estacionamiento`):
   ```bash
   for f in database/*.sql; do /Applications/XAMPP/xamppfiles/bin/mysql -u root < "$f"; done
   ```
   En Windows, usa el `mysql.exe` de XAMPP o importa cada archivo de `database/` en orden desde phpMyAdmin.
3. Abre la app: `python -m app.vista.login_vista`.

Usuarios de prueba: `admin` / `admin123` y `cobrador` / `cobrador123`.

## 1. Login y permisos

| Haz esto | Debe pasar |
|---|---|
| Entra con `admin` y una contraseña incorrecta | Aviso "Credenciales incorrectas" |
| Entra con `admin` / `admin123` | Menú con 8 módulos y "ADMIN" arriba |

## 2. Usuarios (admin)

Usuarios → crea `Cobrador Dos`, usuario `cobrador2`, contraseña `clave123`, rol cobrador. Aparece en la lista. Si lo creas otra vez, avisa que ya existe.

## 3. Clientes y vehículos

1. Clientes → crea `Cliente Demo`, teléfono `5551230003`, tipo `paso`, y asígnale el vehículo `ABC1234`, que estaba en "Público general".
2. Vehículos → crea `DEM1234` para `Cliente Demo`: marca `Kia`, modelo `Rio`, color `Rojo`.

Todos los campos son obligatorios. El nombre y la marca no admiten números, y la matrícula lleva de 5 a 7 caracteres, con letras y números.

## 4. Entradas, salidas y cobro

| Haz esto | Debe pasar |
|---|---|
| Entradas y Salidas → matrícula `DEM1234`, cajón `3` → Registrar entrada | Aparece en "Dentro ahora" con su cajón |
| Una matrícula nueva (por ejemplo `NVA0001`) y despliega el selector de cajón | No aparecen el 3 ni el 5 (ocupados) |
| Elige el cajón `4`, el cliente, marca, modelo y color → Registrar entrada | Se crea el vehículo y entra |
| Matrícula `XYZ9876`, escribe `5` como cajón → Registrar entrada | Aviso "El cajón 5 no está disponible" |
| Registrar entrada de `DEM1234` otra vez | Aviso "ya está dentro" |
| Registrar salida de `NVA0001` | Cuadro de cobro con el cajón y el monto. Esc cancela y sigue dentro; Cobrar la saca y libera el cajón 4 |

Para ver un monto real, retrasa 7 horas la entrada en phpMyAdmin (base `estacionamiento`, pestaña SQL):

```sql
UPDATE detalle_servicios SET fecha_entrada = DATE_SUB(NOW(), INTERVAL 7 HOUR)
WHERE matricula = 'DEM1234' AND fecha_salida IS NULL;
```

La salida de `DEM1234` da **$200.00** (cliente de paso). Para comparar con un cliente frecuente, registra la entrada de `MNP2345` en el cajón `2`, retrásala igual (cambia la matrícula en la consulta) y registra su salida: da **$174.00**.

## 5. Pensiones (admin)

1. Registra la entrada de `DEM1234` en el cajón `3`. En Pensiones, escribe su matrícula: el cajón `3` aparece puesto y bloqueado, porque la pensión de un vehículo que está dentro va en su cajón actual.
2. Registra su salida. De vuelta en Pensiones, borra y vuelve a escribir `DEM1234`, cajón `10`, fecha de hoy, 1 mes → cuadro con **$1,200.00** → Cobrar.
3. Repite lo mismo: avisa que ya tiene una pensión en esas fechas.
4. Prueba con `XYZ9876` (Público general): la rechaza, porque es solo para clientes registrados.
5. Registra la entrada de `DEM1234`: el cajón `10` aparece puesto y bloqueado. Registra la salida: el cobro es **$0.00** por pensión vigente.
6. Registra la entrada de `XYZ9876` e intenta el cajón `10`: no está disponible, porque lo aparta la pensión.

## 6. Estacionamiento (croquis)

| Haz esto | Debe pasar |
|---|---|
| Abre el módulo Estacionamiento | 20 cajones en 4 filas de 5: 18 libres, el `5` rojo (`JKL4567`) y el `10` morado (`DEM1234`) |
| Pasa el cursor sobre el cajón `10` | Matrícula, cliente, fin de la pensión y "Vehículo fuera" |
| Sin cerrar el croquis, registra la entrada de `XYZ9876` en el cajón `1` y presiona "Actualizar" | El cajón `1` cambia a rojo con su matrícula |
| Registra su salida y presiona "Actualizar" | El cajón `1` vuelve a verde |

## 7. Reportes (admin)

Reportes abre en el año más reciente. Cambia entre 2025, 2026 y "Todos" y revisa las 4 pestañas: entradas y salidas por mes, meses con mayor demanda, horarios con mayor demanda e ingresos por servicio. Cada una trae su total al pie.

El total de ingresos de "Todos" debe coincidir con `SELECT SUM(monto_total) FROM cobros;`.

## 8. Perfil cobrador

Cierra sesión y entra como `cobrador` / `cobrador123`: el menú tiene 5 módulos y **no muestra** Usuarios, Pensiones ni Reportes. Sí puede abrir Estacionamiento.

## 9. Lo que hace la base por sí sola

- Un cliente registrado pasa a **frecuente** al llegar a 10 visitas en 30 días, y desde entonces paga $26.00 y $22.00 por hora.
- Un vehículo no puede tener dos entradas abiertas (trigger `tg_evitar_doble_entrada`).
- No se puede cobrar una estancia que no tiene salida (trigger `tg_validar_cobro_estancia`).
- No se puede asignar un cajón ocupado, apartado por una pensión o fuera del rango (triggers `tg_validar_cajon_*`).

## Si algo falla

- **"No se pudo conectar a MySQL":** MySQL no está encendido en XAMPP.
- **"A la base de datos le falta una parte":** vuelve a correr los scripts de `database/` en orden.
- **Error 400 en phpMyAdmin con Safari:** abre `http://127.0.0.1/phpmyadmin` en lugar de `localhost`.
