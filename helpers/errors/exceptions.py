import warnings
import traceback

from werkzeug.exceptions import HTTPException, InternalServerError, Unauthorized
from flask import g
from lxml import etree

from helpers.debugging import DEBUG_G_VAR_NAME
from . import enums


# TODO : formatting class for message dictionary

# CUSTOM EXCEPTIONS FOR HANDLERS
class IBError(HTTPException):
    """
    Base class for the other system exceptions to be handled for custom responses.
    """
    status = 'Error Interno'
    error_code = enums.InternalErrorCodes.INTERNAL_ERROR
    message_dictionary = {}
    default_message = InternalServerError.description

    def __init__(self, *args, error_code=None, status=None, message=None):
        super().__init__()

        if error_code is not None:
            self.error_code = error_code

        if status is not None:
            self.status = status

        self.message = message
        self.args = args

    def get_message(self):
        if self.message:
            return self.message

        try:
            return self._format_message(self.message_dictionary[self.error_code], self.args)
        except KeyError:
            return self.default_message

    @staticmethod
    def _format_message(message, args):
        try:
            return message.format(*args)
        except IndexError:
            # TODO : change exceptions or messages to include amount of args required for formatting.
            warnings.warn(
                'Message formatting failed. Returning message without formatting. '
                'Check that the amount of arguments passed to the Exception'
                ' matches the exception type.'
            )
            return message

    def to_response(self):
        exc = {
            'status': self.status,
            'code': self.error_code,
            'detail': self.get_message()
        }
        if g.get(DEBUG_G_VAR_NAME):
            exc['debug'] = self._build_debug_info(self)

        return exc

    @staticmethod
    def _build_debug_info(exception: Exception):
        info = """Exception Type: {type}
Args: {args}
Traceback: {trace}""".format(type=type(exception),
                             args=exception.args,
                             trace=traceback.format_exc())
        return info


class ServerError(IBError):
    """
    Class for errors related to logic errors or internal application-based unhandled exceptions
    Error handler for this error type will set an HTTP Status Code of 500
    """
    # HTTPException override
    code = 500

    # IBError overrides
    message_dictionary = {
        enums.InternalErrorCodes.INTERNAL_ERROR: InternalServerError.description
    }


