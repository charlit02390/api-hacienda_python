# -*- coding: utf-8 -*-
import base64
import datetime
import pytz
from connexion.exceptions import OAuthProblem
from configuration import globalsettings
from num2words import num2words

from io import BytesIO as StringIO

cfg = globalsettings.cfg

TOKEN_DB = {
    cfg['api_key']: {
        'uid': 100
    }
}

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree


# REPRESENTACION DE NUMERO EN PALABRAS
def numToWord(n):
    return num2words(n, lang='es_CO', to='currency')


# REDONDEA UN NUMERO FLOAT EN FORMATO STRING
def stringRound(s):
    return round(float(s), 2)


# CONVIERTE UN STRING A BASE 64
def stringToBase64(s):
    return base64.b64encode( s ).decode()


# TOMA UNA CADENA Y ELIMINA LOS CARACTERES AL INICIO Y AL FINAL
def stringStrip(s, start, end):
    return s[start:-end]


# Tomamos el XML y le hacemos el decode de base 64, esto por ahora es solo para probar
# la posible implementacion de la firma en python
def base64decode(string_decode):
    return base64.b64decode( string_decode )


# TOMA UNA CADENA EN BASE64 Y LA DECODIFICA PARA ELIMINAR EL b' Y DEJAR EL STRING CODIFICADO
# DE OTRA MANERA HACIENDA LO RECHAZA
def base64UTF8Decoder(s):
    return s.decode( "utf-8" )


# CLASE PERSONALIZADA (NO EXISTE EN PYTHON) QUE CONSTRUYE UNA CADENA MEDIANTE APPEND SEMEJANTE
# AL STRINGBUILDER DEL C#
class StringBuilder:
    _file_str = None

    def __init__(self):
        self._file_str = StringIO()

    def Append(self, str):
        self._file_str.write( str )

    def __str__(self):
        return self._file_str.getvalue()


def limit(str, limit):
    return (str[:limit - 3] + '...') if len( str ) > limit else str


def get_time_hacienda(format='N'):
    now_utc = datetime.datetime.now( pytz.timezone( 'UTC' ) )
    now_cr = now_utc.astimezone( pytz.timezone( 'America/Costa_Rica' ) )
    if format == 'N':
        date_cr = now_cr.strftime( "%Y-%m-%dT%H:%M:%S-06:00" )
    else:
        date_cr = now_cr.strftime( "%d%m%y" )

    return date_cr


def parse_xml(name):
    return etree.parse( name ).getroot()


def api_key_auth(token, required_scopes=None):
    info = TOKEN_DB.get(token, None)
    if not info:
        raise OAuthProblem('Invalid token')
    return info


def buildResponseData(result: dict, defaultbody = list, warningmsg: str = None, errormsg: str = None) -> dict:
    """
    Builds data for a response from the given result.
    
    If the result passes validation, it's set as 'body'.
    Optionally, receives a list or dict type for a default body; and, warning and/or error messages to be set.

    :param result: dict - A dictionary with possible data for the response body.
    :param defaultbody: [optional] type(list|dict) - The type for list or dict that will be used as default empty body.
    :param warningmsg: [optional] str - A warning message to be displayed if a warning was triggered.
    :param errormsg: [optional] str - An error message to be displayed if an error was raised.
    :returns: dict - A dictionary with data to be used to generate a proper response.
    :raises TypeError: If the defaultbody parameters is not of type(list) or type(dict)
    """
    if defaultbody is not list and defaultbody is not dict:
        raise TypeError('defaultbody argument must be a list or dict type')

    response = {'httpstatus' : 200, 'body' : defaultbody()}

    # Error happened? Set error message and status code
    if '_error' in result:
        response['error'] = errormsg or result['_error']
        response['httpstatus'] = 500

    # Warning prompted? Set a nice message
    elif '_warning' in result:
        response['message'] = warningmsg or result['_warning']

    # All good? Valid body, therefore set it
    else:
        response['body'] = result

    return response


def prepareResponse(mainpropertyname: str, data: dict) -> dict:
    """
    Prepares a response to be sent with the received data.

    :param mainpropertyname: str - The name of the property that will hold the response's body.
    :param data: dict - The dictionary with data to build the response.
    :returns: dict - A dictionary with keys:
        'mainpropertyname' : The main body for the response.
        'status' : An status code for the operation. To be propertly determined. For now:
            0 = All good.
            1 = No data found.
            20 = Error.
        {scraped, but might be used later...?}
        ['error'] : If an error was raised, this will contain an error message.
        ['message'] : If a warning was emitted, this will contain a warning or information message.
    """
    response = {'status' : '0', mainpropertyname : data['body']}

    if 'message' in data:
        response['status'] = '1' # data['message']

    if 'error' in data:
        response['status'] = '20' # data['error']


    return response
