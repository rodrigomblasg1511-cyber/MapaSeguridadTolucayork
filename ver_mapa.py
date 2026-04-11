import os
import sys
from supabase import create_client
from shapely import wkb

# Llaves desde la bóveda secreta de GitHub
URL_SUPABASE = os.getenv('URL_SUPABASE')
KEY_SUPABASE = os.getenv('KEY_SUPABASE')
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

def generar_mapa():
    try:
        # 1. Descargar los incidentes de la base de datos
        respuesta = supabase.table("incidentes").select("*").execute()
        incidentes = respuesta.data or []

        # 2. Cabecera del archivo HTML
        html_start = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mapa de Seguridad Toluca</title>
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
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }).addTo(map);

                var redIcon = new L.Icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });

                var goldIcon = new L.Icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                });
        """

        markers_js = ""
        puntos_ok = 0

        # 3. Procesar cada punto de forma súper segura
        for ins in incidentes:
            coord_hex = ins.get('coordenadas')
            if not coord_hex: 
                continue
            
            try:
                punto = wkb.loads(coord_hex, hex=True)
                if punto is None: 
                    continue
                lon, lat = punto.x, punto.y
                
                titulo = str(ins.get('titulo', 'Incidente')).replace('"', '').replace("'", '')
                texto_analisis = (str(ins.get('tipo_delito', '')) + " " + titulo).lower()
                
                palabras_rojas = ["robo", "asalto", "muerto", "homicidio", "arma", "violencia", "frustran", "fallece", "cristalazo", "montachoque", "carterazo", "ajuste de cuentas", "agresion", "acoso", "detenido", "capturan", "investigan"]
                palabras_doradas = ["choque", "accidente", "vial", "volcadura", "tráfico", "moto", "carro", "seguridad", "policía"]

                if any(x in texto_analisis for x in palabras_rojas):
                    icon_js = "redIcon"
                elif any(x in texto_analisis for x in palabras_doradas):
                    icon_js = "goldIcon"
                else:
                    icon_js = "goldIcon"

                markers_js += f"L.marker([{lat}, {lon}], {{icon: {icon_js}}}).addTo(map).bindPopup('<b>{titulo}</b>');\n"
                puntos_ok += 1
                
            except Exception:
                # Si este incidente en particular está roto, lo ignora y pasa al siguiente sin detener el programa
                continue

        html_end = "</script></body></html>"

        # 4. Guardar el archivo definitivo (Esto garantiza que el index.html SIEMPRE nazca)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_start + markers_js + html_end)
            
        print(f"✅ ¡Mapa actualizado con {puntos_ok} puntos válidos!")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1) # Ahora sí, si se rompe algo grave, se pondrá en rojo en GitHub

if __name__ == "__main__":
    print("🗺️ Dibujando mapa en la nube...")
    generar_mapa()
    print("✅ Proceso terminado.")