class HaciendaError(IBError):
    """
    Class for errors thrown by Hacienda during a request.
    HTTP Status code for this will be 502.
    """
    code = 502
    status = 'Error Hacienda'

    def __init__(self, *args, http_status, headers, body, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_status = http_status
        self.headers = headers
        self.body = body

    def get_message(self):  # override
        data = self.body
        if 'html' in self.headers.get('content-type', ''):
            htmldoc = etree.HTML(self.body)
            data = htmldoc.findtext('.//title')

        return """Se presentó un error en el servidor de Hacienda durante la solicitud:
HTTP Status: {}
Datos: {}""".format(self.http_status, data)


class AuthError(IBError):
    """
    Exception raised when an authorization challenge fails.
    """
    # HTTPException override
    code = 401

    # IBError overrides
    status = 'Error Auth'
    error_code = enums.AuthErrorCodes._BASE
    message_dictionary = {
        enums.AuthErrorCodes.WRONG_CREDENTIALS:
            'Credenciales incorrectas. Por favor, intente nuevamente.',
        **dict.fromkeys([
            enums.AuthErrorCodes.WRONG_API_KEY,
            enums.AuthErrorCodes.WRONG_JWT
        ], Unauthorized.description)
    }
    default_message = Unauthorized.description


class InputError(IBError):
    """
    Exception raised when incoming data doesn't conform to application rules.
    """
    # HTTPException override
    code = 400

    # IBError overrides
    error_code = enums.InputErrorCodes._BASE
    status = 'Incorrecto'
    message_dictionary = {
        enums.InputErrorCodes.MISSING_PROPERTY:
            'Propiedad faltante: "{}"{}',
        enums.InputErrorCodes.INCORRECT_TYPE:
            'Tipo incorrecto en: {} => {}',
        enums.InputErrorCodes.DUPLICATE_RECORD:
            '{} ya se encuentra registrado en el sistema.',
        enums.InputErrorCodes.NO_RECORD_FOUND:
            'Solicitado {} con identificador: "{}" no fue encontrado en el sistema.',
        enums.InputErrorCodes.P12_PIN_MISMATCH:
            'El PIN provisto para la firma p12 no es correcto.',
        enums.InputErrorCodes.INACTIVE_COMPANY:
            'La operación no se puede completar para una compañia inactiva.'
    }
    default_message = 'Los datos recibidos no posee el formato correcto.'


class ValidationError(InputError):
    """
    Exception raised when data received doesn't pass validation.
    """
    # IBError overrides
    status = 'Invalido'
    error_code = enums.ValidationErrorCodes._BASE
    message_dictionary = {
        enums.ValidationErrorCodes.INVALID_KEY_COMPOSITION:
            "La clave del documento no es válida. Razones: {}",
        enums.ValidationErrorCodes.INVALID_DATETIME_FORMAT:
            r'''El valor de fecha - {} - en "{}" no corresponde a alguno de los siguientes formatos:
YYYY-MM-DDThh:mi:ss[Z|(+|-)hh:mm]
ó
DD-MM-YYYYThh:mi:ss[Z|(+|-)hh:mm]
ó
DD/MM/YYYY''',
        enums.ValidationErrorCodes.INVALID_EMAIL:
            'Correo inválido: {}'
    }
    default_message = 'Datos inválidos.'


class EmailError(ServerError):
    """
    Exception raised when a problem related to the email module occurs.
    """
    # IBError overrides
    status = 'Error Email'
    error_code = enums.EmailErrorCodes._BASE
    message_dictionary = {
        enums.EmailErrorCodes.SMTP_CONNECTION_ERROR:
            'Se presentó un problema con la conexión al servidor SMTP.',
        enums.EmailErrorCodes.SMTP_NOT_SUPPORTED_ERROR:
            'La operación intentada no es soportada por el servidor SMTP.',
        enums.EmailErrorCodes.SMTP_AUTH_ERROR:
            'El proceso de autentificación falló.',
        enums.EmailErrorCodes.SENDER_REFUSED:
            'El servidor del emisor rechazo la solicitud.',
        enums.EmailErrorCodes.SMTP_DATA_ERROR:
            'Los datos enviados al servidor fueron rechazados.',
        enums.EmailErrorCodes.ALL_RECIPIENTS_REFUSED:
            'El correo fue rechazado por todos los receptores.'
    }
    default_message = 'Se presentó un problema enviando el correo.'


class DatabaseError(ServerError):
    """
    Exception raised when a problem related to database operations occurs.
    """
    # IBError overrides
    status = 'Error BaseDatos'
    error_code = enums.DBErrorCodes._BASE
    message_dictionary = {
        enums.DBErrorCodes.DB_CABYS_SEARCH_MEDICATION:
            'Se presentó un problema al buscar el medicamento solicitado.',
        enums.DBErrorCodes.DB_CABYS_SEARCH_CODE:
            'Se presentó un problema buscando el código CABYS solicitado.',
        enums.DBErrorCodes.DB_CABYS_SEARCH_SACS:
            'Se presentó un problema buscando el código SACS solicitado.',
        enums.DBErrorCodes.DB_REGISTRY_SELECT_ONE:
            'Se presentó un problema buscando la persona solicitada.',
        enums.DBErrorCodes.DB_COMPANY_CREATE:
            'La compañia no se pudo guardar. {}',
        enums.DBErrorCodes.DB_COMPANY_CREATE_MH:
            'Los datos de Hacienda de la compañia no se pudieron crear. {}',
        enums.DBErrorCodes.DB_COMPANY_UPDATE:
            'La compañia no pudo ser actualizada. {}',
        enums.DBErrorCodes.DB_COMPANY_UPDATE_MH:
            'Los datos de Hacienda de la compañia no pudieron ser actualizados. {}',
        enums.DBErrorCodes.DB_COMPANY_DELETE:
            'La compañia no pudo ser eliminada. {}',
        enums.DBErrorCodes.DB_COMPANY_SELECT_ONE:
            'Se presentó un problema al obtener los datos de la compañia.',
        enums.DBErrorCodes.DB_COMPANY_SELECT_ALL:
            'Se presentó un problema al obtener las compañias del sistema.',
        enums.DBErrorCodes.DB_COMPANY_SIGNATURE:
            'Se presentó un problema al obtener los datos de la firma de la compañia.',
        enums.DBErrorCodes.DB_COMPANY_LOGO:
            'Se presentó un problema al obtener el logo de la compañia.',
        enums.DBErrorCodes.DB_COMPANY_VERIFY:
            'Se presentó un problema al verificar la compañia.',
        enums.DBErrorCodes.DB_COMPANY_SMTP_CREATE:
            'El SMTP de la compañia no se logró guardar. {}',
        enums.DBErrorCodes.DB_COMPANY_SMTP_UPDATE:
            'El SMTP de la compañia no se logro actualizar. {}',
        enums.DBErrorCodes.DB_COMPANY_SMTP_DELETE:
            'El SMTP de la compañia no se logro eliminar. {}',
        enums.DBErrorCodes.DB_COMPANY_SMTP_SELECT_ONE:
            'Los datos del SMTP de la compañia no se lograron obtener.',
        enums.DBErrorCodes.DB_COMPANY_SMTP_VERIFY:
            'Se presentó un problema al verificar el SMTP de la compañia.',
        enums.DBErrorCodes.DB_DOCUMENT_CREATE:
            'El documento no se pudo guardar. {}',
        enums.DBErrorCodes.DB_DOCUMENT_DETAIL_LINE_CREATE:
            'Una linea de detalle para el documento no se logro guardar.'
            ' La operación no se pudo completar {}',
        enums.DBErrorCodes.DB_DOCUMENT_LINE_TAX_CREATE:
            'La información de impuestos para el documento no se logro guardar.'
            ' La operación no se pudo completar. {}',
        enums.DBErrorCodes.DB_DOCUMENT_ADDITIONAL_EMAIL_CREATE:
            'Se presentó un problema al procesar los correos adicionales provistos. {}',
        enums.DBErrorCodes.DB_DOCUMENT_UPDATE:
            'El documento no se logró actualizar. {}',
        enums.DBErrorCodes.DB_DOCUMENT_SELECT_ONE:
            'Se presentó un problema al obtener los datos del documento.',
        enums.DBErrorCodes.DB_DOCUMENT_SELECT_BY_COMPANY_AND_TYPE:
            'Se presentó un problema obteniendo los documentos de la compañia.',
        enums.DBErrorCodes.DB_DOCUMENT_SELECT_ADDITIONAL_EMAILS_BY_KEY:
            "Se presentó un problema obteniendo los correos adicionales del documento.",
        enums.DBErrorCodes.DB_DOCUMENT_JOBS:
            'Se presentó un problema al obtener los documentos para una tarea programada.'
            ' Acción relacionada: {}',
        enums.DBErrorCodes.DB_DOCUMENT_UPDATE_ISSENT:
            'Se presentó un problema al actualizar si el correo para el documento fue enviado. {}',
        enums.DBErrorCodes.DB_USER_CREATE:
            'El usuario no se pudo guardar. {}',
        enums.DBErrorCodes.DB_USER_COMPANIES_LINK:
            'No se pudieron asignar las compañias del usuario. {}',
        enums.DBErrorCodes.DB_USER_COMPANIES_UNLINK:
            "No se pudieron quitar las compañias del usuario. {}",
        enums.DBErrorCodes.DB_USER_UPDATE:
            'El usuario no pudo ser actualizado. {}',
        enums.DBErrorCodes.DB_USER_DELETE:
            'El usuario no pudo ser eliminado. {}',
        enums.DBErrorCodes.DB_USER_SELECT_ONE:
            'Se presentó un problema al intentar obtener los datos del usuario. {}',
        enums.DBErrorCodes.DB_USER_COMPANIES_SELECT_ALL:
            'Se presentó un problema obteniendo las compañias del usuario.',
        enums.DBErrorCodes.DB_USER_SELECT_ALL:
            'Se presentó un problema obteniendo los usuarios del sistema.',
        enums.DBErrorCodes.DB_USER_EMAIL_VERIFY:
            'Se presentó un problema verificando al usuario por su email.',
        enums.DBErrorCodes.DB_USER_VERIFY:
            'Se presentó un problema verificando al usuario.',
        enums.DBErrorCodes.DB_MESSAGE_CREATE:
            'Se presentó un problema al guardar el mensaje. {}',
        enums.DBErrorCodes.DB_MESSAGE_UPDATE_ANSWER:
            'Se presentó un problema al actualizar el mensaje con la respuesta de Hacienda. {}',
        enums.DBErrorCodes.DB_MESSAGE_UPDATE_EMAILSENT:
            'Se presentó un problema al actualizar si el correo del mensaje fue enviado. {}'
    }
    default_message = 'Se presentó un problema en las operaciones de la base de datos.'

# END_CUSTOM_EXCEPTIONS
