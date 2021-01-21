"""
Module with utilities for string types
"""
from abc import ABC, abstractmethod
from enum import Enum
from re import sub as regex_sub


class IDNType(Enum): # valid Hacienda IDNTypes
    PID = '01'
    GID = '02'
    DIMEX = '03'
    NITE = '04'


class IDN(ABC, object):
    """
    Abstract implementation for IDN strings.
    Validates the given string to it's derived clases'
    constraints and returns a proper instance.
    """
    class IDNTypeNotFound(Exception):
        """
        Exception raised when the specified IDNType to
        instantiate has not been defined.
        """

    __class_registry = {}

    _IDN_TYPE: IDNType
    _TARGET_LENGTH = 0

    number: str

    @property
    def type(self):
        return self._IDN_TYPE.value

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__class_registry[cls._IDN_TYPE] = cls
   
    def __new__(cls, subclass_type, number):
        subclass = cls.__class_registry.get(subclass_type)
        if subclass:
            instance = object.__new__(subclass)
            instance.number = number
            subclass.validate_idn(instance)
            return instance
        else:
            raise IDN.IDNTypeNotFound(('No class'
                                       ' found for type {}'
                                      ).format(subclass_type))

    @classmethod
    def validate_idn(cls, idn):
        target_length = cls._TARGET_LENGTH \
            if isinstance(cls._TARGET_LENGTH, tuple) \
            else (cls._TARGET_LENGTH,) 
        if len(idn.number) not in target_length:
            raise ValueError(('{} Number "{}" length'
                              ' must be of {} characters.'
                             ).format(cls._IDN_TYPE.name,
                                     idn.number,
                                     cls._TARGET_LENGTH))

        strippedIdn = idn.number.lstrip('0')
        if len(strippedIdn) not in target_length:
            raise ValueError(("{} Number \"{}\" has"
                              " leading zeroes. Stripping"
                              " them makes it's length not"
                              " match the required length of"
                              " {} characters."
                             ).format(cls._IDN_TYPE.name,
                                     idn.number,
                                     cls._TARGET_LENGTH))

        onlyDigitsIdn = regex_sub(r'\D', '', idn.number)
        if len(onlyDigitsIdn) not in target_length:
            raise ValueError(("{} Number \"{}\" has"
                              " characters other than digits."
                              " Stripping them makes it's"
                              " length not match the required"
                              " length of {} characters."
                             ).format(cls._IDN_TYPE.name,
                                     idn.number,
                                     cls._TARGET_LENGTH))

        return True

    def __str__(self):
        return self.number


class PID(IDN):
    _IDN_TYPE = IDNType.PID
    _TARGET_LENGTH = 9

class GID(IDN):
    _IDN_TYPE = IDNType.GID
    _TARGET_LENGTH = 10

class DIMEX(IDN):
    _IDN_TYPE = IDNType.DIMEX
    _TARGET_LENGTH = (11, 12)

class NITE(IDN):
    _IDN_TYPE = IDNType.NITE
    _TARGET_LENGTH = 10
