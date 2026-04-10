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
    print(f"🛰️ Buscando noticias recientes en: {', '.join(fuentes)}")

    prompt_busqueda = f"""
    Encuentra las noticias más recientes de seguridad, choques y delitos en Toluca 
    de estos sitios: {fuentes}.
    Dame una lista de los títulos más actuales (máximo 10).
    Responde solo los títulos, uno por línea, sin símbolos.
    """

    try:
        response = client.models.generate_content(model=MODELO, contents=prompt_busqueda)
        titulos = response.text.strip().split('\n')
        
        print(f"📊 Analizando {len(titulos)} noticias recientes...")

        for titulo in titulos:
            titulo = titulo.strip()
            if len(titulo) < 15: continue

            # Evitar repetidos
            check = supabase.table("incidentes").select("id").eq("titulo", titulo).execute()
            if len(check.data) > 0:
                continue

            print(f"🆕 NOTICIA NUEVA: {titulo[:60]}...")
            
            prompt_coords = f"""
            Analiza: "{titulo}"
            Dime el tipo de incidente y coordenadas (Lat/Lon) en Toluca o Edomex.
            Responde SOLO JSON: {{"delito": "Tipo", "lat": 19.x, "lon": -99.x}}
            """
            
            try:
                # Pausa para que Google no bloquee la IA
                time.sleep(5)
                res_coords = client.models.generate_content(model=MODELO, contents=prompt_coords)
                txt = res_coords.text.strip().replace('```json', '').replace('```', '')
                datos = json.loads(txt)
                
                nueva_fila = {
                    "titulo": titulo,
                    "tipo_delito": datos['delito'],
                    "coordenadas": f"POINT({datos['lon']} {datos['lat']})"
                }
                
                supabase.table("incidentes").insert(nueva_fila).execute()
                print(f"📍 PUNTO AGREGADO: {datos['delito']}")
                
            except Exception as e:
                print(f"⚠️ Error en esta noticia: {e}")
                continue

    except Exception as e:
        print(f"❌ Error en la conexión: {e}")

if __name__ == "__main__":
    print("🤖 Robot en la nube trabajando...")
    ejecutar_extraccion()
    print("✅ Misión cumplida. Apagando.")
