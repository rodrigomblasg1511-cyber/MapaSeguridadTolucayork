import re
from supabase import create_client
from shapely import wkb

# 1. TUS LLAVES
URL_SUPABASE = 'https://vgovgphauqbaxhurqdqo.supabase.co'
KEY_SUPABASE = 'sb_publishable_jH3kroEnsfa0Trp5Aa-Yww_p9l4a2Mz'

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

def generar_mapa():
    print("🛰️ Generando mapa con semáforo de colores (Rojo, Dorado, Verde)...")
    try:
        res = supabase.table("incidentes").select("*").execute()
        incidentes = res.data
        
        html_start = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa Seguridad Toluca</title>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <style>#map { height: 100vh; width: 100%; } body { margin: 0; }</style>
        </head>
        <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                var map = L.map('map').setView([19.2827, -99.6557], 11);
                L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map);

                // Configuración de Iconos
                var redIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });
                var goldIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });
                var greenIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });
        """

        markers_js = ""
        puntos_ok = 0

        for ins in incidentes:
            coord_hex = ins.get('coordenadas')
            if not coord_hex: continue

try:
            punto = wkb.loads(coord_hex, hex=True)
            lon, lat = punto.x, punto.y
            
            titulo = str(ins.get('titulo', 'Incidente')).replace('"', '').replace("'", '')
            texto_analisis = (str(ins.get('tipo_delito', '')) + " " + titulo).lower()
            
            # Listas de palabras clave para el radar
            palabras_rojas = ["robo", "asalto", "muerto", "homicidio", "arma", "violencia", "frustran", "fallece", "cristalazo", "montachoque", "carterazo", "ajuste de cuentas", "agresion", "acoso", "detenido", "capturan", "investigan"]
            
            palabras_doradas = ["choque", "accidente", "vial", "volcadura", "tráfico", "moto", "carro", "seguridad", "policía"]

            # Clasificación de colores
            if any(x in texto_analisis for x in palabras_rojas):
                icon_js = "redIcon"
            elif any(x in texto_analisis for x in palabras_doradas):
                icon_js = "goldIcon"
            else:
                icon_js = "goldIcon" # Color por defecto si no detecta ninguna

            markers_js += f"L.marker([{lat}, {lon}], {{icon: {icon_js}}}).addTo(map).bindPopup('<b>{titulo}</b>');\n"
            puntos_ok += 1
            
        except:
            continue

        html_end = "</script></body></html>"
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_start + markers_js + html_end)
        
        print(f"✅ ¡Mapa actualizado! Ahora con globos Verdes, Rojos y Dorados.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_mapa()
