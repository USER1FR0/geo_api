from flask import Flask, render_template, request
import requests

#Importar la libreria de flask
app = Flask(__name__, template_folder= './templates')

#Crear un objeto app con la propiedad __name__
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['GET','POST'])
def buscar():
    if request.method == 'POST':
        lugar = request.form['lugar']
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': lugar,
            'format': 'json',
            'limit': 1
        }
        headers = {
            "User-Agent": "Flask-Educational-App"
        }
        
        response = requests.get(url, params = params, headers = headers)
        data = response.json()
        
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            nombre = data[0]['display_name']
            
            return render_template(
                'map.html',
                lat = lat,
                lon = lon,
                nombre = nombre
            )
    return render_template('map.html', error = True)

if __name__ == '__main__' :
    app.run(debug=True)