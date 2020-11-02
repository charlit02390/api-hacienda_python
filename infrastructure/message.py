
from pymysql.connections import Connection

from infrastructure import dbadapter as dba
from helpers.entities.messages import RecipientMessage
from helpers.errors.enums import DBErrorCodes
from helpers.errors.exceptions import DatabaseError

def insert(company_id: str, message: RecipientMessage,
           encoded_xml: bytes, status: str, issuer_email: str = None,
           connection: Connection = None):
    procedure = 'usp_insert_message'
    args = (company_id, message.key, message.issuerIDN.number,
            message.issuerIDN.type, message.issueDate,
            message.code, message.recipientIDN.number,
            message.recipientSequenceNumber, encoded_xml, status,
            issuer_email)

    try:
        dba.execute_proc(proc_name=procedure, args=args,
                         conn=connection, assert_unique=True)

    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                            status=DBErrorCodes.DB_MESSAGE_CREATE) from dbae

    return True


def update_from_answer(company_id: str, message_key: str,
                       encoded_answer_xml: bytes, status: str,
                       answer_date: str, connection: Connection = None):
    procedure = 'usp_updateFromAnswer_message'
    args = (company_id, message_key, encoded_answer_xml,
            status, answer_date)

    try:
        dba.execute_proc(proc_name=procedure, args=args,
                         conn=connection, assert_unique=True)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                            status=DBErrorCodes.DB_MESSAGE_UPDATE_ANSWER) from dbae

    return True


def select(key_mh: str):
    procedure = 'usp_select_message'
    args = (key_mh,)
    try:
        return dba.fetchone_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_MESSAGE_SELECT_ONE) from dbae


def select_by_company(company_user: str, limit: int = None):
    procedure = 'usp_selectByCompany_message'
    args = (company_user, limit)
    try:
        return dba.fetchone_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_MESSAGE_SELECT_BY_COMPANY)


def select_by_status(status: str, company_user: str = None,
                     limit: int = 20):
    procedure = 'usp_selectByStatus_message'
    args = (status, company_user, limit)
    try:
        return dba.fetchall_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_MESSAGE_SELECT_BY_STATUS) from dbae


def select_by_code(code: str, company_user: str = None,
                   limit: int = None):
    procedure = 'usp_selectByCode_message'
    args = (code, company_user, limit)
    try:
        return dba.fetchall_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_MESSAGE_SELECT_BY_CODE) from dbae


def select_by_issuer_idn(issuer_idn: str, company_user: str = None,
                         limit: int = None):
    procedure = 'usp_selectByIssuerIDN_message'
    args = (issuer_idn, company_user, limit)
    try:
        return dba.fetchall_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_MESSAGE_SELECT_BY_ISSUER_IDN) from dbae
