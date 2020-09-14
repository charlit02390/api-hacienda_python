import json
from infrastructure import dbadapter as dba


def save_company_smtp(host, user, password, port, encrypt_type, id_company):
    procedure = 'sp_createSmtpData'
    args = (host,user,password,port,encrypt_type,id_company)
    try:
        dba.execute_proc(proc_name=procedure,args=args,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The company's SMTP couldn't be saved")

    return True


def get_company_smtp(id_company):
    procedure = 'sp_getCompanySmtpInfo'
    args = (id_company,)
    return dba.fetchone_from_proc(procname=procedure,args=args)


def delete_company_smtp(id_company):
    procedure = 'sp_deleteCompanySmtp'
    args = (id_company,)
    try:
        dba.execute_proc(proc_name=procedure, args=args,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The company's SMTP couldn't be deleted.")

    return {'message' : "The company's SMTP has been deleted."}


def modify_company_smtp(host, password, user, port, encrypt_type, id_company):
    procedure = 'sp_ModifyCompanySmtp'
    args = (host, password, user, port, encrypt_type, id_company)
    try:
        dba.execute_proc(proc_name=procedure,args=args,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The company's SMTP couldn't be updated.")

    return {'message' : "The company's SMTP was successfully updated."}


def verify_company_smtp(company_user):
    procedure = 'sp_getCompanySmtpInfo'
    args = (company_user,)
    smtp = dba.fetchone_from_proc(procname=procedure,args=args)
    if '_error' in smtp:
        raise dba.DatabaseError('A problem occurred when trying to verify the SMTP')
    elif '_warning' in smtp:
        return False
    else:
        return True
