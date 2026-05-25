import os
# Bypass crítico para prevenir crashes gráficos por discrepancias de SDK en macOS
os.environ["MACOSX_DEPLOYMENT_TARGET"] = "14.0"

import json
import threading
import sys
import re
import tkinter as tk
from tkinter import ttk, messagebox
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN GLOBAL ---
capturas = []
escenario_config = {
    "nombre": "Enrolamiento USA - PC", 
    "filtro_api": "https://api.aseastage.com/api/v2.0/",
    "url_inicial": "https://shop.aseastage.com"
}
playwright_instancia = None
browser = None
page = None


def plantilla_a_regex(plantilla):
    """Convierte formatos como {id} en patrones regex de forma segura en Python 3.13."""
    patron = re.sub(r"\{[^}]+\}", lambda m: r"\d+", plantilla)
    return patron


def es_api_valida(url_peticion):
    """Verifica si la petición pertenece a la API definida."""
    return escenario_config["filtro_api"] in url_peticion


def obtener_ruta_dinamica(url_pagina):
    """Extrae la sección limpia de la pestaña del navegador."""
    try:
        parsed_url = urlparse(url_pagina)
        ruta = parsed_url.path.strip("/")
        if not ruta:
            return "home"
        return ruta.replace("/", "-")
    except Exception:
        return "desconocido"


def obtener_etiqueta_escenario(url_pagina):
    """Une tu escenario manual con la subpágina detectada en tiempo real."""
    url_limpia = obtener_ruta_dinamica(url_pagina)
    return f"{escenario_config['nombre']} -> {url_limpia}"


def agregar_captura_a_interfaz(item):
    """Agrega la captura al cuadro izquierdo y actualiza el análisis por regex al vuelo."""
    capturas.append(item)
    
    # 1. Insertar en consola de capturas crudas (Izquierda)
    texto_json = json.dumps(item, indent=4, ensure_ascii=False)
    txt_json_crudo.insert(tk.END, texto_json + ",\n")
    txt_json_crudo.see(tk.END)
    
    # 2. Ejecutar análisis comparativo automático con las plantillas actuales
    procesar_analisis_regex()


def procesar_analisis_regex():
    """Lee el cuadro de texto superior, procesa las expresiones regulares y añade el resumen al inicio."""
    contenido_input = txt_plantillas.get("1.0", tk.END).strip()
    
    # Separar plantillas ingresadas por comas o saltos de línea
    plantillas_sucias = re.split(r',\s*', contenido_input)
    plantillas_objetivo = []
    for p in plantillas_sucias:
        p_limpia = p.strip().strip('"').strip("'").strip(",")
        if p_limpia:
            plantillas_objetivo.append(p_limpia)

    if not plantillas_objetivo or not capturas:
        txt_json_filtrado.delete("1.0", tk.END)
        return

    # Estructura temporal para acumular coincidencias
    reporte = {p: [] for p in plantillas_objetivo}
    
    # Analizar el historial acumulado en memoria
    for idx, item in enumerate(capturas):
        url_real = item.get("url", "")
        ruta_limpia = urlparse(url_real).path
        
        for plantilla in plantillas_objetivo:
            patron = plantilla_a_regex(plantilla)
            if re.search(patron, ruta_limpia):
                reporte[plantilla].append({
                    "posicion_original": idx,
                    "escenario": item.get("escenario"),
                    "metodo": item.get("metodo"),
                    "url_pagina": item.get("url_pagina"),
                    "url_api": url_real
                })
                break

    # Filtro estricto: Eliminar las que se quedaron vacías []
    reporte_limpio = {plantilla: datos for plantilla, datos in reporte.items() if len(datos) > 0}

    # 🌟 NUEVA FUNCIONALIDAD: Construir el bloque de resumen al inicio
    resumen_conteos = {}
    for plantilla, items in reporte_limpio.items():
        total_llamadas = len(items)
        resumen_conteos[plantilla] = f"llamadas {total_llamadas}"

    # Estructurar el objeto final combinado
    json_final_combinado = {
        "resumen_conteos": resumen_conteos,      # 👈 Aparece arriba de todo
        "detalle_peticiones": reporte_limpio     # 👈 Desglose uno por uno abajo
    }

    # Renderizar el JSON resultante en el cuadro derecho (Consola Verde)
    txt_json_filtrado.delete("1.0", tk.END)
    txt_json_filtrado.insert("1.0", json.dumps(json_final_combinado, indent=4, ensure_ascii=False))


