import json
import base64
from infrastructure import dbadapter as dba


def create_company(company_user, name, tradename, type_identification, dni, state, county, district, neighbor, address,
                   phone_code, phone, email, activity_code, is_active, user_mh, pass_mh, signature, logo, pin_sig, env,
                   expiration_date):
    conn = None
    try:
        conn = dba.connectToMySql()
    except dba.DatabaseError as dbe:
        raise

    try: 
        comp_proc = 'sp_createCompany'
        comp_args = (company_user, name, tradename, type_identification, dni, state,
                                                 county, district, neighbor, address, phone_code, phone, email,
                                                 activity_code, is_active)
        try:
            dba.execute_proc(proc_name=comp_proc, args=comp_args,conn=conn,assert_unique=True)

        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The company couldn't be created.")

        mh_proc = 'sp_saveMHInfo'
        mh_args = (user_mh, pass_mh, signature, logo, pin_sig, company_user, env,
                                              expiration_date)
        try:
            dba.execute_proc(proc_name=mh_proc, args=mh_args, conn=conn, assert_unique=True)

        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The company's Hacienda data couldn't be saved.")

        conn.commit()
        return True

    finally:
        conn.close()
   



def modify_company(company_user, name, tradename, type_identification, dni, state, county, district, neighbor, address,
                   phone_code, phone, email, activity_code, is_active, user_mh, pass_mh, signature, logo, pin_sig, env,
                   expiration_date):
    conn = None
    try:
        conn = dba.connectToMySql()
    except dba.DatabaseError as dbe:
        raise

    try: 
        comp_proc = 'sp_ModifyCompany'
        comp_args = (company_user, name, tradename, type_identification, dni, state,
                                             county, district, neighbor, address, phone_code, phone, email,
                                             activity_code, is_active)
        try:
            dba.execute_proc(proc_name=comp_proc, args=comp_args,conn=conn,assert_unique=True)

        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The company couldn't be created.")


        # in case the mh_info is missing for a company, we should be able to add new info to it.
        # consider changing this procedure to one less intensive.
        mh_info = dba.fetchone_from_proc('sp_getMHInfo',(company_user,))
        if '_error' in mh_info:
            conn.rollback()
            raise dba.DatabaseError("A problem occurred in the database and the company couldn't be created.")
        elif '_warning' in mh_info: # if no info, add new info
            mh_proc = 'sp_saveMHInfo'
        else: # else, update it
            mh_proc = 'sp_modifyMHInfo'

        mh_args = (user_mh, pass_mh, signature, logo,
                                            pin_sig, company_user, env, expiration_date)
        try:
            dba.execute_proc(proc_name=mh_proc, args=mh_args, conn=conn, assert_unique=True)

        except dba.DatabaseError as dbe:
            conn.rollback()
            raise dba.DatabaseError(str(dbe) + " The company's Hacienda data couldn't be saved.")

        conn.commit()
        return True

    finally:
        conn.close()


def verify_company(company_user):
    procedure = 'sp_getCompanyInfo'
    args = (company_user,)
    company = dba.fetchone_from_proc(procname=procedure, args=args)
    result = None
    if '_error' in company:
        raise dba.DatabaseError('A problem occured when trying to verify the company.')
    elif '_warning' in company:
        result = False
    else:
        result = True

    return result


def get_company_data(company_user):
    procedure = 'sp_getCompanyInfo'
    args = (company_user,)
    return dba.fetchone_from_proc(procname=procedure, args=args)


def get_companies():
    procedure = 'sp_getCompanies'
    return dba.fetchall_from_proc(procname=procedure)


def get_sign_data(company_user):
    procedure = 'sp_getSignCompany'
    args = (company_user,)
    return dba.fetchone_from_proc(procname=procedure,args=args)


def get_logo_data(company_user):
    procedure = 'sp_getLogoCompany'
    args = (company_user,)
    return dba.fetchone_from_proc(procname=procedure, args=args)


def delete_company_data(company_user):
    procedure = 'sp_deleteCompany'
    args = (company_user,)
    try:
        dba.execute_proc(proc_name=procedure,args=args,assert_unique=True)
        return {'message':'The company has been succesfully deleted.'}
    except dba.DatabaseError as dbe:
        return {'error' : str(dbe) + " The company couldn't be deleted."}
