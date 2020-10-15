from enum import IntEnum

# ENUMS
class AuthErrorCodes(IntEnum):
    _BASE = 10
    WRONG_CREDENTIALS = _BASE + 1
    WRONG_API_KEY = _BASE + 2
    WRONG_JWT = _BASE + 3


class InputErrorCodes(IntEnum):
    _BASE = 2 * 10
    MISSING_PROPERTY = _BASE + 1
    INCORRECT_TYPE = _BASE + 2
    DUPLICATE_RECORD = _BASE + 3
    NO_RECORD_FOUND = _BASE + 4
    P12_PIN_MISMATCH = _BASE + 5


class ValidationErrorCodes(IntEnum):
    _BASE = 3 * 10
    INVALID_KEY_COMPOSITION = _BASE + 1
    INVALID_DATETIME_FORMAT = _BASE + 2
    INVALID_EMAIL = _BASE + 5


class EmailErrorCodes(IntEnum):
    _BASE = 6 * 10
    SMTP_CONNECTION_ERROR = _BASE + 1
    SMTP_NOT_SUPPORTED_ERROR = _BASE + 2
    SMTP_AUTH_ERROR = _BASE + 3
    SENDER_REFUSED = _BASE + 4
    SMTP_DATA_ERROR = _BASE + 5
    ALL_RECIPIENTS_REFUSED = _BASE + 6


class DBErrorCodes(IntEnum):
    _BASE = 70000
    #   COMPANY
    _COMPANY = _BASE + 100
    DB_COMPANY_CREATE = _COMPANY + 1
    DB_COMPANY_UPDATE = _COMPANY + 2
    DB_COMPANY_DELETE = _COMPANY + 3
    DB_COMPANY_SELECT_ONE = _COMPANY + 4
    DB_COMPANY_SELECT_ALL = _COMPANY + 5
    DB_COMPANY_CREATE_MH = _COMPANY + 6
    DB_COMPANY_UPDATE_MH = _COMPANY + 7
    DB_COMPANY_SELECT_ONE_MH = _COMPANY + 8
    DB_COMPANY_SIGNATURE = _COMPANY + 9
    DB_COMPANY_LOGO = _COMPANY + 10
    DB_COMPANY_VERIFY = _COMPANY + 11
    #   END_COMPANY

    #   COMPANY_SMTP
    _COMPANY_SMTP = _BASE + 200
    DB_COMPANY_SMTP_CREATE = _COMPANY_SMTP + 1
    DB_COMPANY_SMTP_UPDATE = _COMPANY_SMTP + 2
    DB_COMPANY_SMTP_DELETE = _COMPANY_SMTP + 3
    DB_COMPANY_SMTP_SELECT_ONE = _COMPANY_SMTP + 4
    DB_COMPANY_SMTP_SELECT_ALL = _COMPANY_SMTP + 5
    DB_COMPANY_SMTP_VERIFY = _COMPANY_SMTP + 6
    #   END_COMPANY_SMPT

    #   USER
    _USER = _BASE + 300
    DB_USER_CREATE = _USER + 1
    DB_USER_UPDATE = _USER + 2
    DB_USER_DELETE = _USER + 3
    DB_USER_SELECT_ONE = _USER + 4
    DB_USER_SELECT_ALL = _USER + 5
    DB_USER_COMPANIES_LINK = _USER + 6
    DB_USER_COMPANIES_UNLINK = _USER + 7
    DB_USER_COMPANIES_SELECT_ALL = _USER + 8
    DB_USER_EMAIL_VERIFY = _USER + 9
    DB_USER_VERIFY = _USER + 10
    #   END_USER

    #   DOCUMENT
    _DOCUMENT = _BASE + 400
    DB_DOCUMENT_CREATE = _DOCUMENT + 1
    DB_DOCUMENT_UPDATE = _DOCUMENT + 2
    DB_DOCUMENT_DELETE = _DOCUMENT + 3
    DB_DOCUMENT_SELECT_ONE = _DOCUMENT + 4
    DB_DOCUMENT_SELECT_ALL = _DOCUMENT + 5
    DB_DOCUMENT_DETAIL_LINE_CREATE = _DOCUMENT + 6
    DB_DOCUMENT_LINE_TAX_CREATE = _DOCUMENT + 7
    DB_DOCUMENT_ADDITIONAL_EMAIL_CREATE = _DOCUMENT + 8
    DB_DOCUMENT_SELECT_BY_COMPANY_AND_TYPE = _DOCUMENT + 9
    DB_DOCUMENT_SELECT_ADDITIONAL_EMAILS_BY_KEY = _DOCUMENT + 10
    DB_DOCUMENT_JOBS = _DOCUMENT + 10

    #   END_DOCUMENT

    #   CABYS
    _CABYS = _BASE + 500
    DB_CABYS_SEARCH_MEDICATION = _CABYS + 6
    DB_CABYS_SEARCH_CODE = _CABYS + 7
    DB_CABYS_SEARCH_SACS = _CABYS + 8
    #   END_CABYS

    #   REGISTRY
    _REGISTRY = _BASE + 600
    DB_REGISTRY_SELECT_ONE = _REGISTRY + 4
    #   END_REGISTRY


class DBAdapterErrorCodes(IntEnum):
    _BASE = 8 * 10
    DBA_CONNECTION = _BASE + 1
    DBA_STATEMENT_EXECUTION = _BASE + 2
    DBA_NON_UNIQUE_OPERATION = _BASE + 3
    DBA_FETCHING = _BASE + 4
    DBA_GENERAL_DATABASE = _BASE + 9


class InternalErrorCodes(IntEnum):
    _BASE = 9 * 100
    INTERNAL_ERROR = _BASE + 1
# END_ENUMS
