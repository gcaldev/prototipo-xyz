# Prototipo Sistema Z

## Propuesta
El prototipo agrega validaciones para eliminar las debilidades detectadas relacionadas al control de accesos. Cada usuario únicamente tiene acceso a los expedientes en los que participa. 

Para lograr esto se identifica a la persona que esta operando (autenticación) por medio de la cookie de sesión y se valida que pueda acceder al expediente consultado (autorización).

Se divide el proyecto en 2 aplicaciones:
- **Servicio frontend:** servidor Flask que resuelve la interfaz que verá el cliente, asocia la cookie de sesión al momento de ingresar, la controla en cada llamado y propaga un contexto firmado al servidor interno.
- **Servicio backend:** servidor Flask que valida qué recurso es accesible por el usuario del contexto. A su vez, implementa el logging de auditoría ante cada operación ejecutada.

Adicionalmente, las contraseñas almacenadas quedan en Argon2id a diferencia del Aplicativo original donde se almacenaban en texto plano.
Queda fuera del prototipo la configuración de permisos de distintas tablas. La base de datos utilizada no tiene este tipo de configuración y es usada únicamente por simplicidad. Administración de participación por roles a definir junto a XY, no contemplado en el prototipo.

## Ejecución

Frente y servicio de expedientes, separados. El frente escucha en el puerto 5000 y el servicio en el 5001. No usa la maqueta de CentOS.

Hace falta Python 3. Desde esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Completar `.env` antes de seguir. `CONTEXTO_SECRETO` y `SESION_SECRETO` son dos cadenas largas, distintas, elegidas para esta demo. `SEMILLA_PEDRO_CLAVE` y `SEMILLA_VGOMEZ_CLAVE` son las claves de `pedro` y `vgomez` de la Figura 8 del informe técnico. Ese archivo no se versiona.

Cargar los datos y levantar los dos procesos, cada uno en su terminal, con el entorno virtual activado:

```powershell
python seed.py
```

```powershell
python -m service
```

```powershell
python -m frontend
```

Abrir `http://127.0.0.1:5000/SistemaZ/login`.

`pedro` puede buscar `EXP-13`. `vgomez`, con el mismo código, ve «Acceso denegado». Los cinco casos de la demo están en `guia.md`.

Para volver al estado inicial, detener los dos procesos y correr otra vez `python seed.py`.
