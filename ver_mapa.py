import os
import sys
from supabase import create_client
from shapely import wkb

# 1. Configuración de llaves
URL_SUPABASE = os.getenv('URL_SUPABASE')
KEY_SUPABASE = os.getenv('KEY_SUPABASE')

if not URL_SUPABASE or not KEY_SUPABASE:
    print("❌ Error: Faltan las llaves de Supabase en los Secrets.")
    sys.exit(1)

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

def generar_mapa():
    try:
        # 2. Descargar datos
        print("🛰️ Conectando a Supabase...")
        respuesta = supabase.table("incidentes").select("*").execute()
        incidentes = respuesta.data or []
        print(f"📦 Total de incidentes encontrados: {len(incidentes)}")

        # 3. Estructura de la página web
        html_start = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa de Seguridad</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body { margin: 0; padding: 0; }
                #map { width: 100vw; height: 100vh; }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([19.2826, -99.6557], 12);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);

                // Configuración de íconos
                var redIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });

                var goldIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });
        """

        # 4. Generar los globitos (Marcadores)
        markers_js = ""
        puntos_ok = 0

        for ins in incidentes:
            try:
                coord_hex = ins.get('coordenadas')
                if not coord_hex: continue

                # Traducir coordenadas
                punto = wkb.loads(coord_hex, hex=True)
                lon, lat = punto.x, punto.y
                
                titulo = str(ins.get('titulo', 'Incidente')).replace("'", "").replace('"', "")
                delito = str(ins.get('tipo_delito', '')).lower()
                
                # Decidir color del globito
                color = "redIcon" if any(x in delito for x in ["robo", "asalto", "muerto", "homicidio"]) else "goldIcon"
                
                # Crear la línea de JavaScript para este marcador
                markers_js += f"L.marker([{lat}, {lon}], {{icon: {color}}}).addTo(map).bindPopup('<b>{titulo}</b>');\n"
                puntos_ok += 1
            except Exception:
                continue

        html_end = """
            </script>
        </body>
        </html>
        """

        # 5. Guardar el archivo final
        os.makedirs("public", exist_ok=True)
        with open("public/index.html", "w", encoding="utf-8") as f:
            f.write(html_start + markers_js + html_end)
            
        print(f"✅ ¡Mapa listo con {puntos_ok} puntos en la carpeta public!")

    except Exception as e:
        print(f"❌ Error crítico al generar el mapa: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generar_mapa()
