"""
Module with numeric types that can be used as validation
agents.
"""
from decimal import Decimal, ROUND_HALF_UP, Context, Inexact


class DecimalMoney(Decimal):
    """
    decimal.Decimal implementation that validates the given
    string value to Hacienda's DecimalMoney XSD type.
    """
    _MIN = 0
    _MAX = 9999999999999.99999
    _DECIMALS = 5
    _ROUNDING = ROUND_HALF_UP
    _EXP = Decimal(10) ** (abs(_DECIMALS) * -1)

    def __new__(cls, *args, **kwargs):
        _d = super().__new__(cls, *args, **kwargs)
        if _d < cls._MIN:
            raise ValueError(('Value: {} is under the specified'
                              ' minimum of: {}'.format(str(_d),
                                                       str(cls._MIN))))
        if _d > cls._MAX:
            raise ValueError(('Value: {} is over the specified'
                             ' maximum of: ').format(str(_d),
                                                     str(cls._MAX)))

        try:
            _d = _d.quantize(cls._EXP,
                             rounding=cls._ROUNDING,
                             context=Context(traps=[Inexact]))
        except Inexact:
            raise ValueError(('Value: {} exceeds the decimal'
                              ' digits limit of: {}').format(str(_d),
                                                             str(cls._DECIMALS)))
        return _d

    @classmethod
    def mul(cls, x, y):
        return (x * y).quantize(cls._EXP, cls._ROUNDING)

    @classmethod
    def div(cls, x, y):
        return (x / y).quantize(cls._EXP, cls._ROUNDING)
