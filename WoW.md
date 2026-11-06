# Cómo vamos a trabajar (Ways of Working)

Reglas cortas para que los tres avancemos sin estorbarnos. Si algo no funciona, lo cambiamos entre todos.

## Principios

1. `main` siempre debe funcionar. Si alguien lo clona, debe poder correr.
2. Cada quien es dueño de sus archivos. No se edita el archivo de otro sin avisar.
3. Lo que no está en un issue no existe. Si hay trabajo nuevo, se crea el issue.
4. Pedir ayuda pronto es mejor que atorarse solo.

## Organización

- **Milestones:** uno por entrega (9, 13, 20 y 23 de noviembre).
- **Issues:** una tarea concreta con responsable y milestone. Describen la meta y cuándo está listo, no cómo se hace.
- **Estados:** abierto → en progreso (quien lo toma se lo asigna) → cerrado cuando se une a `main`.
- Nadie toma un issue de otra persona sin hablarlo antes.

## Dueño de cada parte

| Persona | Es dueño de |
|---|---|
| Carlos | `sql/` y el diagrama ER |
| Cristobal | Login, menú, usuarios, clientes, vehículos y permisos |
| Yael | `main.py`, `config`, conexión, entradas y salidas, cobros, pensiones y reportes |

Si necesitas algo en un archivo ajeno, abre un issue para el dueño o pídelo por el chat. No lo edites directo.

## Git

- **Ramas:** una por issue, con el formato `nombre/tema`, por ejemplo `cristobal/login`.
- **Nadie sube directo a `main`.** Todo entra por pull request.
- **Pull requests:**
  - Se abren cuando el issue está listo para revisarse, y mencionan el issue (`Cierra #12`).
  - Los revisa otra persona. Si no hay problemas, la misma persona que revisó hace el merge.
  - Se espera la revisión máximo 24 horas. Si pasa más, se avisa por el chat.
- **Antes de abrir un PR:** traer los últimos cambios de `main` a tu rama y probar que tu código corre.
- **Commits:** en español, cortos y en presente (`agrega tabla Pensiones`).
- **Archivos que no se suben:** contraseñas, `config.py` local y carpetas de entorno. Se sube un `config.example.py` para copiar.

## Cómo se hace una revisión

1. Terminas tu issue en tu rama y la subes.
2. Abres un pull request hacia `main`. En la descripción: `Cierra #12` y dos líneas con qué hiciste y cómo probarlo.
3. Pides la revisión a quien le toca (tabla de abajo) y avisas en el chat.
4. El revisor lee los cambios y los prueba:
   - Si está bien, aprueba y hace el merge.
   - Si hay algo que arreglar, deja comentarios en las líneas. El autor corrige en la misma rama y el PR se actualiza solo.
5. Con el merge, el issue se cierra solo.

**Quién revisa a quién** (revisa quien usa lo que se hizo):

| Autor | Lo revisa |
|---|---|
| Carlos (SQL) | Yael |
| Cristobal (login y catálogos) | Carlos |
| Yael (operación) | Cristobal |

**Qué se revisa** (no hace falta una revisión profunda):

- ¿Cumple lo que dice "Listo cuando" del issue?
- ¿Corre sin errores con los datos semilla?
- ¿Respeta los nombres del modelo de datos?
- ¿Tocó archivos que no son del autor?
- ¿Hay contraseñas o datos personales en el código?

Lo demás, como el estilo o los nombres de variables, se deja pasar.

Nadie aprueba su propio PR. Si una revisión pasa de 24 horas, el autor escribe en el chat. Los PR que sigan abiertos se revisan en la llamada corta.

## Contratos entre partes

Para no esperarnos, programamos contra nombres acordados (tablas, columnas, funciones y vistas), que están en `Modelo_Datos.md`.

- Si alguien necesita cambiar un nombre o una firma, lo avisa por el chat **antes** de cambiarlo, y se actualiza `Modelo_Datos.md`.
- Cada quien prueba con su base local y los datos semilla de `sql/`.

## Comunicación

- **Chat del equipo:** para dudas rápidas, avisos y bloqueos.
- **Issues:** para lo que debe quedar registrado (tareas, bugs, cambios al contrato).
- **Avisar al terminar:** al cerrar un issue, escribir en el chat para que se pueda probar.
- **Revisión de los jueves o la víspera de cada entrega:** una llamada corta para ver qué falta y qué se recorta.

## Definición de "listo"

Un issue se cierra cuando:
- Cumple lo que dice "Listo cuando" del issue.
- Se probó con los datos semilla.
- Otra persona lo revisó y se unió a `main`.
- Si cambió algo del modelo o del contrato, `Modelo_Datos.md` está actualizado.

## Si algo se atrasa

1. Se avisa en cuanto se detecta, sin esperar al día de la entrega.
2. Se pide ayuda o se mueve el issue a otro hito, hablándolo entre todos.
3. Los extras (gráficas, puntos y procedimientos) son lo primero que se recorta.
4. Un sistema que funciona completo vale más que uno con extras a medias.

## Calendario

| Entrega | Fecha |
|---|---|
| Avance 1 | 9 de noviembre |
| Avance 2 | 13 de noviembre |
| Avance 3 | 20 de noviembre |
| Entrega final | 23 de noviembre |
