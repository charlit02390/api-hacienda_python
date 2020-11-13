"""Module that provides reusable functions for communicating with the database in a generic way. Hopefully...
"""

import json
from enum import Enum
from pymysql import cursors
from pymysql.err import OperationalError, InternalError, DatabaseError
import logging
# todo: config logging, breaking returns into exception throws, documentation

from extensions import mysql
from helpers.errors.enums import DBAdapterErrorCodes
from helpers.errors.exceptions import DatabaseError as IBDatabaseError


class DbAdapterError(IBDatabaseError):
    """Exception thrown when operations on the database fail."""
    status = DBAdapterErrorCodes._BASE
    message_dictionary = {
        DBAdapterErrorCodes.DBA_CONNECTION : ('A problem'
                                              ' occurred when attempting to connect'
                                              ' to the database.'),
        DBAdapterErrorCodes.DBA_STATEMENT_EXECUTION : ('An'
                                                       ' issue was encountered during'
                                                       ' database operations.'),
        DBAdapterErrorCodes.DBA_NON_UNIQUE_OPERATION : ('An'
                                                        ' unintended behavior occured'
                                                        ' during the operation and'
                                                        ' execution was stopped.'),
        DBAdapterErrorCodes.DBA_FETCHING : ('An issue was'
                                            ' encountered when reading data'
                                            ' from the database.'),
        DBAdapterErrorCodes.DBA_GENERAL_DATABASE : ('An issue'
                                                    ' was encountered during'
                                                    ' database operations.')
        }
    default_message = ('An issue was encountered during database'
                       ' operations.')


class NonUniqueResultError(Exception):
    """Exception thrown when an operation on the database
        expected only affected row, but instead returned either
        no rows, or more than one."""
    pass



class FetchType(Enum):
    """
    Enum that specifies how cursors will fetch data from the the
        query given.

    For convenience, each enum has a dictionary value for the
        warning error used in functions.
    
    :FetchType.ONE: Fetches only the first row.
    :FetchType.ALL: Fetches all rows available.
    :FetchType.ALL_UNBUFFERED: Prompts the creation of a
        generator. Should only be used with buffered as False.
    """
    ONE = {'_warning' : 'No data found.'}
    ALL = {'_warning' : 'No matches found.'}
    ALL_UNBUFFERED = {'_warning' : 'No data found.'}


def fetchall_from_proc(procname: str, args: tuple=(),
                       headers: list=None) -> list:
    """
    Fetches all rows from the given database procedure name and
    returns them in a list.

    Optionally, accepts as parameters an arguments tuple and a
    headers list.
    Delegates to _fetch_from_proc

    :param procname: str - The name of the stored procedure to call.
    :param args: [optional] tuple - A tuple that contains the data to
        be sent as the called procedure's parameters.
    :param headers: [optiona] list - A list that contains strings to be
        used as "headers" for the dictionaries produced for each row.
    :returns: list[dict] - A list composed of dictionaries for each row
        fetched from the stored procedure called. The list can be
        empty if no rows were found.
    :raises: pymysql.err.DatabaseError - when a 'DatabaseError'
        is raised during data retrieval or an 'Exception' is raised.
    """
    return _fetch_from_proc(FetchType.ALL, True, procname,
                            args, headers)


def fetchone_from_proc(procname: str, args: tuple=(),
                       headers: list=None):
    """
    Fetches the first row from the given database procedure name
    and returns it in a dictionary.

    Optionally, accepts as parameters an arguments tuple and a
    headers list.
    Delegates to _fetch_from_proc

    :param procname: str - The name of the stored procedure to call.
    :param args: [optional] tuple - A tuple that contains the data to
        be sent as the called procedure's parameters.
    :param headers: [optiona] list - A list that contains strings to be
        used as "headers" for the dictionary produced.
    :returns: dict|None - A dictionary that contains the data fetched
        from the stored procedure called; or None if no data was found.
    :raises: pymysql.err.DatabaseError - when a 'DatabaseError' is
        raised during data retrieval or an 'Exception' is raised.
    """
    return _fetch_from_proc(FetchType.ONE, False, procname,
                            args, headers)
    

