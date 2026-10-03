# IntelliKonta 💼📈

**IntelliKonta** es un sistema de escritorio para gestión financiera integral, control de ingresos, gastos, conciliación de cuentas, directorio de contactos y emisión de reportes contables listos para imprimir.

Desarrollado en **Python 3**, interfaz moderna en **CustomTkinter** con estética **Glassmorphism**, base de datos embebida **SQLite** y generación de documentos PDF con **fpdf2**.

---

## ✨ Características Principales

### 🎨 Diseño Glassmorphism en Tonos de Azul Suave
- **Barra de navegación superior (Navbar)**:
  - Fondo oscuro permanente (`#070a13`) con indicador activo en azul vibrante (`#2563eb`).
  - Botones con auto-ajuste de ancho compacto (`width=0`) para garantizar la visibilidad total de los 8 módulos del sistema.
  - Distintivo de sesión con avatar e identificación del usuario activo.
- **Área de contenido inferior**:
  - Paleta en **tonos de azul bajo** (`#ebf2fc`) que reduce la fatiga visual.
  - Paneles, tarjetas y modales con efecto de cristal esmerilado blanco (`#ffffff`), sombras y bordes sutiles en `#cde0f5`.
- **Estandarización de botones de acción con iconos y colores corporativos**:
  - 👁️ **Detalle (Azul Info `#2563eb`)**: Abre una ventana modal esmerilada con resumen y datos completos.
  - ✏️ **Editar (Amarillo/Ámbar Warning `#f59e0b`)**: Abre el diálogo de edición del elemento seleccionado.
  - 🗑️ **Eliminar (Rojo Danger `#ef4444`)**: Solicita confirmación y valida restricciones de integridad referencial.

---

## 📦 Módulos del Sistema

1. **Dashboard (Panel Principal)**
   - Resumen ejecutivo con tarjetas métricas (KPIs): Total en Cuentas, Ingresos del Período, Gastos del Período y Balance Neto.
   - Acceso directo para registrar ingresos o gastos inmediatos.
   - Tabla con los movimientos más recientes y panel de cuentas activas con su saldo disponible.

2. **Ingresos**
   - Registro de entradas, ventas y cobranzas.
   - Filtros dinámicos por cuenta receptora, categoría contable y campo de búsqueda en vivo.
   - Consulta de detalle (`👁️`), edición (`✏️`) y eliminación (`🗑️`).

3. **Gastos**
   - Control de egresos, compras, pagos a proveedores, servicios e impuestos.
   - Totales calculados en tiempo real según los filtros aplicados.
   - Acciones completas de detalle, modificación y borrado.

4. **Cuentas Financieras**
   - Gestión de cuentas de cheques, ahorro y cajas de efectivo.
   - Saldo inicial configurable y saldo actual calculado automáticamente a partir de todas las transacciones.
   - **Modal de Resumen de Cuenta (`👁️`)**: Visualización de saldo de apertura, total acumulado de ingresos recibidos, total de gastos desembolsados, saldo actual disponible y conteo de movimientos vinculados.

5. **Contactos (Clientes y Proveedores)**
   - Directorio con teléfono, correo electrónico, empresa y dirección.
   - **Modal de Ficha de Contacto (`👁️`)**: Consulta consolidada con historial de movimientos, total facturado/cobrado, total pagado y saldo comercial neto.

6. **Categorías y Métodos de Pago**
   - Clasificación de conceptos para ingresos y gastos.
   - Catálogo de medios de pago (Efectivo, Transferencia SPEI, Tarjeta de Débito/Crédito, etc.).
   - Botones estandarizados en advertencia (amarillo) y peligro (rojo).

7. **Reportes Profesionales (FPDF2)**
   - Generación de estados de cuenta filtrables por rango de fechas (mes actual, mes anterior, año en curso, o personalizado), cuenta y tipo de operación.
   - Previsualización métrica con total de ingresos, gastos y balance neto.
   - Exportación a PDF con formato ejecutivo, tipografía limpia, filas alternadas, paginado y apertura inmediata para impresión.

8. **Usuarios y Permisos**
   - Administración de usuarios del sistema con roles (Administrador / Operador).
   - Control de estado (Activo / Inactivo) y validaciones de seguridad (evita eliminar al usuario en sesión o dejar el sistema sin administradores).
   - **Modal de Detalle de Usuario (`👁️`)**: Información de perfil, correo, rol y fecha de alta.

---

## 📁 Arquitectura del Código

