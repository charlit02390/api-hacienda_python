from collections import OrderedDict
from abc import ABC, abstractmethod

from lxml import etree

from .numerics import DecimalMoney
from .strings import IDN

class Message(ABC):
    """
    Abstract Implementation for an Hacienda Message.
    """
    _XML_ROOT_TAG = 'Mensaje'
    _XML_TAG_MAP = OrderedDict({
        'key': 'Clave',
        'code': 'Mensaje',
        'detail': 'DetalleMensaje',
        'taxTotalAmount': 'MontoTotalImpuesto',
        'invoiceTotalAmount': 'TotalFactura'
        })
    _XML_HACIENDA_NAMESPACE = ''
    _XML_HACIENDA_SCHEMA_LOCATION = ''
    _XMLNS_DS = 'http://www.w3.org/2000/09/xmldsig#'
    _XMLNS_XSD = 'http://www.w3.org/2001/XMLSchema'
    _XMLNS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
    
    key: str
    code: int
    detail: str
    taxTotalAmount: DecimalMoney
    invoiceTotalAmount: DecimalMoney

    def __init__(self, *args, **kwargs):
        self._order_tag_map()

    def toXml(self):
        nsmap = {
            None: self._XML_HACIENDA_NAMESPACE,
            'ds': self._XMLNS_DS,
            'xsd': self._XMLNS_XSD,
            'xsi': self._XMLNS_XSI
            }

        schemaLocation_attr = etree.QName(self._XMLNS_XSI,
                                          'schemaLocation')

        root = etree.Element(self._XML_ROOT_TAG,
                             attrib={
                                 schemaLocation_attr: self._XML_HACIENDA_SCHEMA_LOCATION
                                 },
                             nsmap=nsmap)

        tagmap = self._XML_TAG_MAP
        for prop, tag in tagmap.items():
            propData = self.__dict__.get(prop)
            if propData:
                child = etree.SubElement(root, tag)
                child.text = str(propData)

        return etree.tostring(root,
                              encoding='UTF-8',
                              pretty_print=True,
                              xml_declaration=True)

    @abstractmethod
    def _order_tag_map(self):
        raise NotImplementedError(('func _order_tag_map'
                                   ' is not implemented.'))


class RecipientMessage(Message):
    _XML_ROOT_TAG = 'MensajeReceptor'
    _XML_HACIENDA_NAMESPACE = 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/mensajeReceptor'
    _XML_HACIENDA_SCHEMA_LOCATION = 'https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/MensajeReceptor_V4.3.xsd'    
    issuerIDN: IDN
    issueDate: str
    activityCode: str
    taxTerms: str
    accreditTotalTaxAmount: DecimalMoney
    applicableExpenseTotalAmount: DecimalMoney
    recipientIDN: IDN
    recipientSequenceNumber: str

    def __init__(self):
        self._XML_TAG_MAP.update({
            'issuerIDN': 'NumeroCedulaEmisor',
            'issueDate': 'FechaEmisionDoc',
            'activityCode': 'CodigoActividad',
            'taxTerms': 'CondicionImpuesto',
            'accreditTotalTaxAmount': 'MontoTotalImpuestoAcreditar',
            'applicableExpenseTotalAmount': 'MontoTotalDeGastoAplicable',
            'recipientIDN': 'NumeroCedulaReceptor',
            'recipientSequenceNumber': 'NumeroConsecutivoReceptor'
            })
        super().__init__()

    def _order_tag_map(self):
        key_order = ('key', 'issuerIDN', 'issueDate', 'code',
                     'detail', 'activityCode', 'taxTerms',
                     'accreditTotalTaxAmount',
                     'applicableExpenseTotalAmount', 'taxTotalAmount',
                     'invoiceTotalAmount', 'recipientIDN',
                     'recipientSequenceNumber')

        for key in key_order:
            self._XML_TAG_MAP.move_to_end(key)

