import json
from infrastructure import dbadapter as dba


def save_user(id_user, password, name, idrol, idcompanies):
    conn = None
    try:
        conn = dba.connectToMySql()
    except dba.DatabaseError as dbe:
        raise

    try:
        user_proc = 'sp_createUser'
        user_args = (id_user, password, name, idrol)
        try:
            dba.execute_proc(proc_name=user_proc,args=user_args,conn=conn,assert_unique=True)

        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The user couldn't be created.")

        # should prolly move to function or something
        usercom_proc = 'sp_createUser_Company'
        for id in idcompanies:
            try:
                idcompany = id['id']
            except KeyError as ker:
                conn.rollback()
                raise KeyError('Missing property ' + str(ker))
            except TypeError as ter:
                conn.rollback()
                raise TypeError('Expected object with property "id"; instead got: ' + str(ter).rstrip('object is not subscriptable'))

            usercom_args = (id_user, idcompany)            
            try:
                dba.execute_proc(proc_name=usercom_proc,args=usercom_args,conn=conn,assert_unique=True)
            except dba.DatabaseError as dbe:
                conn.rollback()
                raise dba.DatabaseError(str(dbe) + "Couldn't assign the user's companies.")

        conn.commit()
        return True

    finally:
        conn.close()


def get_user_data(id_user):
    user_proc = 'sp_getUserInfo'
    user_args = (id_user,)
    found_user = dba.fetchone_from_proc(procname=user_proc,args=user_args)
    if '_error' in found_user:
        raise dba.DatabaseError("A problem occurred when attempting to obtain the user's data.")
    elif '_warning' in found_user:
        return {'error' : 'The specified user was not found.'}

    try:
        user_companies = get_user_company_data(id_user)
    except dba.DatabaseError as dbe:
        raise

    found_user['companies'] = user_companies
    return found_user


def get_user_company_data(id_user):
    usercoms_proc = 'sp_getUserInfoCompanies'
    usercoms_args = (id_user,)
    companies = dba.fetchall_from_proc(procname=usercoms_proc,args=usercoms_args)
    if isinstance(companies,dict):
        if '_error' in companies:
            raise dba.DatabaseError("A problem occured when attempting to obtain the user's companies.")
        elif '_warning' in companies: # if no companies were found, it's fine to return an empty array. A user could still have no companies assigned.
            companies = []

    return companies


def get_users():
    procedure = 'sp_getUsers'
    return dba.fetchall_from_proc(procname=procedure)


def modify_user(id_user, password, name, idrol, idcompanies):
    conn = None
    try:
        conn = dba.connectToMySql()
    except dba.DatabaseError as dbe:
        raise

    try:
        # clear the user's companies first, so adding the ones received gives the impression of deleting the missing ones and adding new ones
        delcom_proc = 'usp_deleteUser_CompanyByUser'
        delcom_args = (id_user,)
        try:
            dba.execute_proc(proc_name=delcom_proc,args=delcom_args,conn=conn)
        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The user couldn't be updated.")

        # update the user
        user_proc = 'sp_ModifyUser'
        user_args = (id_user, password, name, idrol)
        try:
            dba.execute_proc(proc_name=user_proc,args=user_args,conn=conn, assert_unique=True)
        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The user's data couldn't be updated.")

        # add the companies received
        usercom_proc = 'sp_createUser_Company'
        for id in idcompanies:
            try:
                idcompany = id['id']
            except KeyError as ker:
                conn.rollback()
                raise KeyError('Missing property: ' + str(ker))
            except TypeError as ter:
                conn.rollback()
                raise TypeError('Expected object with property "id"; instead got: ' + str(ter).rstrip('object is not subscriptable'))

            usercom_args = (id_user, idcompany)
            try:
                dba.execute_proc(proc_name=usercom_proc,args=usercom_args,conn=conn, assert_unique=True)
            except dba.DatabaseError as dbe:
                conn.rollback()
                raise dba.DatabaseError(str(dbe) + " The user's companies couldn't be updated.")

        conn.commit()
        return True
    finally:
        conn.close()


def verify_email(id_user):
    procedure = 'sp_getUserInfo'
    args = (id_user,)
    user = dba.fetchone_from_proc(procname=procedure,args=args)
    if '_error' in user:
        raise dba.DatabaseError("A problem occured when attempting to verify the user by their email.") # ?
    if '_warning' in user:
        return False
    else:
        return True


def verify_user_company(id_user,idcompany):
    procedure = 'sp_getUserCompany_info'
    args = (id_user, idcompany)
    usercom = dba.fetchone_from_proc(procname=procedure,args=args)
    if '_error' in usercom:
        raise dba.DatabaseError("A problem occured when attempting to verify if the company belongs to the user.") # ?
    if '_warning' in usercom:
        return False
    else:
        return True


def delete_user_data(id_user):
    procedure = 'sp_deleteUser'
    args = (id_user,)
    try:
        dba.execute_proc(proc_name=procedure,args=args,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The user couldn't be deleted.")

    return {'message' : 'The user has been deleted successfully.'}


def delete_user_company(id_user,ids_company): # thinking of scraping this... but, whatevs
    conn = None
    try:
        conn = dba.connectToMySql()
    except dba.DatabaseError as dbe:
        raise

    try:
        procedure = 'sp_deleteUserCompany'
        for com_id in ids_company:
            args = (id_user, com_id)
            try:
                dba.execute_proc(proc_name=procedure,args=args,conn=conn,assert_unique=True)
            except dba.DatabaseError as dbe:
                conn.rollback()
                raise dba.DatabaseError(str(dbe) + " Couldn't dissociate the company from the user.")

        conn.commit()
        return True
    finally:
        conn.close()


def check_user(email, password):
    procedure = 'sp_CheckUser'
    args = (email,password)
    return dba.fetchone_from_proc(procname=procedure,args=args)
