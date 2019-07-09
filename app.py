from flask import Flask, jsonify
from extensions import mysql

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'jack_api_hacienda'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

from routes.companies import app as companies_app
app.register_blueprint( companies_app, url_prefix='/api/companies')

from routes.invoices import app as invoices_app
app.register_blueprint( invoices_app, url_prefix='/api/invoices')

from routes.utils import app as utils_app
app.register_blueprint( utils_app, url_prefix='/api/utils')


@app.route( "/", methods=['GET'] )
def route_index():
    return jsonify( {
        'apiVersion': 1.0
    } )


if __name__ == '__main__':
    app.run( host='localhost', port=3005, debug=False, threaded=False )
