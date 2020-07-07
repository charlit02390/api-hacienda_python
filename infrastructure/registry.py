"""Module for manipulating data for table registrocivil in the database
"""
from infrastructure import dbadapter as dbadp


def get_person(id: str):
	"""
	Gets the information of a person from the database using the given id.

	:param id: str - The unique identification number for the person to find.
	:returns: dict - A dictionary, either with obtained data, or warning/error info.
	"""
	procname = 'usp_obtenerpersona_registrocivil'
	return dbadp.fetchone_from_proc(procname, (id,))
