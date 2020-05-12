import json
from extensions import mysql


def get_document(key_mh):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getDocumentByKey', (key_mh,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            return json_data
        else:
            return {'error': 'Error: Not get information of the document'}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()


def get_documents(company_id, state):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getDocumentByCompany', (company_id, state))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return True
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def get_documents(state):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getDocuments', state)
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return True
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def get_documentsreport(company_id, document_type):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_getDocumentsReport', (company_id, document_type,))
        row_headers = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        if len(data) is not 0:
            conn.commit()
            json_data = []
            for row in data:
                json_data.append(dict(zip(row_headers, row)))
            return json_data
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def save_document(company_id, key_mh, sign_xml, status, date, document_type, receiver,
                  total_document, total_taxed, pdf, email, email_costs):
    try:
        if receiver is not None:
            receiver_type = receiver['tipoIdentificacion']
            receiver_dni = receiver['numeroIdentificacion']
        else:
            receiver_type = None
            receiver_dni = None
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_saveDocument', (company_id, key_mh, sign_xml, status, date, document_type,receiver_type,
                                            receiver_dni, total_document, total_taxed, pdf, email, email_costs))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return True
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def update_document(company_id, key_mh, answer_xml, status, date):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_updateDocument', (company_id, key_mh, answer_xml, status, date))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return True
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def save_document_line_info(id_company, line_number, quantity, unity
                            , detail, unit_price, net_tax, total_line, key_mh):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createDocumentLineInfo', (id_company, line_number, quantity, unity
                                                      , detail, unit_price, net_tax, total_line, key_mh))
        data = cursor.rowcount
        if data != 0:
            conn.commit()
            return True
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def save_document_line_taxes(id_company, line_number, rate_code, code, rate, amount, key_mh):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_createDocumentTaxInfo', (id_company, line_number, rate_code
                                                     , code, rate, amount, key_mh))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return True
        else:
            return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()