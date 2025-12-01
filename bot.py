import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN ---
# El token se obtiene de las Variables de Entorno de Railway (TELEGRAM_BOT_TOKEN)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALBION_API_URL_WEST = "https://west.albion-online-data.com/api/v2/stats/prices/"

# --- 2. FUNCIÓN PARA BUSCAR EN ALBION ONLINE API ---

def obtener_precio_albion(nombre_objeto):
    # La API necesita que los espacios se reemplacen por guiones bajos
    item_id = nombre_objeto.upper().replace(" ", "_")
    
    # Construir la URL completa para el servidor de América (WEST)
    url = f"{ALBION_API_URL_WEST}{item_id}"
    
    try:
        # Realizar la solicitud a la API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return f"❌ No se encontraron datos para '{nombre_objeto}'. Verifica el nombre exacto del objeto."
        
        mensaje = f"💰 **Precios Actuales para: {nombre_objeto.capitalize()}**\n\n"
        
        # Filtramos y procesamos solo los datos de algunas ciudades clave
        ciudades_clave = ["Black Market", "Caerleon", "Thetford", "Fort Sterling", "Martlock"]
        datos_encontrados = False
        
        for item in data:
            city = item.get("city")
            
            if city in ciudades_clave:
                datos_encontrados = True
                # Precios de Venta (Buy) y Compra (Sell)
                buy_price_max = item.get("buy_price_max", 0) # Lo máximo que pagan
                sell_price_min = item.get("sell_price_min", 0) # Lo mínimo que piden
                
                # Formatear la salida
                mensaje += f"📍 **{city}**:\n"
                mensaje += f"   - Venta Máx. (Si vendes): {buy_price_max:,} plata\n"
                mensaje += f"   - Compra Mín. (Si compras): {sell_price_min:,} plata\n"
        
        if not datos_encontrados:
            return f"⚠️ Se encontraron datos, pero no en las ciudades clave."
            
        return mensaje
        
    except requests.exceptions.RequestException as e:
        return f"🚨 Error al conectar con la API de Albion Online: {e}"
    except Exception as e:
        return f"🚨 Error interno: {e}"

# --- 3. FUNCIONES DE TELEGRAM (HANDLERS) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente de arbitraje de Albion Online.\n"
        "Envíame el **nombre exacto de un objeto** (ej: 'Espada Anónima T5') y te daré sus precios más recientes en el servidor de América (WEST).\n"
    )

async def buscar_objeto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nombre_objeto_usuario = update.message.text.strip()
    
    await update.message.reply_text(f"🔍 Buscando precios para **{nombre_objeto_usuario}**...")