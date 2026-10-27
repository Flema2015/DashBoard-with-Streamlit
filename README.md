# Dashboard Mesa de Ayuda TI — Panel de Monitoreo ITSM

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
   streamlit run app.py
   ```
   *(Tambien ejecutable con `streamlit run main.py` o `streamlit run proyecto_dashboard/app.py`)*

---

## Credenciales de Acceso

| Usuario      | Contrasena   | Rol           |
|:-------------|:-------------|:--------------|
| `hamui`      | `hamui123`   | Administrador |
| `admin`      | `admin123`   | Administrador |
| `supervisor` | `super123`   | Supervisor    |

---

## Estructura Modular del Proyecto

```text
proyecto_dashboard/
├── app.py                  # Punto de entrada, configuracion de pagina y router de sesion/vistas
├── config.py               # Constantes, paleta de colores corporativa (GLPI style) y rutas
├── database/
│   ├── __init__.py         # Exportacion de modulo
│   ├── connection.py       # Gestion de conexion a SQLite
│   ├── schema_seed.py      # Creacion de tablas e INSERTs iniciales (con contrasenas hasheadas)
│   └── queries.py          # Todas las consultas SQL puras (Login, KPIs y Niveles 1, 2 y 3)
├── components/
│   ├── __init__.py         # Exportacion de componentes
│   ├── styles.py           # Inyeccion de CSS (tarjetas GLPI, animaciones pulse del semaforo, limpieza UI)
│   ├── header_sidebar.py   # Cabecera y barra lateral con usuario, rol, filtros globales y logout
│   └── kpi_cards.py        # Renderizado de las tarjetas superiores y el bloque de referencia del semaforo
└── views/
    ├── __init__.py         # Exportacion de vistas
    ├── login_view.py       # Pantalla de inicio de sesion formal
    ├── nivel1_deptos.py    # Vista Nivel 1: Departamentos + Grafico comparativo (Totales/Abiertos/Cerrados)
    ├── nivel2_tecnicos.py  # Vista Nivel 2: Tecnicos del depto seleccionado + Drill Up/Down
    └── nivel3_tickets.py   # Vista Nivel 3: Detalle de tickets del tecnico + Grafico de prioridades
```

---

## Navegacion Analitica en 3 Niveles (Drill Down / Drill Up)

- **Nivel 1: Departamentos**
  - Tarjetas KPI superiores (Tickets Resueltos/En Tiempo, Abiertos/Asignados, Vencidos/Fuera de SLA, Total Tickets e Indice SLA) en bloques solidos corporativos.
  - Bloque superior con referencia animada de semaforo de SLA.
  - Listado estructurado de departamentos con indicadores de estado y boton formal `Ver tecnicos` (Drill Down).
  - Grafico de barras agrupadas corporativo por departamento (Total, Abiertos y Cerrados) con data labels superiores (`textposition='outside'`) y grilla tenue punteada.
- **Nivel 2: Tecnicos por Departamento**
  - Boton formal de retorno `<- Volver a departamentos` (Drill Up) y ruta de navegacion (breadcrumb).
  - Listado de tecnicos del departamento con volumen de tickets asignados, abiertos, cerrados, estado individual y boton `Ver tickets` (Drill Down).
  - Grafico de barras comparando la carga de tickets (Abiertos vs. Cerrados) por tecnico.
- **Nivel 3: Detalle de Tickets por Tecnico**
  - Boton formal de retorno `<- Volver a tecnicos` (Drill Up) y ruta de navegacion (breadcrumb).
  - Detalle individual de cada ticket en tarjetas operativas o tabla estilizada: ID Ticket, Titulo, Reportado por (Solicitante via JOIN con `usuarios`), Prioridad, Estado, Fecha Apertura, Fecha Cierre, SLA Horas y Estado SLA calculado en tiempo real.
  - Graficos corporativos de distribucion de incidencias segun su Prioridad (dona) y segun su Estado (barras).

---

## Referencia de Monitoreo SLA
- **Verde:** Dentro de SLA (Situacion normal / favorable)
- **Amarillo:** Por vencer — menos del 20% del tiempo de SLA restante (Advertencia)
- **Rojo:** Vencido / Fuera de SLA (Situacion critica)
