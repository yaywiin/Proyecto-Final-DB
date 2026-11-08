# Guía de inicio

Los comandos para trabajar en el proyecto, de la primera vez al pull request. Las reglas del equipo están en [WoW.md](WoW.md).

## 1. Primera vez

### 1.1 Clonar el repo

```bash
git clone https://github.com/yaywiin/Proyecto-Final-DB.git
cd Proyecto-Final-DB
```

### 1.2 Configurar tu usuario de Git (solo en este repo)

```bash
git config user.name "tu-usuario-de-github"
git config user.email "tu-correo"
```

Verifica con `git config user.name`.

### 1.3 Instalar las dependencias de Python

```bash
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1.4 Encender la base de datos

Abre XAMPP y presiona **Start** en MySQL. Si no enciende, revisa que otro programa no esté usando el puerto 3306.

### 1.5 Configurar la conexión

```bash
cp app/config.example.py app/config.py
```

Abre `app/config.py` y pon tus datos locales (en XAMPP el usuario suele ser `root` sin contraseña). **Ese archivo no se sube a Git.**

### 1.6 Crear la base de datos local

Los scripts de `database/` van numerados y se corren en orden:

```bash
for f in database/*.sql; do /Applications/XAMPP/xamppfiles/bin/mysql -u root < "$f"; done
```

En Windows, usa el `mysql.exe` que está en la carpeta `mysql\bin` de XAMPP, o abre phpMyAdmin e importa cada archivo en orden.

### 1.7 Probar la conexión

```bash
python -m app.main
```

Debe imprimir `✓ Conexión exitosa`. Si falla, el mensaje te dice qué hacer (encender MySQL, crear la base o revisar `app/config.py`).

## Cómo usar la base desde el código

Solo `app/modelo/` habla con la base, y lo hace con las funciones de `app/modelo/conexion.py`:

```python
from app.modelo.conexion import consultar, insertar, ejecutar, transaccion

filas = consultar("SELECT * FROM clientes WHERE id_cliente = %s", (1,))   # lista de diccionarios
nuevo_id = insertar("INSERT INTO clientes (nombre) VALUES (%s)", ("Ana",))  # id generado
afectadas = ejecutar("UPDATE clientes SET telefono = %s WHERE id_cliente = %s", ("5551234567", 2))

# varias sentencias que se guardan todas o ninguna
with transaccion() as cur:
    cur.execute("UPDATE servicios SET fecha_salida = NOW() WHERE id_servicio = %s", (5,))
    cur.execute("INSERT INTO cobros (id_servicio, id_usuario, monto) VALUES (%s, %s, %s)", (5, 1, 90))
```

Los valores siempre van como parámetros (`%s`), nunca pegados al texto del SQL.

## 2. Cambios en la base: no hay migraciones

No usamos herramientas de migraciones. La base se vuelve a crear desde cero cada vez:

- Los scripts empiezan con `DROP DATABASE IF EXISTS ...` y `CREATE DATABASE ...`, así que correrlos de nuevo reinicia todo.
- Si alguien cambia una tabla, **edita el script** (por ejemplo `01_tablas.sql`) en lugar de escribir un `ALTER`. Avisa en el chat y los demás vuelven a correr el comando de 1.6.
- El CI hace lo mismo en cada pull request, así que si tu script falla desde cero, el PR sale en rojo.

## 3. Trabajar en una tarea

Cada issue se trabaja en su propia rama. Nunca se trabaja en `main`.

### 3.1 Traer `main` actualizado y crear tu rama

```bash
git checkout main
git pull
git checkout -b nombre/tema        # ejemplo: cristobal/login
```

### 3.2 Guardar tus cambios

```bash
git status                         # qué cambió
git add archivo1 archivo2          # agrega solo lo que tocaste
git commit -m "agrega ventana de login"
```

Evita `git add .` si no revisaste antes con `git status`: puedes subir archivos que no querías.

### 3.3 Subir tu rama

```bash
git push -u origin nombre/tema
```

(`-u` solo la primera vez. Después basta con `git push`.)

## 4. Abrir el pull request

Con la terminal:

```bash
gh pr create --title "Login con perfiles" --body "Cierra #12. Valida usuario y contraseña. Se prueba con el admin de los datos semilla."
```

O desde GitHub: aparece un botón verde **Compare & pull request** al subir la rama.

En la descripción:
- `Cierra #número` del issue, para que se cierre solo al unirse.
- Dos líneas con qué hiciste y cómo probarlo.

Después, pide la revisión a quien te toca según la tabla de [WoW.md](WoW.md) y avisa en el chat.

## 5. Revisar el PR de otra persona

```bash
gh pr checkout 15                  # baja la rama del PR #15 para probarla
```

Pruébala, y en GitHub deja comentarios o aprueba. Si todo está bien, haz el merge.

## 6. Si `main` cambió mientras trabajabas

```bash
git checkout main
git pull
git checkout nombre/tema
git merge main
```

Si no hay conflictos, listo. Sube los cambios con `git push`.

### Conflictos

Si Git dice `CONFLICT`, abre los archivos marcados. Verás algo así:

```
<<<<<<< HEAD
tu versión
=======
la versión de main
>>>>>>> main
```

Deja la versión correcta (o combina las dos), borra las tres líneas de marcas, y luego:

```bash
git add archivo-con-conflicto
git commit
```

Si no estás seguro de cuál versión conservar, pregunta a la persona dueña del archivo antes de decidir.

## 7. Errores comunes

| Problema | Qué hacer |
|---|---|
| Hice cambios estando en `main` | No hagas commit. Corre `git checkout -b nombre/tema` y tus cambios se van contigo a la rama nueva. |
| Ya hice commit en `main` pero no he subido | `git branch nombre/tema`, luego `git reset --hard origin/main` y `git checkout nombre/tema`. Avisa antes si dudas. |
| Subí un archivo que no debía (contraseña, `config.py`) | Avisa en el chat de inmediato. Hay que cambiar la contraseña y quitarlo del repo. |
| `git push` me pide contraseña | Inicia sesión con `gh auth login`, o configura una llave SSH. |
| El CI me salió en rojo | Entra al PR, abre la pestaña **Checks** y mira qué paso falló. Casi siempre es un error en el SQL o de sintaxis en Python. |
| No puedo conectarme a la base | Revisa que MySQL esté encendido en XAMPP y que `config.py` tenga tus datos. |
| `git pull` dice que tengo cambios sin guardar | Haz commit de tus cambios, o guárdalos con `git stash` y recupéralos después con `git stash pop`. |

## 8. Resumen

```
git checkout main && git pull
git checkout -b nombre/tema
  ... trabajas ...
git add archivos && git commit -m "mensaje"
git push -u origin nombre/tema
gh pr create
  ... te revisan ...
merge → el issue se cierra solo
```
