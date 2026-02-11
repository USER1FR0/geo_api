"""
Aplicación Flask para mostrar ubicación y gasolineras cercanas usando OpenStreetMap.
- Ruta '/' muestra el formulario de búsqueda.
- Ruta '/buscar' procesa la búsqueda por nombre o ubicación actual.
- Ruta '/gasolineras' busca gasolineras cercanas usando Overpass API
"""

# --> Importaciones necesarias
from flask import Flask, render_template, request #<-- Crea la app web y maneja rutas y plantillas
import requests #<-- Para hacer solicitudes HTTP a APIs externas

# --> Crear la aplicación Flask y configurar la carpeta de plantillas
app = Flask(__name__, template_folder= './templates')

# --> Se ejecuta al acceder a la raíz del sitio, muestra el formulario de búsqueda o pagina principal/inicial
@app.route('/')
def index():
    return render_template('index.html')

# --> Se ejecuta al enviar el formulario de búsqueda, maneja tanto la búsqueda por nombre como por ubicación actual
# --> Permite metodos Get y Post, pero principalmente se espera un POST con los datos del formulario
@app.route('/buscar', methods=['GET','POST'])
def buscar():
    if request.method == 'POST':
        # Verificar si viene ubicación actual
        # Si el formulario incluye latitud y longitud, se asume que es la ubicación actual del usuario
        if request.form.get('lat_actual') and request.form.get('lon_actual'):
            lat = float(request.form.get('lat_actual'))
            lon = float(request.form.get('lon_actual'))
            nombre = "Mi ubicación actual"
            
            # Mostrar el mapa con la ubicación actual del usuario
            return render_template(
                'map.html',
                lat=lat,
                lon=lon,
                nombre=nombre
            )
        
        # Buscar por nombre
        # Si no se proporcionan coordenadas, se asume que el usuario está buscando por nombre de lugar
        lugar = request.form.get('lugar')
        if lugar:
            # Usar Nominatim para geocodificar el nombre del lugar a coordenadas
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': lugar,
                'format': 'json',
                'limit': 1
            }

            # Nominatim requiere un User-Agent personalizado para identificar la aplicación que hace la solicitud
            headers = {"User-Agent": "Flask-Educational-App"}

            # Hacer la solicitud a Nominatim para obtener las coordenadas del lugar buscado
            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if data:
                # Si se encuentra el lugar, extraer latitud, longitud y nombre completo para mostrar en el mapa
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                nombre = data[0]['display_name']

                # Mostrar el mapa con la ubicación del lugar buscado
                return render_template(
                    'map.html',
                    lat=lat,
                    lon=lon,
                    nombre=nombre
                )

    # Si no se encuentra el lugar o hay un error, mostrar el mapa con un mensaje de error
    return render_template('map.html', error=True)

# --> Se ejecuta al buscar gasolineras cercanas a una ubicación específica, recibe latitud y longitud para realizar la búsqueda
@app.route('/gasolineras', methods=['POST'])
def gasolineras():
    try:
        # Extraer latitud, longitud y nombre del formulario para buscar gasolineras cercanas a esa ubicación
        lat = float(request.form.get('lat'))
        lon = float(request.form.get('lon'))
        nombre = request.form.get('nombre', 'Ubicación')
        
        # --> Debug...
        print(f"Buscando gasolineras cerca de: {lat}, {lon}")

        # buscar gasolineras cercanas
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # La consulta Overpass busca nodos y vías etiquetados como "amenity=fuel" dentro de un radio de 5000 metros alrededor de las coordenadas proporcionadas
        query = f"""
                [out:json];
                (
                node["amenity"="fuel"](around:5000,{lat},{lon});
                way["amenity"="fuel"](around:5000,{lat},{lon});
                );
                out center;
            """
        # Hacer la solicitud POST a la API de Overpass con la consulta para obtener las gasolineras cercanas
        gasolineras_res = requests.post(overpass_url, data={'data': query})
        gasolineras_data = gasolineras_res.json() if gasolineras_res.status_code == 200 else {"elements": []}

        # Debug ...
        print(f"Gasolineras encontradas: {len(gasolineras_data.get('elements', []))}")

        # Procesar los resultados de la consulta para extraer latitud, longitud y nombre de cada gasolinera encontrada
        gasolineras = []
        for g in gasolineras_data.get('elements', []):
            if 'lat' in g:
                lat_g = g['lat']
                lon_g = g['lon']
            else:
                lat_g = g['center']['lat']
                lon_g = g['center']['lon']

            # Agregar la gasolinera a la lista con su latitud, longitud y nombre (si está disponible, de lo contrario se muestra "Sin nombre")
            gasolineras.append({
                'lat': float(lat_g),
                'lon': float(lon_g),
                'nombre': g.get('tags', {}).get('name', 'Sin nombre')
            })
        # Mostrar el mapa con la ubicación y las gasolineras cercanas
        return render_template(
            'map.html',
            lat=lat,
            lon=lon,
            nombre=nombre,
            gasolineras=gasolineras
        )
    # Si ocurre algún error durante el proceso de búsqueda de gasolineras, se captura la excepción y se muestra un mensaje de error en el mapa
    except Exception as e:
        print(f"Error: {e}")
        return render_template('map.html', error=True)

# --> Ejecutar la aplicación Flask en modo debug para facilitar el desarrollo y la depuración de errores
if __name__ == '__main__' :
    app.run(debug=True)