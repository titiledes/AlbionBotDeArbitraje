# Instala estas librerías primero si usas Python (el servidor lo hará por ti):
# pip install python-telegram-bot requests

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURACIÓN ---
# ¡IMPORTANTE! Este es el Token que te dio BotFather
TELEGRAM_BOT_TOKEN = "8259947015:AAE13WwqqBPtaNOmaFeP0NBWi8C59hmv9pE"
ALBION_API_URL_WEST = "https://west.albion-online-data.com/api/v2/stats/prices/"

# --- 2. FUNCIÓN PARA BUSCAR EN ALBION ONLINE API ---

def obtener_precio_albion(nombre_objeto):
    # La API necesita que los espacios se reemplacen por guiones bajos
    # Ejemplo: 'Espada Anónima T5' -> 'ESPADA_ANÓNIMA_T5'
    item_id = nombre_objeto.upper().replace(" ", "_")
    
    # Construir la URL completa para el servidor de América (WEST)
    url = f"{ALBION_API_URL_WEST}{item_id}"
    
    try:
        # Realizar la solicitud a la API
        response = requests.get(url)
        response.raise_for_status() # Lanza un error si la solicitud falla
        data = response.json()
        
        if not data:
            return f"❌ No se encontraron datos para '{nombre_objeto}'. Verifica el nombre exacto del objeto."
        
        # Procesar los datos de las ciudades principales para arbitraje
        mensaje = f"💰 **Precios Actuales para: {nombre_objeto.capitalize()}**\n\n"
        
        # Ciudades clave para el arbitraje
        ciudades_clave = ["Black Market", "Caerleon", "Thetford", "Fort Sterling", "Martlock", "Bridgewatch", "Lymhurst"]
        
        datos_encontrados = False
        
        for item in data:
            city = item.get("city")
            
            if city in ciudades_clave:
                datos_encontrados = True
                # buy_price_max: Precio máximo que pagan los compradores (lo que TÚ ganas al vender)
                buy_price_max = item.get("buy_price_max", 0) 
                # sell_price_min: Precio mínimo que piden los vendedores (lo que TÚ pagas al comprar)
                sell_price_min = item.get("sell_price_min", 0) 
                
                # Formatear la salida con separador de miles
                # Nota: Uso '.' como separador de miles y ',' como separador decimal si aplica,
                # aunque Albion Online usa números enteros para plata.
                buy_formateado = f"{buy_price_max:,}".replace(",", ".")
                sell_formateado = f"{sell_price_min:,}".replace(",", ".")

                mensaje += f"📍 **{city}**:\n"
                mensaje += f"   - Venta Máx. (Si tú vendes): **{buy_formateado}** plata\n"
                mensaje += f"   - Compra Mín. (Si tú compras): **{sell_formateado}** plata\n"

        if not datos_encontrados:
            return "⚠️ Se encontraron datos, pero no en las ciudades principales de comercio (Caerleon, Black Market, etc.)."
            
        return mensaje
        
    except requests.exceptions.RequestException as e:
        return f"🚨 Error al conectar con la API de Albion Online. Inténtalo de nuevo."
    except Exception as e:
        # Esto captura errores si el formato del nombre es muy incorrecto, etc.
        return f"🚨 Error en el procesamiento de datos. Asegúrate de usar el nombre de objeto exacto."

# --- 3. FUNCIONES DE TELEGRAM (HANDLERS) ---

# Comando /start o /ayuda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente de arbitraje de Albion Online (Servidor América).\n"
        "Envíame el **nombre exacto de un objeto** (ej: 'Espada Anónima T5') y te daré sus precios más recientes en las ciudades clave.\n\n"
        "**Ejemplo de uso:** Espada Anónima T5"
    )

# Función principal que procesa el mensaje del usuario
async def buscar_objeto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nombre_objeto_usuario = update.message.text.strip()
    
    # Notificar al usuario que estamos procesando
    await update.message.reply_text(f"🔍 Buscando precios para **{nombre_objeto_usuario}**...", parse_mode='Markdown')
    
    # Llamar a la función que interactúa con la API de Albion
    resultado = obtener_precio_albion(nombre_objeto_usuario)
    
    # Enviar el resultado al usuario. Parse_mode='Markdown' permite usar negritas, etc.
    await update.message.reply_text(resultado, parse_mode='Markdown')

# --- 4. CONFIGURACIÓN Y EJECUCIÓN PRINCIPAL ---

def main() -> None:
    # 1. Crear la aplicación (el bot)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 2. Asignar los "handlers" (qué función se ejecuta con qué comando o mensaje)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buscar_objeto))
    
    # 3. Iniciar el bot y dejarlo escuchando
    print("El bot de arbitraje está corriendo...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()