import os
import time
import json
from supabase import create_client
from google import genai

# LLAVES SEGURAS DESDE LA BÓVEDA DE GITHUB
URL_SUPABASE = os.getenv('URL_SUPABASE')
KEY_SUPABASE = os.getenv('KEY_SUPABASE')
GEMINI_KEY = os.getenv('GEMINI_KEY')

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)
client = genai.Client(api_key=GEMINI_KEY)
MODELO = 'gemini-2.0-flash'

def ejecutar_extraccion():
    fuentes = ["metricadigital.com", "adnoticias.mx", "elsoldetoluca.com.mx"]
    print(f"🛰️ Buscando noticias recientes en: {', '.join(
