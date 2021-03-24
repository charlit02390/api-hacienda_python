from flask import Flask, jsonify
from extensions import mysql
from configuration import globalsettings
from routes import scheduler
import connexion

from helpers import debugging
from helpers.errors import handlers as errorhandlers
from helpers.overrides.connexion import DetailedRequestBodyValidator

app = Flask(__name__)


cfg = globalsettings.cfg

app.config['MYSQL_DATABASE_USER'] = cfg['mysql']['user']
app.config['MYSQL_DATABASE_PASSWORD'] = cfg['mysql']['passwd']
app.config['MYSQL_DATABASE_DB'] = cfg['mysql']['db']
app.config['MYSQL_DATABASE_HOST'] = cfg['mysql']['host']
mysql.init_app(app)
options = {'swagger_path': '/api/swagger_ui/'}
spec_args = {'debug_switch' : debugging.DEBUG_SWITCH_NAME}
validator_map = {
    'body': DetailedRequestBodyValidator
}
app = connexion.App(__name__, specification_dir='./', options=options)
app.add_api('api-hacienda.yaml',arguments=spec_args,
            validator_map=validator_map)
app.app.config['JSON_SORT_KEYS'] = False
app.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Sets custom error handlers for application error responses.
errorhandlers.register_flask_app_handlers(app)

if __name__ == '__main__':
    scheduler.scheduled_jobs()
    app.run(host='0.0.0.0', port=3005)

