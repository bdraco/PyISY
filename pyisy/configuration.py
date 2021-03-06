"""ISY Configuration Lookup."""
from xml.dom import minidom

from .constants import (
    ATTR_DESC,
    ATTR_ID,
    TAG_FEATURE,
    TAG_FIRMWARE,
    TAG_INSTALLED,
    XML_TRUE,
)
from .helpers import value_from_xml


class Configuration(dict):
    """
    ISY Configuration class.

    DESCRIPTION:
        This class handles the ISY configuration.

    USAGE:
        This object may be used in a similar way as a
        dictionary with the either module names or ids
        being used as keys and a boolean indicating
        whether the module is installed will be
        returned. With the exception of 'firmware' and 'uuid',
        which will return their respective values.

    PARAMETERS:
        Portal Integration - Check-it.ca
        Gas Meter
        SEP ESP
        Water Meter
        Z-Wave
        RCS Zigbee Device Support
        Irrigation/ETo Module
        Electricity Monitor
        AMI Electricity Meter
        URL
        A10/X10 for INSTEON
        Portal Integration - GreenNet.com
        Networking Module
        OpenADR
        Current Cost Meter
        Weather Information
        Broadband SEP Device
        Portal Integration - BestBuy.com
        Elk Security System
        Portal Integration - MobiLinc
        NorthWrite NOC Module

    EXAMPLE:
        >>> configuration['Networking Module']
        True
        >>> configuration['21040']
        True

    ATTRIBUTES:
        isy: The ISY device class

    """

    def __init__(self, isy, xml=None):
        """
        Initialize configuration class.

        isy: ISY class
        xml: String of xml data containing the configuration data
        """
        super().__init__()
        self.isy = isy

        if xml is not None:
            self.parse(xml)

    def parse(self, xml):
        """
        Parse the xml data.

        xml: String of the xml data
        """
        xmldoc = minidom.parseString(xml)

        self["firmware"] = value_from_xml(xmldoc, TAG_FIRMWARE)

        try:
            self["uuid"] = (
                xmldoc.getElementsByTagName("root")[0]
                .getElementsByTagName(ATTR_ID)[0]
                .firstChild.toxml()
            )
        except IndexError:
            self["uuid"] = None

        features = xmldoc.getElementsByTagName(TAG_FEATURE)

        for feature in features:
            idnum = value_from_xml(feature, ATTR_ID)
            desc = value_from_xml(feature, ATTR_DESC)
            installed_raw = value_from_xml(feature, TAG_INSTALLED)
            installed = bool(installed_raw == XML_TRUE)
            self[idnum] = installed
            self[desc] = self[idnum]

        self.isy.log.info("ISY Loaded Configuration")