def _fetch_from_proc(fetchtype: FetchType, buffered: bool,
                     procname: str, args: tuple=(),
                     headers: list=None):
    """
    Fetches data from the database from the given database
    procedure name.

    This function behaves differently depending on the fetchtype
    and buffered parameters given. Needs some more testing...

    :param fetchtype: FetchType - How the cursor will fetch the data.
        Refer to the FetchType class for more information.
    :param buffered: bool - Determines the type of cursor to use:
        True for buffered cursor, which pulls all the data into memory
            and provides some utility functions not available in an
            unbuffered cursor;
        False for unbuffered, which consumes less memory, but has
            other limitations.
    :param procname: str - The name of the stored procedure to call.
    :param args: [optional] tuple - A tuple that contains the data to be
        sent as the called procedure's parameters.
    :param headers: [optiona] list - A list that contains strings to be
        used as "headers" for the dictionaries produced for each row.
    :returns: dict|list[dict]|gen|None

        - A dictionary if 'FetchType.ONE' was used.
        - A list composed of dictionaries if 'FetchType.ALL' was
          used.
        - A generator object if 'FetchType.ALL_UNBUFFERED' was
          used and "buffered" was set to False.
        - None if no data was found.

    :raises: pymysql.err.DatabaseError - when a 'DatabaseError' is
        raised during data retrieval or an 'Exception' is raised.
    """
    data = [] if fetchtype is FetchType.ALL else None
    conn = connectToMySql()
    try:
        cursortype = None
        if buffered:
            cursortype = cursors.Cursor
        else:
            cursortype = cursors.SSCursor

        with conn.cursor(cursortype) as cursor:
            cursor.callproc(procname, args)
            row_headers = headers or [x[0] for x in cursor.description]
            if fetchtype is FetchType.ALL:
                _resultSet = cursor.fetchall()
                if len(_resultSet) != 0:
                    conn.commit()
                    _data = []
                    for row in _resultSet:
                        _data.append(dict(zip(row_headers,row)))

                    data = _data

            elif fetchtype is FetchType.ONE:
                _resultSet = cursor.fetchone()
                if _resultSet is not None:
                    data = dict(zip(row_headers,_resultSet))

            elif fetchtype is FetchType.ALL_UNBUFFERED \
                and not buffered:
                data = cursor.fetchall_unbuffered()

            # gotta raise an exception for when no proper fetching was done... but... too lazy rn
    except DatabaseError as dbe:
        logging.error(str(dbe)) # todo
        raise DbAdapterError(
            status=DBAdapterErrorCodes.DBA_FETCHING) from dbe

    except Exception as e:
        logging.error(str(e)) # todo
        raise DbAdapterError(
            status=DBAdapterErrorCodes.DBA_GENERAL_DATABASE
            ) from e

    finally:
        conn.close()


    return data


def execute_proc(proc_name: str, args: tuple=(), conn=None,
                 assert_unique: bool=False) -> bool:
    """
    Executes the given procedure on the database.

    Provides support for using an external pymysql connection and
        validating that the query's result affected only one row (for
        PRIMARY/UNIQUE based queries).
    Delegates to _execute

    :param proc_name: str - The procedure name to be executed.
    :param args: [optional] tuple - The arguments to be sent to the
        procedure.
    :param conn: [optional] object - An instance of a PyMySQL
        database connection to get a cursor from.
    :param assert_unique: [optional] bool
    
        - True if the affected rows by the procedure call MUST
          be one(1) - a different value for affected rows will raise
          an exception.
        - False if affected rows doesn't need to be checked.

        Default is False.
    :returns: bool - True when execution completed and no exceptions
        were raised.
    :raises pymysql.err.DatabaseError: when an error occurs.
    """
    return _execute(exec_string=proc_name, args=args,
                    conn=conn, assert_unique=assert_unique, callproc=True)


def execute_sql(sql_statement: str, args: tuple=(), conn=None,
                assert_unique: bool=False) -> bool:
    """
    Executes the provided SQL Statement string on the database

    Provides support for using an external pymysql connection and
        validating that the query's result affected only one row (for
        PRIMARY/UNIQUE based queries).
    Delegates to _execute

    :param sql_statement: str - a query string with SQL Statements.
        %s can be used as placeholder for arguments.
    :param args: [optional] tuple - the arguments to be parsed into
        the query string.
    :param conn: [optional] object - an instance of a PyMySQL
        database connection to get a cursor from.
    :param assert_unique: [optional] bool
    
        - True if the affected rows by the procedure call MUST
          be one(1) - a different value for affected rows will raise
          an exception.
        - False if affected rows doesn't need to be checked.

        Default is False.
    :returns: bool - True when execution completed and no
        exceptions were raised.
    :raises pymysql.err.DatabaseError: when an error occurs.
    """
    return _execute(exec_string=sql_statement, args=args,
                    conn=conn, assert_unique=assert_unique)