```
intellikonta/
├── database/
│   ├── __init__.py
│   └── db.py               # Conexión SQLite, esquema relacional, migraciones y seed inicial
├── models/
│   ├── __init__.py
│   ├── account.py          # Modelo de cuentas, cálculo y resumen de saldos
│   ├── category.py         # Categorías y métodos de pago
│   ├── contact.py          # Clientes y proveedores con resumen histórico
│   ├── operation.py        # Ingresos y gastos con filtros avanzados
│   └── user.py             # Usuarios, roles y autenticación
├── components/
│   ├── __init__.py
│   ├── navbar.py           # Menú superior oscuro, botones compactos e indicador activo
│   ├── stat_card.py        # Tarjetas métricas KPI con estética glassmorphic
│   └── modals.py           # Modales para operaciones, cuentas, contactos y DetailModal
├── views/
│   ├── __init__.py
│   ├── dashboard_view.py   # Vista principal con KPIs y accesos directos
│   ├── operations_view.py  # Vista reutilizable para Ingresos y Gastos
│   ├── accounts_view.py    # Listado y saldos de cuentas bancarias
│   ├── contacts_view.py    # Directorio de clientes y proveedores
│   ├── categories_view.py  # Pestañas de categorías y métodos de pago
│   ├── reports_view.py     # Filtros y emisor de reportes PDF
│   └── users_view.py       # Control de usuarios del sistema
├── reports/
│   ├── __init__.py
│   └── pdf_generator.py    # Generador de reportes en PDF con fpdf2
├── utils/
│   ├── __init__.py
│   ├── helpers.py          # Formateo de moneda ($ 0.00), fechas y validaciones
│   └── session.py          # Manejo de la sesión de usuario activa
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias de Python
├── schema.sql              # Esquema SQL de referencia
└── README.md               # Documentación general
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Prerrequisitos
- **Python 3.10** o versión superior instalada en el sistema.

### 2. Instalación de dependencias
Clona o descarga el repositorio y ejecuta en la terminal:
```bash
pip install -r requirements.txt
```

*Dependencias utilizadas:*
- `customtkinter>=5.2.0`
- `fpdf2>=2.7.0`

### 3. Ejecución
Inicia la aplicación con el siguiente comando:
```bash
python main.py
```

> **Nota:** En la primera ejecución se creará automáticamente el archivo `intellikonta.db` en SQLite con la estructura de tablas y un conjunto de datos iniciales de prueba (cuentas bancarias, categorías comunes, métodos de pago, usuarios y transacciones de muestra).

### 4. Credenciales por Defecto para Iniciar Sesión
- **Usuario:** `admin`
- **Contraseña:** `admin`
- **Nombre:** Administrador Principal
- **Rol:** `admin`

> Al iniciar la aplicación se mostrará la pantalla de **Inicio de Sesión**. Tras autenticarte, podrás cerrar la sesión en cualquier momento mediante el botón **"Salir 🚪"** ubicado en el extremo derecho de la barra de navegación superior.

---

## 🛠️ Compilación a Ejecutable (.exe) para Windows

Puedes empaquetar **IntelliKonta** como una aplicación de escritorio nativa para Windows (`.exe`) utilizando **PyInstaller**.

### 1. Instalar PyInstaller
En la misma consola o entorno virtual de Python:
```bash
pip install pyinstaller
```

### 2. Generar el archivo ejecutable

#### Opción A: Ejecutable en un solo archivo independiente (Recomendado)
Genera un único archivo ejecutable portátil listo para distribuir:
```bash
pyinstaller --noconsole --onefile --name "IntelliKonta" --collect-all customtkinter main.py
```

#### Opción B: Ejecutable en carpeta distribuible (Arranque ultra rápido)
Genera una carpeta con el ejecutable y sus bibliotecas ya extraídas:
```bash
pyinstaller --noconsole --name "IntelliKonta" --collect-all customtkinter main.py
```

### 3. Explicación de parámetros clave
- `--noconsole` (o `--windowed`): Oculta la ventana de terminal negra de fondo, mostrando únicamente la interfaz gráfica.
- `--collect-all customtkinter`: **Indispensable** para que PyInstaller empaquete los archivos JSON de temas, paletas de colores y fuentes de CustomTkinter.
- `--onefile`: Comprime todas las dependencias y código en un único binario ejecutable.
- `--name "IntelliKonta"`: Define el nombre del archivo final (`IntelliKonta.exe`).
- `--icon="ruta/al/icono.ico"` *(opcional)*: Permite asignar un icono personalizado al archivo `.exe`.

### 4. Ubicación del binario final
Al finalizar la compilación, encontrarás tu archivo ejecutable listo para usar dentro de la carpeta:
```
dist/
└── IntelliKonta.exe
```

> **Nota sobre la base de datos:** Al ejecutarse, `IntelliKonta.exe` buscará o creará automáticamente la base de datos local `intellikonta.db` en el mismo directorio de ejecución, manteniendo todos los datos guardados de forma persistente.

---

## 🄯 Copyleft

Este proyecto está liberado bajo términos de **Copyleft** por **AgusBot** — [agusbot.com](https://agusbot.com).

*Eres libre de usar, estudiar, modificar y compartir esta aplicación manteniendo las mismas libertades para la comunidad.*
