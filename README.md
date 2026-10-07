# Dashboard Mesa de Ayuda TI - Panel de Monitoreo ITSM

Aplicacion corporativa de Mesa de Ayuda y Gestion de Incidencias TI con navegacion analitica **Drill Down / Drill Up en 3 niveles**, monitoreo de cumplimiento de **SLA** con semaforizacion animada, tarjetas KPI estilo GLPI y autenticacion formal basada en roles.

---

## Requisitos y Puesta en Marcha

1. **Crear y activar el entorno virtual (si no existe):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```cmd
   pip install streamlit bcrypt plotly pandas
   ```

3. **Iniciar la aplicacion:**
   ```cmd
   streamlit run main.py
   ```
   *(Tambien compatible con `streamlit run app.py`)*

---

## Credenciales de Acceso

| Usuario   | Contrasena   | Rol           |
|:----------|:-------------|:--------------|
| `hamui`   | `hamui123`   | Administrador |
| `admin`   | `admin123`   | Administrador |
| `soporte` | `soporte123` | Tecnico       |
| `Mirko`   | `Mirko123`   | Tecnico       |

---

## Estructura Modular del Proyecto

- `database.py`: Gestion de conexion SQLite, migracion de esquema de `usuarios_sistema`, autenticacion con bcrypt y consultas SQL analiticas con `GROUP BY`, `COUNT`, `JOIN` y `CASE WHEN`.
- `app.py`: Interfaz formal en Streamlit con diseno ITSM/GLPI, tarjetas KPI, semaforo animado CSS, navegacion de 3 niveles y graficos corporativos con Plotly.
- `main.py`: Punto de entrada principal que ejecuta `app.py`.
- `Gestionar_usuarios.py`: Herramienta para registrar usuarios y actualizar contrasenas.
- `mesa_ayuda.db`: Base de datos SQLite.

---

## Navegacion Analitica en 3 Niveles (Drill Down / Drill Up)

- **Nivel 1: Departamentos**
  - Tarjetas KPI superiores (Total de Casos, En Proceso, Vencidos, Eficiencia SLA) en bloques solidos corporativos.
  - Bloque superior con referencia animada de semaforo de SLA.
  - Listado de departamentos con indicadores de estado y boton formal `Ver tecnicos` (Drill Down).
  - Grafico de barras agrupadas corporativo por departamento (Total, Abiertos y Cerrados) con data labels superiores (`textposition='outside'`) y grilla tenue punteada.
- **Nivel 2: Tecnicos por Departamento**
  - Boton formal de retorno `<- Volver a departamentos` y ruta de navegacion (breadcrumb).
  - Listado de tecnicos del departamento con volumen de tickets asignados, estado individual y boton `Ver tickets` (Drill Down).
  - Grafico de barras horizontales con el volumen de tickets por tecnico.
- **Nivel 3: Detalle de Tickets por Tecnico**
  - Boton formal de retorno `<- Volver a tecnicos` y ruta de navegacion (breadcrumb).
  - Detalle individual de cada ticket en tarjetas operativas o tabla interactiva: ID, Titulo, Solicitante (JOIN con `usuarios`), Prioridad, Estado, Fecha Apertura, Fecha Cierre, SLA Horas y Estado SLA calculado en tiempo real.
  - Grafico de dona corporativo con la distribucion de incidencias por prioridad.

---

## Referencia de Monitoreo SLA
- **Verde:** Dentro de SLA
- **Amarillo:** Por vencer (< 20% del tiempo restante)
- **Rojo:** Fuera de SLA / Vencido