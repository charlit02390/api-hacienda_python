import json
from infrastructure import dbadapter as dba
from helpers.errors.enums import DBErrorCodes
from helpers.errors.exceptions import DatabaseError


def save_company_smtp(host, user, password, port,
                      encrypt_type, id_company, sender):
    procedure = 'sp_createSmtpData'
    args = (host, user, password, port,
            encrypt_type, id_company, sender)
    try:
        dba.execute_proc(proc_name=procedure,
                         args=args,assert_unique=True)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                            status=DBErrorCodes.DB_COMPANY_SMTP_CREATE) from dbae

    return True



def modify_company_smtp(host, password, user, port,
                        encrypt_type, id_company, sender):
    procedure = 'sp_ModifyCompanySmtp'
    args = (host, password, user, port,
            encrypt_type, id_company, sender)
    try:
        dba.execute_proc(proc_name=procedure, args=args,
                         assert_unique=True)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                                status=DBErrorCodes.DB_COMPANY_SMTP_UPDATE) from dbae

    return True



def delete_company_smtp(id_company):
    procedure = 'sp_deleteCompanySmtp'
    args = (id_company,)
    try:
        dba.execute_proc(proc_name=procedure, args=args,
                         assert_unique=True)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                                status=DBErrorCodes.DB_COMPANY_SMTP_DELETE) from dbae

    return True



def get_company_smtp(id_company):
    procedure = 'sp_getCompanySmtpInfo'
    args = (id_company,)
    try:
        return dba.fetchone_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_COMPANY_SMTP_SELECT_ONE) from dbae



def verify_company_smtp(company_user):
    procedure = 'sp_getCompanySmtpInfo'
    args = (company_user,)
    try:
        smtp = dba.fetchone_from_proc(procname=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_COMPANY_SMTP_VERIFY) from dbae
    if not smtp:
        return False
    else:
        return True
