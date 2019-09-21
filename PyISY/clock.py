"""ISY Clock/Location Information."""
from time import sleep
from xml.dom import minidom

from .constants import XML_PARSE_ERROR, EMPTY_TIME
from .helpers import value_from_xml, ntp_to_system_time


class Clock:
    """
    ISY Clock class cobject.

    DESCRIPTION:
        This class handles the ISY clock/location info.

    ATTRIBUTES:
        isy: The ISY device class
        last_called: the time of the last call to /rest/time
        tz_offset: The Time Zone Offset of the ISY
        dst: Daylight Savings Time Enabled or not
        latitude: ISY Device Latitude
        longitude: ISY Device Longitude
        sunrise: ISY Calculated Sunrise
        sunset: ISY Calculated Sunset
        military: If the clock is military time or not.

    """

    def __init__(self, isy, xml=None):
        """
        Initialize the network resources class.

        isy: ISY class
        xml: String of xml data containing the configuration data
        """
        self.isy = isy
        self._last_called = EMPTY_TIME
        self._tz_offset = 0
        self._dst = False
        self._latitude = 0.0
        self._longitude = 0.0
        self._sunrise = EMPTY_TIME
        self._sunset = EMPTY_TIME
        self._military = False

        if xml is not None:
            self.parse(xml)

    def __str__(self):
        """Return a string representing the clock Class."""
        return "ISY Clock (Last Updated {!s})".format(self.last_called)

    def __repr__(self):
        """Return a long string showing all the clock values."""
        props = [
            name for name, value in vars(Clock).items() if isinstance(value, property)
        ]
        return "ISY Clock: {!r}".format(
            {prop: str(getattr(self, prop)) for prop in props}
        )

    def parse(self, xml):
        """
        Parse the xml data.

        xml: String of the xml data
        """
        try:
            xmldoc = minidom.parseString(xml)
        except (TypeError, KeyError):
            self.isy.log.error("%s: Clock", XML_PARSE_ERROR)
        else:
            tz_offset_sec = int(value_from_xml(xmldoc, "TMZOffset"))
            self._tz_offset = tz_offset_sec / 3600
            self._dst = value_from_xml(xmldoc, "DST") == "true"
            self._latitude = float(value_from_xml(xmldoc, "Lat"))
            self._longitude = float(value_from_xml(xmldoc, "Long"))
            self._military = value_from_xml(xmldoc, "IsMilitary") == "true"
            self._last_called = ntp_to_system_time(int(value_from_xml(xmldoc, "NTP")))
            self._sunrise = ntp_to_system_time(int(value_from_xml(xmldoc, "Sunrise")))
            self._sunset = ntp_to_system_time(int(value_from_xml(xmldoc, "Sunset")))

            self.isy.log.info("ISY Loaded Clock Information")

    def update(self, wait_time=0):
        """
        Update the contents of the networking class.

        wait_time: [optional] Amount of seconds to wait before updating
        """
        sleep(wait_time)
        xml = self.isy.conn.get_time()
        self.parse(xml)

    def update_thread(self, interval):
        """
        Continually update the class until it is told to stop.

        Should be run in a thread.
        """
        while self.isy.auto_update:
            self.update(interval)

    @property
    def last_called(self):
        """Get the time of the last call to /rest/time in UTC."""
        return self._last_called

    @property
    def tz_offset(self):
        """Provide the Time Zone Offset from the isy in Hours."""
        return self._tz_offset

    @property
    def dst(self):
        """Confirm if DST is enabled or not on the ISY."""
        return self._dst

    @property
    def latitude(self):
        """Provide the latitude information from the isy."""
        return self._latitude

    @property
    def longitude(self):
        """Provide the longitude information from the isy."""
        return self._longitude

    @property
    def sunrise(self):
        """Provide the sunrise information from the isy (UTC)."""
        return self._sunrise

    @property
    def sunset(self):
        """Provide the sunset information from the isy (UTC)."""
        return self._sunset

    @property
    def military(self):
        """Confirm if military time is in use or not on the isy."""
        return self._military
