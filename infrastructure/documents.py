import json
from infrastructure import dbadapter as dba


def get_document(key_mh):
    procedure = 'sp_getDocumentByKey'
    args = (key_mh,)
    return dba.fetchone_from_proc(procname=procedure,args=args)


def get_documents(company_id, state): # wtf is this?
    procedure = 'sp_getDocumentByCompany'
    args = (company_id, state)
    return dba.fetchall_from_proc(procname=procedure,args=args)


def get_documents(state): # and this??? 
    procedure = 'sp_getDocuments'
    args = (state,)
    docs = dba.fetchall_from_proc(procname=procedure,args=args)
    if isinstance(docs, dict):
        if '_error' in docs:
            raise dba.DatabaseError('A problem occurred when attempting to fetch documents by their state.')
        elif '_warning' in docs:
            return []

    return True


def get_documentsreport(company_id, document_type):
    procedure = 'sp_getDocumentsReport'
    args = (company_id, document_type)
    return dba.fetchall_from_proc(procname=procedure,args=args)

def get_additional_emails(key_mh):
    procedure = 'usp_selectByDocKey_documentxemail'
    args = (key_mh,)
    return dba.fetchall_from_proc(procname=procedure, args=args)

def save_document(company_id, key_mh, sign_xml, status, date, document_type, receiver,
                  total_document, total_taxed, pdf, email, email_costs, connection=None):
    receiver_type = None
    receiver_dni = None
    if receiver is not None:
        try:
            receiver_type = receiver['tipoIdentificacion']
            receiver_dni = receiver['numeroIdentificacion']
        except KeyError as ker:
            raise KeyError('Missing property: ' + str(ker))

    procedure = 'sp_saveDocument'
    args = (company_id, key_mh, sign_xml, status, date, document_type,receiver_type,
                                            receiver_dni, total_document, total_taxed, pdf, email, email_costs)

    try:
        dba.execute_proc(proc_name=procedure, args=args,conn=connection,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The document couldn't be saved.")

    return True


def update_document(company_id, key_mh, answer_xml, status, date):
    procedure = 'sp_updateDocument'
    args = (company_id, key_mh, answer_xml, status, date)
    try:
        dba.execute_proc(proc_name=procedure,args=args,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The document couldn't be updated.")

    return True


def save_document_line_info(id_company, line_number, quantity, unity
                            , detail, unit_price, net_tax, total_line, key_mh, connection=None):
    procedure = 'sp_createDocumentLineInfo'
    args = (id_company, line_number, quantity, unity
                                                      , detail, unit_price, net_tax, total_line, key_mh)
    try:
        dba.execute_proc(proc_name=procedure,args=args,conn=connection,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " A detail line for the document couldn't be saved, so the operation stopped.")

    return True


def save_document_line_taxes(id_company, line_number, rate_code, code, rate, amount, key_mh, connection=None):
    procedure = 'sp_createDocumentTaxInfo'
    args = (id_company, line_number, rate_code
                                                     , code, rate, amount, key_mh)
    try:
        dba.execute_proc(proc_name=procedure, args=args, conn=connection,assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " The tax information for the document couldn't be saved, so the operation stopped.")

    return True

def save_document_additional_email(key_mh, email, connection=None):
    procedure = 'usp_insert_documentxemail'
    args = (key_mh, email)
    try:
        dba.execute_proc(proc_name=procedure, args=args, conn=connection, assert_unique=True)
    except dba.DatabaseError as dbe:
        raise dba.DatabaseError(str(dbe) + " A problem occurred when processing the additional emails provided.")

    return True
