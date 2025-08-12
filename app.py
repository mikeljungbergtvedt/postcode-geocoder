from flask import Flask, request, send_file
from flask_cors import CORS
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
import pandas as pd
import time
import io

app = Flask(__name__)
CORS(app)

geolocator = Nominatim(user_agent="norwegian_postcode_webapp")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/geocode', methods=['POST'])
def geocode():
    try:
        data = request.get_json()
        postcodes = data.get('postcodes', [])
        
        if not postcodes:
            return {'error': 'No postcodes provided'}, 400

        results = []
        for postcode in postcodes:
            try:
                location = geolocator.geocode(f"{postcode}, Norway")
                results.append({
                    'Postcode': postcode,
                    'Latitude': location.latitude if location else None,
                    'Longitude': location.longitude if location else None
                })
                time.sleep(1)
            except (GeocoderTimedOut, GeocoderQuotaExceeded) as e:
                results.append({
                    'Postcode': postcode,
                    'Latitude': None,
                    'Longitude': None
                })

        df = pd.DataFrame(results)
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='postcode_coordinates.csv'
        )
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
