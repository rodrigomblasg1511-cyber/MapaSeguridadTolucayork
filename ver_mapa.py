import os
import sys
from supabase import create_client
from shapely import wkb

URL_SUPABASE = os.getenv('URL_SUPABASE')
KEY_SUPABASE = os.getenv('KEY_SUPABASE')
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

def generar_mapa():
    try:
        respuesta = supabase.table("incidentes").select("*").execute()
        incidentes = respuesta.data or []

        html_start = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa de Seguridad</title>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>body { margin: 0; } #map { width: 100vw; height: 100vh; }</style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([19.2826, -99.6557], 12);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                var redIcon = L.icon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png', shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41] });
                var goldIcon = L.icon({ iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png', shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41] });
        """

        markers_js = ""
        for ins in incidentes:
            try:
                coord_hex = ins.get('coordenadas')
                if not coord_hex: continue
                punto = wkb.loads(coord_hex, hex=True)
                lon, lat = punto.x, punto.y
                titulo = str(ins.get('titulo', 'Incidente')).replace("'", "")
                
                # Clasificación simple
                icon = "redIcon" if "robo" in titulo.lower() or "muerto" in titulo.lower() else "goldIcon"
                markers_js += f"L.marker([{lat}, {lon}], {{icon: {icon}}}).addTo(map).bindPopup('{titulo}');\n"
            except: continue

        os.makedirs("public", exist_ok=True)
        with open("public/index.html", "w", encoding="utf-8") as f:
            f.write(html_start + markers_js + "</script></body></html>")
        print("✅ Mapa generado en public/index.html")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generar_mapa()
