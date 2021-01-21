import json
from infrastructure import dbadapter as dba
from helpers.errors.enums import DBErrorCodes, InputErrorCodes
from helpers.errors.exceptions import DatabaseError, InputError


def save_user(id_user, password, name, idrol, idcompanies):
    conn = dba.connectToMySql()

    try:
        user_proc = 'sp_createUser'
        user_args = (id_user, password, name, idrol)
        try:
            dba.execute_proc(proc_name=user_proc,args=user_args,conn=conn,assert_unique=True)

        except dba.DbAdapterError as dbae:
            conn.rollback()
            raise DatabaseError(dbae.get_message(),
                                    status=DBErrorCodes.DB_USER_CREATE) from dbae

        # should prolly move to function or something
        usercom_proc = 'sp_createUser_Company'
        for cid in idcompanies:
            if isinstance(cid, (str,int)):
                idcompany = cid
            elif isinstance(cid, dict) and 'id' in cid:
                idcompany = cid['id']
            else:
                conn.rollback()
                raise InputError('companies array',
                                 'expected either a string, an int or an object with property "id" : string, int',
                                 status=InputErrorCodes.INCORRECT_TYPE)

            usercom_args = (id_user, idcompany)            
            try:
                dba.execute_proc(proc_name=usercom_proc,args=usercom_args,conn=conn,assert_unique=True)
            except dba.DbAdapterError as dbae:
                conn.rollback()
                raise DatabaseError(dbae.get_message(),
                                        DBErrorCodes.DB_USER_COMPANIES_LINK) from dbae

        conn.commit()
        return True

    finally:
        conn.close()



def modify_user(id_user, password, name, idrol, idcompanies):
    conn = dba.connectToMySql()

    try:
        # clear the user's companies first, so adding the ones received gives the impression of deleting the missing ones and adding new ones
        delcom_proc = 'usp_deleteUser_CompanyByUser'
        delcom_args = (id_user,)
        try:
            dba.execute_proc(proc_name=delcom_proc,args=delcom_args,
                             conn=conn)
        except dba.DbAdapterError as dbae:
            conn.rollback()
            raise DatabaseError(dbae.get_message(),
                                    status=DBErrorCodes.DB_USER_COMPANIES_UNLINK) from dbae

        # update the user
        user_proc = 'sp_ModifyUser'
        user_args = (id_user, password, name, idrol)
        try:
            dba.execute_proc(proc_name=user_proc,args=user_args,
                             conn=conn, assert_unique=True)
        except dba.DbAdapterError as dbae:
            conn.rollback()
            raise DatabaseError(dbae.get_message(),
                                    status=DBErrorCodes.DB_USER_UPDATE) from dbae

        # add the companies received
        usercom_proc = 'sp_createUser_Company'
        for cid in idcompanies:
            if isinstance(cid, (str,int)):
                idcompany = cid
            elif isinstance(cid, dict) and 'id' in cid:
                idcompany = cid['id']
            else:
                conn.rollback()
                raise InputError('companies array',
                                 'expected either a string, an int or an object with property "id" : string, int',
                                 status=InputErrorCodes.INCORRECT_TYPE)

            usercom_args = (id_user, idcompany)
            try:
                dba.execute_proc(proc_name=usercom_proc,args=usercom_args,conn=conn, assert_unique=True)
            except dba.DbAdapterError as dbae:
                conn.rollback()
                raise DatabaseError(dbae.get_message(),
                                        status=DBErrorCodes.DB_USER_COMPANIES_LINK) from dbae

        conn.commit()
        return True
    finally:
        conn.close()



def delete_user_data(id_user):
    procedure = 'sp_deleteUser'
    args = (id_user,)
    try:
        dba.execute_proc(proc_name=procedure,args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                                status=DBErrorCodes.DB_USER_DELETE) from dbae

    return True



def delete_user_companies(id_user):
    procedure = 'sp_deleteUserCompany'
    args = (id_user,)
    try:
        dba.execute_proc(proc_name=procedure, args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(dbae.get_message(),
                                status=DBErrorCodes.DB_USER_COMPANIES_UNLINK) from dbae

    return True



def get_user_data(id_user):
    user_proc = 'sp_getUserInfo'
    user_args = (id_user,)
    try:
        found_user = dba.fetchone_from_proc(procname=user_proc,args=user_args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_USER_SELECT_ONE) from dbae
    if not found_user:
        return found_user # or None

    user_companies = get_user_company_data(id_user)

    found_user['companies'] = user_companies
    return found_user



def get_user_company_data(id_user):
    usercoms_proc = 'sp_getUserInfoCompanies'
    usercoms_args = (id_user,)
    try:
        companies = dba.fetchall_from_proc(procname=usercoms_proc,args=usercoms_args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_USER_COMPANIES_SELECT_ALL) from dbae

    return companies



def get_users():
    procedure = 'sp_getUsers'
    try:
        return dba.fetchall_from_proc(procname=procedure)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_USER_SELECT_ALL) from dbae



def verify_email(id_user):
    procedure = 'sp_getUserInfo'
    args = (id_user,)
    try:
        user = dba.fetchone_from_proc(procname=procedure,args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_USER_EMAIL_VERIFY) from dbae

    if not user:
        return False
    else:
        return True



def check_user(email, password):
    procedure = 'sp_CheckUser'
    args = (email,password)
    try:
        return dba.fetchone_from_proc(procname=procedure,args=args)
    except dba.DbAdapterError as dbae:
        raise DatabaseError(status=DBErrorCodes.DB_USER_VERIFY) from dbae


def verify_user_company(id_user,idcompany): # not used. MARKED FOR DEATH
    procedure = 'sp_getUserCompany_info'
    args = (id_user, idcompany)
    usercom = dba.fetchone_from_proc(procname=procedure,args=args)
    if '_error' in usercom:
        raise dba.DbAdapterError("A problem occured when attempting to verify if the company belongs to the user.") # ?
    if '_warning' in usercom:
        return False
    else:
        return True
