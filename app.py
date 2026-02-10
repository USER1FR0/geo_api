from flask import Flask, render_template, request
import requests

app = Flask(__name__, template_folder= './templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET','POST'])
def buscar():
    if request.method == 'POST':
        # Verificar si viene ubicación actual
        if request.form.get('lat_actual') and request.form.get('lon_actual'):
            lat = float(request.form.get('lat_actual'))
            lon = float(request.form.get('lon_actual'))
            nombre = "Mi ubicación actual"
            
            return render_template(
                'map.html',
                lat=lat,
                lon=lon,
                nombre=nombre
            )
        
        # Buscar por nombre
        lugar = request.form.get('lugar')
        if lugar:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': lugar,
                'format': 'json',
                'limit': 1
            }

            headers = {"User-Agent": "Flask-Educational-App"}

            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                nombre = data[0]['display_name']

                return render_template(
                    'map.html',
                    lat=lat,
                    lon=lon,
                    nombre=nombre
                )

    return render_template('map.html', error=True)

@app.route('/gasolineras', methods=['POST'])
def gasolineras():
    try:
        lat = float(request.form.get('lat'))
        lon = float(request.form.get('lon'))
        nombre = request.form.get('nombre', 'Ubicación')
        
        print(f"Buscando gasolineras cerca de: {lat}, {lon}")

        # buscar gasolineras cercanas
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        query = f"""
[out:json];
(
  node["amenity"="fuel"](around:5000,{lat},{lon});
  way["amenity"="fuel"](around:5000,{lat},{lon});
);
out center;
"""

        gasolineras_res = requests.post(overpass_url, data={'data': query})
        gasolineras_data = gasolineras_res.json() if gasolineras_res.status_code == 200 else {"elements": []}

        print(f"Gasolineras encontradas: {len(gasolineras_data.get('elements', []))}")

        gasolineras = []
        for g in gasolineras_data.get('elements', []):
            if 'lat' in g:
                lat_g = g['lat']
                lon_g = g['lon']
            else:
                lat_g = g['center']['lat']
                lon_g = g['center']['lon']

            gasolineras.append({
                'lat': float(lat_g),
                'lon': float(lon_g),
                'nombre': g.get('tags', {}).get('name', 'Sin nombre')
            })

        return render_template(
            'map.html',
            lat=lat,
            lon=lon,
            nombre=nombre,
            gasolineras=gasolineras
        )
    except Exception as e:
        print(f"Error: {e}")
        return render_template('map.html', error=True)

if __name__ == '__main__' :
    app.run(debug=True)