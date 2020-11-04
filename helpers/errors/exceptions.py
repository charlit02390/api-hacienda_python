
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
    status = enums.InternalErrorCodes.INTERNAL_ERROR
    message_dictionary = {}
    default_message = InternalServerError.description

    def __init__(self, *args, status=None, message=None):
        super().__init__()
        if status is not None:
            self.status = status

        self.message = message
        self.args = args

    def get_message(self):
        if self.message:
            return self.message

        try:
            return self._format_message(self.message_dictionary[self.status], self.args)
        except KeyError:
            return self.default_message

    @staticmethod
    def _format_message(message, args):
        try:
            return message.format(*args)
        except IndexError:
            # TODO : change exceptions or messages to include amount of args required for formatting.
            warnings.warn('Message formatting failed. Returning message without formatting. Check that the amount of arguments passed to the Exception matches the exception type.')
            return message

    def to_response(self):
        exc = { 'status' : self.status,
              'detail' : self.get_message() }
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
        enums.InternalErrorCodes.INTERNAL_ERROR : InternalServerError.description
        }

class HaciendaError(IBError):
    """
    Class for errors thrown by Hacienda during a request.
    HTTP Status code for this will be 502.
    """
    code = 502

    def __init__(self, *args, http_status, headers, body, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_status = http_status
        self.headers = headers
        self.body = body

    def get_message(self): # override
        data = self.body
        if 'html' in self.headers.get('content-type', ''):
            htmldoc = etree.HTML(self.body)
            data = htmldoc.findtext('.//title')

        return """An error ocurred in Hacienda's Server during a request:
HTTP Status: {}
Data: {}""".format(self.http_status, data)


class AuthError(IBError):
    """
    Exception raised when an authorization challenge fails.
    """
    # HTTPException override
    code = 401

    # IBError overrides
    status = enums.AuthErrorCodes._BASE
    message_dictionary = {
        enums.AuthErrorCodes.WRONG_CREDENTIALS : 'Incorrect credentials. Please, try again.',
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
    status = enums.InputErrorCodes._BASE
    message_dictionary = {
        enums.InputErrorCodes.MISSING_PROPERTY : 'Missing property: "{}"{}',
        enums.InputErrorCodes.INCORRECT_TYPE : 'Incorrect type in: {} => {}',
        enums.InputErrorCodes.DUPLICATE_RECORD : '{} is already registered in the system.',
        enums.InputErrorCodes.NO_RECORD_FOUND : 'Requested {} with identifier: "{}" was not found in the system.',
        enums.InputErrorCodes.P12_PIN_MISMATCH : "The PIN provided for the p12 signature doesn't match.",
        enums.InputErrorCodes.INACTIVE_COMPANY: "The operation cannot be completed on an inactive company."
        }
    default_message = 'Received data is not properly formatted.'


class ValidationError(InputError):
    """
    Exception raised when data received doesn't pass validation.
    """
    # IBError overrides
    status = enums.ValidationErrorCodes._BASE
    message_dictionary = {
        enums.ValidationErrorCodes.INVALID_KEY_COMPOSITION : "Document's Key is not valid. Reasons: {}",
        enums.ValidationErrorCodes.INVALID_DATETIME_FORMAT : r'''The date value - {} - in "{}" is not any of these expected formats:
             YYYY-MM-DDThh:mi:ss[Z|(+|-)hh:mm]
             or
             DD-MM-YYYYThh:mi:ss[Z|(+|-)hh:mm]
             or
             DD/MM/YYYY''',
        enums.ValidationErrorCodes.INVALID_EMAIL : 'Invalid email: {}'
        }
    default_message = 'Invalid data.'

    
class EmailError(ServerError):
    """
    Exception raised when a problem related to the email module occurs.
    """
    # IBError overrides
    status = enums.EmailErrorCodes._BASE
    message_dictionary = {
        enums.EmailErrorCodes.SMTP_CONNECTION_ERROR : "There was a problem with the connection to the server.",
        enums.EmailErrorCodes.SMTP_NOT_SUPPORTED_ERROR : 'The operation attempted was not supported by the server.',
        enums.EmailErrorCodes.SMTP_AUTH_ERROR : 'The authentication process failed.',
        enums.EmailErrorCodes.SENDER_REFUSED : "The sender's server refused the request.",
        enums.EmailErrorCodes.SMTP_DATA_ERROR : 'The data sent to the server was refused.',
        enums.EmailErrorCodes.ALL_RECIPIENTS_REFUSED : 'Mail was refused by all the recipients.'
        }
    default_message = 'A problem was encountered when sending email.'


class DatabaseError(ServerError):
    """
    Exception raised when a problem related to database operations occurs.
    """
    # IBError overrides
    status = enums.DBErrorCodes._BASE
    message_dictionary = {
        enums.DBErrorCodes.DB_CABYS_SEARCH_MEDICATION : 'An issue was found while searching for the medication.',
        enums.DBErrorCodes.DB_CABYS_SEARCH_CODE : 'An issue was found while searching for the CABYS code.',
        enums.DBErrorCodes.DB_CABYS_SEARCH_SACS :  'An issue was found while searching for the SACS code.',
        enums.DBErrorCodes.DB_REGISTRY_SELECT_ONE : 'An issue was found while searching for the person.',
        enums.DBErrorCodes.DB_COMPANY_CREATE : "The company couldn't be created. {}",
        enums.DBErrorCodes.DB_COMPANY_CREATE_MH : "The company's Hacienda data couldn't be saved. {}",
        enums.DBErrorCodes.DB_COMPANY_UPDATE : "The company couldn't be updated. {}",
        enums.DBErrorCodes.DB_COMPANY_UPDATE_MH : "The company's Hacienda data couldn't be updated. {}",
        enums.DBErrorCodes.DB_COMPANY_DELETE : "The company couldn't be deleted. {}",
        enums.DBErrorCodes.DB_COMPANY_SELECT_ONE : "A problem occurred when obtaining the data for the company.",
        enums.DBErrorCodes.DB_COMPANY_SELECT_ALL : "An issue was found while obtaining the system's companies' data.",
        enums.DBErrorCodes.DB_COMPANY_SIGNATURE : "An issue was found while obtaining the company's signature information.",
        enums.DBErrorCodes.DB_COMPANY_LOGO : "An issue was found while obtaining the company's logo.",
        enums.DBErrorCodes.DB_COMPANY_VERIFY : "An issue was found while trying to verify the company.",
        enums.DBErrorCodes.DB_COMPANY_SMTP_CREATE : "The company's SMTP couldn't be saved. {}",
        enums.DBErrorCodes.DB_COMPANY_SMTP_UPDATE : "The company's SMTP couldn't be updated. {}",
        enums.DBErrorCodes.DB_COMPANY_SMTP_DELETE : "The company's SMTP couldn't be deleted. {}",
        enums.DBErrorCodes.DB_COMPANY_SMTP_SELECT_ONE : "The company's SMTP data couldn't be obtained.",
        enums.DBErrorCodes.DB_COMPANY_SMTP_VERIFY : "A problem occurred when trying to verify the SMTP.",
        enums.DBErrorCodes.DB_DOCUMENT_CREATE : "The document couldn't be saved. {}",
        enums.DBErrorCodes.DB_DOCUMENT_DETAIL_LINE_CREATE : "A detail line for the document couldn't be saved, so the operation stopped. {}",
        enums.DBErrorCodes.DB_DOCUMENT_LINE_TAX_CREATE : "The tax information for the document couldn't be saved, so the operation stopped. {}",
        enums.DBErrorCodes.DB_DOCUMENT_ADDITIONAL_EMAIL_CREATE : "A problem occurred when processing the additional emails provided. {}",
        enums.DBErrorCodes.DB_DOCUMENT_UPDATE : "The document couldn't be updated. {}",
        enums.DBErrorCodes.DB_DOCUMENT_SELECT_ONE : "An issue was found while obtaining the document's data.",
        enums.DBErrorCodes.DB_DOCUMENT_SELECT_BY_COMPANY_AND_TYPE : "An issue was found while trying to obtain the documents for the company.",
        enums.DBErrorCodes.DB_DOCUMENT_SELECT_ADDITIONAL_EMAILS_BY_KEY : "An issue was found while trying to obtain the additional emails registered for the document.",
        enums.DBErrorCodes.DB_DOCUMENT_JOBS : "An issue was found while querying documents from the database during a scheduled job. Action involved: {}",
        enums.DBErrorCodes.DB_DOCUMENT_UPDATE_ISSENT: "An issue was found while trying to set if the mail for the document was sent. {}",
        enums.DBErrorCodes.DB_USER_CREATE : "The user couldn't be created. {}",
        enums.DBErrorCodes.DB_USER_COMPANIES_LINK : "Couldn't assign the user's companies. {}",
        enums.DBErrorCodes.DB_USER_COMPANIES_UNLINK : "The user couldn't be updated. {}",
        enums.DBErrorCodes.DB_USER_UPDATE : "The user couldn't be updated. {}",
        enums.DBErrorCodes.DB_USER_DELETE : "The user couldn't be deleted. {}",
        enums.DBErrorCodes.DB_USER_SELECT_ONE : "A problem occurred when attempting to obtain the user's data.",
        enums.DBErrorCodes.DB_USER_COMPANIES_SELECT_ALL : "A problem occured when attempting to obtain the user's companies.",
        enums.DBErrorCodes.DB_USER_SELECT_ALL : "An issue was found while trying to obtain the users' data.",
        enums.DBErrorCodes.DB_USER_EMAIL_VERIFY : "A problem occured when attempting to verify the user by their email.",
        enums.DBErrorCodes.DB_USER_VERIFY : "An issue was found while trying to verify the user.",
        enums.DBErrorCodes.DB_MESSAGE_CREATE : "An issue was found while trying to create the message. {}",
        enums.DBErrorCodes.DB_MESSAGE_UPDATE_ANSWER : "An issue was found while trying to update a message from an Hacienda answer. {}",
        enums.DBErrorCodes.DB_MESSAGE_UPDATE_EMAILSENT: "An issue was found while trying to set if the email for the message was sent. {}"
        }
    default_message = 'A problem was encountered during database operations.'

# END_CUSTOM_EXCEPTIONS
