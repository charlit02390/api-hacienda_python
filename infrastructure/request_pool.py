from infrastructure import dbadapter as dba


def spend(amount: int = 1):
    try:
        procedure = 'usp_requestpool_spend'
        args = (amount,)
        success = dba.fetchone_from_proc(procname=procedure, args=args)
        if success is None:
            return False  # raise exception => BadDBConfig?
        else:
            return success['success']
    except dba.DbAdapterError as dbae:
        pass


def reset_interval(connection=None):
    try:
        procedure = 'usp_requestpool_resetInterval'
        dba.execute_proc(proc_name=procedure, conn=connection)
    except dba.DbAdapterError as dbae:
        pass


def set_sleep(seconds: int, connection=None):
    try:
        procedure = 'usp_requestpool_setSleep'
        args = (seconds,)
        dba.execute_proc(proc_name=procedure, args=args, conn=connection)
    except dba.DbAdapterError as dbae:
        pass


def is_sleeping():
    try:
        procedure = 'usp_requestpool_isSleeping'
        sleeping = dba.fetchone_from_proc(procname=procedure)
        if sleeping is None:
            return True  # raise exception => BadDBConfig?
        else:
            return sleeping['isSleeping']
    except dba.DbAdapterError as dbae:
        pass