def _execute(exec_string:str, args: tuple=(), conn=None,
             assert_unique: bool=False,
             callproc: bool=False) -> bool:
    """
    Executes the given string either as an SQL Statement or as an
        Stored Procedure.

    Provides support for using an external pymysql connection and
        validating that the query's result affected only one row (for
        PRIMARY/UNIQUE based queries).
    Default execution is as an SQL Statement. 'callproc' argument
        can be set to True so 'exec_string' is executed as a Stored
        Procedure.

    :param exec_string: str - A string containing either SQL
        Statements or the name of a Procedure.
    :param args: [optional] tuple - The arguments to be sent to the
        'exec_string'
    :param conn: [optional] object - An instance of a PyMySQL
        database connection to get a cursor from.
    :param assert_unique: [optional] bool
    
        - True if the affectedrows by the procedure call MUST be
          one(1) - a different value for affected rows will raise an
          exception.
        - False if affected rows doesn't need to be checked.

        Default is False.
    :param callproc: [optional] bool - Set to True in order to
        execute 'exec_string' as an Stored Procedure.
        Else, 'exec_string' will be executed as an SQL Statement.
    :returns: bool - True when execution completed and no
        exceptions were raised.
    :raises pymysql.err.DatabaseError: when an error occurs.
    """
    self_managed = False # controls whether we are responsible for committing and closing the connection or if an external manager is in charge of that.

    if conn is None: # if no connection was received, we make our own and we must manage it
        conn = connectToMySql()
        self_managed = True

    try:
        with conn.cursor() as cur:
            if assert_unique:
                affected = -1
                if callproc:
                    cur.callproc(exec_string, args)
                    affected = cur.rowcount
                else:
                    affected = cur.execute(exec_string, args)

                if affected != 1:
                    errmsg = _log_unique_assertion_failure(
                        affected < 1, callproc, exec_string, str(args))
                    if self_managed:
                        conn.rollback()
                    raise NonUniqueResultError(errmsg)
            elif callproc:
                cur.callproc(exec_string, args)
            else:
                cur.execute(exec_string, args)

            if self_managed:
                conn.commit()

    except NonUniqueResultError as nure:
        logging.error(str(nure)) # todo
        if self_managed:
            conn.rollback()
        raise DbAdapterError(
            str(nure),
            status=DBAdapterErrorCodes.DBA_NON_UNIQUE_OPERATION
            ) from nure
    except DatabaseError as dbe:
        logging.error(str(dbe)) # todo
        if self_managed:
            conn.rollback()
        raise DbAdapterError(
            status=DBAdapterErrorCodes.DBA_STATEMENT_EXECUTION
            ) from dbe

    finally:
        if self_managed:
            conn.close()
            conn = None

    return True


def _log_unique_assertion_failure(no_rows_affected: bool,
                                  is_proc: bool, exec_string: str,
                                  args: str) -> str:
    """
    Logs a custom message when 'unique_assertion' failed.

    :param no_rows_affected: bool

        - True if no rows were affected.
        - False if more than one.

    :param is_proc: bool

        - True if assertion failed on a stored procedure.
        - False for SQL Statements.

    :param exec_string: str - the operation that failed the assertion.
    :param args: str - the arguments used in the operation that
        failed assertion.
    :returns: str - the custom message built from the arguments received.
    """

    message_main = ''
    message_reason = ''
    message_detail = ''

    if is_proc:
        message_main = ('Procedure: {} was expected to produce'
                        ' a unique matched registry, but').format(
                            exec_string)
        message_detail = ' | Arguments used: {}'.format(args)
    else:
        message_main = ('The executed SQL Statement was expected'
                        ' to produce a unique matched registry, but')
        message_detail = ' | Statement: {} | Arguments used: {}'.format(
            exec_string, args)

    if no_rows_affected:
        message_reason = ' it yielded no affected rows.'
    else:
        message_reason = ' it yielded more than one(1) affected rows.'

    message = message_main + message_reason + message_detail
    logging.error(message) # todo
    return message


def connectToMySql():
    """
    Returns a PyMySql Connection instance to be used as the
        database connection.

    @todo: contextmanager this

    :returns: a PyMySql Connection instance
    :raises: pymysql.err.DatabaseError - when an error occurs
        during connection to the database.
    """
    conn = None
    try:
        conn =  mysql.connect()
    except (OperationalError, InternalError) as e:
        logging.error(str(e)) # todo
        raise DbAdapterError(
            status=DBAdapterErrorCodes.DBA_CONNECTION) from e
    
    return conn
