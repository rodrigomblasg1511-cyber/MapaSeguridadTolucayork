import os
import time
import json
from supabase import create_client
import google.generativeai as genai

# LLAVES SEGURAS
URL_SUPABASE = os.getenv('URL_SUPABASE')
KEY_SUPABASE = os.getenv('KEY_SUPABASE')
GEMINI_KEY = os.getenv('GEMINI_KEY')

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def ejecutar_extraccion():
    fuentes = ["metricadigital.com", "adnoticias.mx", "elsoldetoluca.com.mx"]
    print(f"🛰️ Buscando noticias en: {fuentes}")

    prompt_busqueda = f"Dame una lista de los 10 títulos más recientes de seguridad en Toluca de estos sitios: {fuentes}. Responde solo los títulos, uno por línea."

    try:
        # CORRECCIÓN: Usamos 'model' que es lo que definiste arriba
        response = model.generate_content(prompt_busqueda)
        titulos = response.text.strip().split('\n')
        
        for titulo in titulos:
            titulo = titulo.strip()
            if len(titulo) < 15: continue

            check = supabase.table("incidentes").select("id").eq("titulo", titulo).execute()
            if len(check.data) > 0: continue

            print(f"🆕 NOTICIA NUEVA: {titulo[:50]}...")
            
            prompt_coords = f'Analiza: "{titulo}". Responde SOLO JSON: {{"delito": "Tipo", "lat": 19.x, "lon": -99.x}}'
            
            try:
                time.sleep(3) 
                # CORRECCIÓN: Aquí también usamos 'model'
                res_coords = model.generate_content(prompt_coords)
                txt = res_coords.text.strip().replace('```json', '').replace('```', '')
                datos = json.loads(txt)
                
                nueva_fila = {
                    "titulo": titulo,
                    "tipo_delito": datos['delito'],
                    "coordenadas": f"POINT({datos['lon']} {datos['lat']})"
                }
                
                supabase.table("incidentes").insert(nueva_fila).execute()
                print(f"📍 AGREGADO: {datos['delito']}")
                
            except Exception as e:
                print(f"⚠️ Error en noticia: {e}")

    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    ejecutar_extraccion()