# --- LISTENERS DE RED (PLAYWRIGHT) ---
def manejar_request(request):
    if not es_api_valida(request.url):
        return
    try:
        url_de_la_pagina = request.frame.page.url
        item = {
            "escenario": obtener_etiqueta_escenario(url_de_la_pagina),
            "tipo": "request",
            "url_pagina": url_de_la_pagina,
            "url": request.url,
            "metodo": request.method,
            "headers": dict(request.headers),
            "body": request.post_data
        }
        root.after(0, agregar_captura_a_interfaz, item)
    except Exception:
        pass


def manejar_response(response):
    if not es_api_valida(response.url):
        return
    try:
        url_de_la_pagina = response.frame.page.url
        try:
            body = response.text()
        except Exception:
            body = "[No accesible o binario]"

        item = {
            "escenario": obtener_etiqueta_escenario(url_de_la_pagina),
            "tipo": "response",
            "url_pagina": url_de_la_pagina,
            "url": response.url,
            "status": response.status,
            "body": body
        }
        root.after(0, agregar_captura_a_interfaz, item)
    except Exception:
        pass


# --- CONTROLADOR DEL NAVEGADOR ---
def bucle_playwright():
    global playwright_instancia, browser, page
    try:
        playwright_instancia = sync_playwright().start()
        browser = playwright_instancia.chromium.launch(headless=False, channel="chrome")
        page = browser.new_page()

        page.on("request", manejar_request)
        page.on("response", manejar_response)

        url_destino = escenario_config["url_inicial"]
        page.goto(url_destino)
        
        while browser.is_connected():
            page.wait_for_timeout(500)
            
    except Exception as e:
        print(f"Playwright cerrado o con error: {e}")
    finally:
        btn_iniciar.config(state=tk.NORMAL)
        btn_detener.config(state=tk.DISABLED)


# --- ACCIONES DE LA INTERFAZ GRÁFICA ---
def iniciar_navegador():
    actualizar_escenario()
    btn_iniciar.config(state=tk.DISABLED)
    btn_detener.config(state=tk.NORMAL)
    threading.Thread(target=bucle_playwright, daemon=True).start()


def detener_navegador():
    global browser, playwright_instancia
    if browser:
        browser.close()
    if playwright_instancia:
        playwright_instancia.stop()
    btn_iniciar.config(state=tk.NORMAL)
    btn_detener.config(state=tk.DISABLED)
    messagebox.showinfo("Navegador", "Navegador cerrado correctamente.")


def actualizar_escenario():
    escenario_config["nombre"] = entry_nombre.get()
    escenario_config["filtro_api"] = entry_filtro.get()
    escenario_config["url_inicial"] = entry_url.get()
    lbl_status.config(text=f"Activo: {escenario_config['nombre']} | Filtrando: {escenario_config['filtro_api']}")
    procesar_analisis_regex()


def copiar_crudo():
    root.clipboard_clear()
    contenido = txt_json_crudo.get("1.0", tk.END).strip().rstrip(",")
    contenido_final = f"[\n{contenido}\n]" if contenido else "[]"
    root.clipboard_append(contenido_final)
    messagebox.showinfo("Copiado", "¡JSON Completo en bruto copiado!")


