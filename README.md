```markdown
# Capturador de Servicios API & Comparador Regex 🌐🔍

Una herramienta de escritorio intuitiva desarrollada en **Python 3.13** utilizando **Tkinter** para la interfaz gráfica y **Playwright** para la interceptación y auditoría de tráfico de red en tiempo real. Diseñada específicamente para agilizar el análisis y mapeo de endpoints en flujos corporativos de QA y Desarrollo.

---

## ✨ Características Principales

* **Interceptación de Tráfico en Tiempo Real:** Captura peticiones (`requests`) y respuestas (`responses`) de red de forma transparente mediante una instancia automatizada de Chromium (Google Chrome).
* **Entrada Masiva de Plantillas:** Panel superior inteligente que acepta listas de URLs objetivo separadas por comas o saltos de línea, limpiando automáticamente comillas simples o dobles.
* **Procesamiento Dinámico por Regex:** Convierte estructuras dinámicas como `{shoppingCartId}` o `{Code}` en patrones de expresiones regulares (`\d+`) de forma automática y segura.
* **Interfaz de Doble Consola Oscura:** 1. **Consola Izquierda:** Historial completo de peticiones capturadas en bruto (JSON sin filtrar).
  2. **Consola Derecha:** Reporte JSON analítico estructurado en caliente con las coincidencias exactas.
* **Módulo de Resumen Integrado:** El reporte filtrado calcula e inyecta un bloque de conteo rápido (`resumen_conteos`) al inicio del archivo para auditorías veloces sin necesidad de scroll infinito.
* **Exportación Independiente:** Botones dedicados para copiar al portapapeles y guardar los archivos `capturas.json` y `reporte_plantillas.json` simultáneamente.

---

## 🛠️ Requisitos del Sistema

* **Python 3.13.x** o superior.
* **Google Chrome** instalado en el sistema (utilizado como canal nativo de ejecución).
* Compatibilidad completa con **Windows 10/11** y **macOS (Intel / Apple Silicon)**.

---

## 🚀 Instalación y Configuración (Entorno de Desarrollo)

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/KAISET/BrowserApiCapture.git](https://github.com/KAISET/BrowserApiCapture.git)
   cd BrowserApiCapture

```

2. **Crear y activar el entorno virtual (`venv`):**
* **En Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate

```

* **En macOS (Instalador Oficial de Python.org recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate

```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt

```

*(Nota: Si no tienes un archivo `requirements.txt`, instala directamente con `pip install playwright pyinstaller`)*
4. **Instalar los componentes de red de Playwright:**
```bash
playwright install chromium

```

---

## 💻 Uso de la Aplicación

El proyecto se encuentra modularizado con un script optimizado para cada sistema operativo con el fin de evitar configuraciones redundantes:

* **En Windows:**
```bash
python app_windows.py

```

* **En macOS (Bypass estricto de firmas SDK dinámicas):**
```bash
SYSTEM_VERSION_COMPAT=1 python3 app_macos.py

```

### Flujo de Trabajo Recomendado:

1. Define la **URL Inicial**, el **Nombre del Escenario** y el **Filtro URL API** de tu empresa en el panel superior y haz clic en *Aplicar Cambios*.
2. Pega tu listado de rutas a evaluar en el cuadro de texto superior.
3. Haz clic en **🌐 Abrir Navegador** para inicializar la instancia automatizada.
4. Interactúa con la página web; verás cómo las consolas procesan y estructuran la información en tiempo real.
5. Usa los botones de copiado o haz clic en **💾 Guardar ambos archivos JSON** para persistir tus reportes locales.

---

## 📦 Empaquetado para Producción (Distribución)

El proyecto está configurado para compilarse en binarios independientes utilizando **PyInstaller**. *(Nota: No se admite la compilación cruzada; debes compilar en Windows para obtener el `.exe` y en Mac para la estructura `.app`)*.

### Para Windows (`.exe` ejecutable autónomo):

Ejecuta en la terminal de Windows:

```bash
pyinstaller --noconfirm --onedir --windowed --copy-metadata playwright app_windows.py

```

El resultado se generará en `dist/app_windows/`. Comprime la carpeta **`app_windows`** en un archivo `.zip` para su distribución. El programa heredará de forma automática el Google Chrome instalado en la máquina destino de tus compañeros de trabajo.

### Para macOS (`.app` Nativo):

Ejecuta en la terminal de tu Mac:

```bash
pyinstaller --noconfirm --onedir --windowed --copy-metadata playwright app_macos.py

```

El resultado se generará en `dist/app.app`. Para ejecutar este bundle en otras Macs de la empresa sin bloqueos de cuarentena preventiva por falta de firma digital, el usuario destino debe ejecutar en su terminal:

```bash
xattr -cr /Ruta/A/Tu/Descarga/app.app

```

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT** - Consulta el archivo [LICENSE](https://www.google.com/search?q=LICENSE) para más detalles.

---

**Desarrollado con EL CORA Y GEMINI OFC, BC HAY QUE OPTIMIZAR 600 SERVICIOS, para la optimización de flujos de pruebas de software. :)**
**MUCHAS GRACIAS A GEMINI**
