# -*- coding: utf-8 -*-
import base64
import datetime
import pytz
from connexion.exceptions import OAuthProblem
from configuration import globalsettings

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

# end me
from num2words.lang_ES_CO import Num2Word_ES
from helpers.errors.exceptions import InputError
from helpers.errors.enums import InputErrorCodes

class Num2Words_ES_CR(Num2Word_ES):
    CURRENCY_FORMS = {
            'EUR': (('euro', 'euros'), ('céntimo', 'céntimos')),
            'ESP': (('peseta', 'pesetas'), ('céntimo', 'céntimos')),
            'USD': (('dolar', 'dólares'), ('centavo', 'centavos')),
            'PEN': (('sol', 'soles'), ('céntimo', 'céntimos')),
            'CRC': (('colón', 'colones'), ('céntimo', 'céntimos')),
            }

    def num2words(self, val, currency='CRC'):
        if not isinstance(val, float):
            try:
                val = float(val)
            except ValueError as ver: # assuming totalComprobante is the only place where we are using this function... too lazy to properly change this... for now...
                raise InputError('totalComprobante', str(ver), status=InputErrorCodes.INCORRECT_TYPE)

        return self.to_currency(val, currency=currency)


# REPRESENTACION DE NUMERO EN PALABRAS
def numToWord(n, curr):
    return Num2Words_ES_CR().num2words(n, curr)


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

    def Append(self, _str):
        self._file_str.write(_str)

    def __str__(self):
        return self._file_str.getvalue()


def limit(_str, _limit):
    return (_str[:_limit - 3] + '...') if len(_str) > _limit else _str


def get_time_hacienda(_format='N'):
    now_utc = datetime.datetime.now( pytz.timezone( 'UTC' ) )
    now_cr = now_utc.astimezone( pytz.timezone( 'America/Costa_Rica' ) )
    if _format == 'N':
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