def copiar_filtrado():
    root.clipboard_clear()
    contenido = txt_json_filtrado.get("1.0", tk.END).strip()
    root.clipboard_append(contenido if contenido else "{}")
    messagebox.showinfo("Copiado", "¡JSON Filtrado con Resumen copiado!")


def guardar_ambos_archivos():
    if not capturas:
        messagebox.showwarning("Guardar", "No hay capturas disponibles.")
        return
    
    # Guardar archivo bruto sin filtros
    with open("capturas.json", "w", encoding="utf-8") as f:
        json.dump(capturas, f, indent=4, ensure_ascii=False)
        
    # Guardar reporte analítico con el resumen incluido
    contenido_filtrado = txt_json_filtrado.get("1.0", tk.END).strip()
    if contenido_filtrado:
        try:
            objeto_json_filtrado = json.loads(contenido_filtrado)
            with open("reporte_plantillas.json", "w", encoding="utf-8") as f:
                json.dump(objeto_json_filtrado, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar reporte filtrado: {e}")
            
    messagebox.showinfo("Guardado", "¡Ambos archivos exportados! Resumen incluido en 'reporte_plantillas.json'")


# --- DISEÑO DE LA INTERFAZ DE USUARIO (TKINTER) ---
root = tk.Tk()
root.title("Capturador de Servicios API & Comparador Regex Avanzado")
root.geometry("1250x850")

# Panel Superior 1: Configuración Estándar
frame_config = ttk.LabelFrame(root, text=" Configuración de Navegación y Escenario ", padding=10)
frame_config.pack(fill="x", padx=15, pady=5)

ttk.Label(frame_config, text="URL Inicial Página:").grid(row=0, column=0, sticky="w", pady=2)
entry_url = ttk.Entry(frame_config, width=50)
entry_url.insert(0, escenario_config["url_inicial"])
entry_url.grid(row=0, column=1, columnspan=3, padx=5, pady=2, sticky="ew")

ttk.Label(frame_config, text="Nombre Escenario:").grid(row=1, column=0, sticky="w", pady=2)
entry_nombre = ttk.Entry(frame_config, width=25)
entry_nombre.insert(0, escenario_config["nombre"])
entry_nombre.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

ttk.Label(frame_config, text="Filtro URL API:").grid(row=1, column=2, sticky="w", pady=2)
entry_filtro = ttk.Entry(frame_config, width=35)
entry_filtro.insert(0, escenario_config["filtro_api"])
entry_filtro.grid(row=1, column=3, padx=5, pady=2, sticky="ew")

btn_aplicar = ttk.Button(frame_config, text="Aplicar Cambios", command=actualizar_escenario)
btn_aplicar.grid(row=0, column=4, rowspan=2, padx=10, pady=2, sticky="ns")

frame_config.columnconfigure(1, weight=1)
frame_config.columnconfigure(3, weight=2)

# Panel Superior 2: Entrada masiva de Plantillas Objetivo
frame_input_plantillas = ttk.LabelFrame(root, text=" Lista de Plantillas URLs Objetivo (Separadas por comas, admite comillas) ", padding=10)
frame_input_plantillas.pack(fill="x", padx=15, pady=5)

txt_plantillas = tk.Text(frame_input_plantillas, height=5, font=("Courier New", 10))
txt_plantillas.pack(fill="x", side="left", expand=True, padx=5)

valores_default = '"Shipping/Calculate",\n"Promotion/Validate/{Code}",\n"Product/PriceList",\n"Ecommerce/ShoppingCart/{shoppingCartId}/RecommendedProducts/{productId}",\n"Ecommerce/ShoppingCart/SaveAutoship",\n"Ecommerce/ShoppingCart/SaveOrder",\n"Ecommerce/ShoppingCart/{shoppingCartId}/Product"'
txt_plantillas.insert("1.0", valores_default)

scroll_p = ttk.Scrollbar(frame_input_plantillas, orient="vertical", command=txt_plantillas.yview)
txt_plantillas.configure(yscrollcommand=scroll_p.set)
scroll_p.pack(side="right", fill="y")

# Panel de Botones de Control
frame_acciones = ttk.Frame(root, padding=5)
frame_acciones.pack(fill="x", padx=15)

btn_iniciar = ttk.Button(frame_acciones, text="🌐 Abrir Navegador", command=iniciar_navegador)
btn_iniciar.pack(side="left", padx=5)

btn_detener = ttk.Button(frame_acciones, text="🛑 Cerrar Navegador", command=detener_navegador, state=tk.DISABLED)
btn_detener.pack(side="left", padx=5)

btn_manual_run = ttk.Button(frame_acciones, text="🔄 Forzar Re-Filtrado Regex", command=procesar_analisis_regex)
btn_manual_run.pack(side="left", padx=15)

btn_guardar = ttk.Button(frame_acciones, text="💾 Guardar Ambos JSON", command=guardar_ambos_archivos)
btn_guardar.pack(side="right", padx=5)

lbl_status = ttk.Label(root, text="Navegador inactivo", font=("Arial", 10, "italic"), foreground="gray")
lbl_status.pack(anchor="w", padx=20, pady=2)

# --- SECCIÓN CENTRAL - LAS DOS CONSOLAS EN PARALELO ---
frame_consolas = ttk.Frame(root, padding=5)
frame_consolas.pack(fill="both", expand=True, padx=15, pady=5)

# Columna Izquierda: JSON en Bruto
col_izquierda = ttk.LabelFrame(frame_consolas, text=" 1. Historial JSON en Bruto (Sin Filtrar) ", padding=5)
col_izquierda.pack(side="left", fill="both", expand=True, padx=5)

btn_copiar_crudo = ttk.Button(col_izquierda, text="📋 Copiar JSON Bruto", command=copiar_crudo)
btn_copiar_crudo.pack(anchor="e", pady=2)

txt_json_crudo = tk.Text(col_izquierda, wrap="none", font=("Courier New", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
scroll_y_c = ttk.Scrollbar(col_izquierda, orient="vertical", command=txt_json_crudo.yview)
scroll_x_c = ttk.Scrollbar(col_izquierda, orient="horizontal", command=txt_json_crudo.xview)
txt_json_crudo.configure(yscrollcommand=scroll_y_c.set, xscrollcommand=scroll_x_c.set)
scroll_y_c.pack(side="right", fill="y")
txt_json_crudo.pack(fill="both", expand=True)
scroll_x_c.pack(fill="x")

# Columna Derecha: JSON Filtrado Comparativo (Con Resumen)
col_derecha = ttk.LabelFrame(frame_consolas, text=" 2. Reporte JSON Filtrado (Resumen + Coincidencias Regex) ", padding=5)
col_derecha.pack(side="right", fill="both", expand=True, padx=5)

btn_copiar_filtrado = ttk.Button(col_derecha, text="📋 Copiar Reporte Filtrado", command=copiar_filtrado)
btn_copiar_filtrado.pack(anchor="e", pady=2)

txt_json_filtrado = tk.Text(col_derecha, wrap="none", font=("Courier New", 10), bg="#1e1e1e", fg="#3ba55d", insertbackground="white")
scroll_y_f = ttk.Scrollbar(col_derecha, orient="vertical", command=txt_json_filtrado.yview)
scroll_x_f = ttk.Scrollbar(col_derecha, orient="horizontal", command=txt_json_filtrado.xview)
txt_json_filtrado.configure(yscrollcommand=scroll_y_f.set, xscrollcommand=scroll_x_f.set)
scroll_y_f.pack(side="right", fill="y")
txt_json_filtrado.pack(fill="both", expand=True)
scroll_x_f.pack(fill="x")


def al_cerrar_ventana():
    try:
        detener_navegador()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", al_cerrar_ventana)

if __name__ == "__main__":
    root.mainloop()