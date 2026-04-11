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
        puntos_ok = 0
        
        print(f"📦 Total de filas encontradas en Supabase: {len(incidentes)}")

        for ins in incidentes:
            try:
                coord_raw = ins.get('coordenadas')
                if not coord_raw: continue
                
                # Intentamos extraer lat y lon del texto "POINT(lon lat)"
                # Esto es más seguro si tu columna en Supabase es de texto
                if isinstance(coord_raw, str) and "POINT" in coord_raw:
                    coords_clean = coord_raw.replace("POINT(", "").replace(")", "")
                    lon, lat = map(float, coords_clean.split())
                else:
                    # Si es formato hexadecimal (Geometry), usamos shapely
                    punto = wkb.loads(coord_raw, hex=True)
                    lon, lat = punto.x, punto.y
                
                titulo = str(ins.get('titulo', 'Incidente')).replace("'", "")
                tipo = str(ins.get('tipo_delito', '')).lower()
                
                # Elegir icono
                icon = "redIcon" if any(x in tipo for x in ["robo", "asalto", "muerto"]) else "goldIcon"
                
                markers_js += f"L.marker([{lat}, {lon}], {{icon: {icon}}}).addTo(map).bindPopup('{titulo}');\n"
                puntos_ok += 1
            except Exception as e:
                print(f"⚠️ Saltando un punto por error: {e}")
                continue

if __name__ == "__main__":
    generar_mapa()
