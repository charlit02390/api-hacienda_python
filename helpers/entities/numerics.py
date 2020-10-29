
from decimal import Decimal, ROUND_HALF_UP, Context, Inexact


class DecimalMoney(Decimal):
    _MIN = 0
    _MAX = 9999999999999.99999
    _DECIMALS = 5
    _ROUNDING = ROUND_HALF_UP
    _EXP = Decimal(10) ** (abs(_DECIMALS) * -1)

    def __new__(cls, *args, **kwargs):
        _d = super().__new__(cls, *args, **kwargs)
        if _d < cls._MIN:
            raise ValueError('Value: ' + str(_d) + ' is under the specified minimum of: ' + str(cls._MIN))
        if _d > cls._MAX:
            raise ValueError('Value: ' + str(_d) + ' is over the specified maximum of: ' + str(cls._MAX))

        try:
            _d = _d.quantize(cls._EXP, rounding=cls._ROUNDING, context=Context(traps=[Inexact]))
        except Inexact:
            raise ValueError('Value: ' + str(_d) + ' exceeds the decimal digits limit of: ' + str(cls._DECIMALS))
        return _d

