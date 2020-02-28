"""Base object for nodes and groups."""
from xml.dom import minidom

from ..constants import COMMAND_FRIENDLY_NAME, UPDATE_INTERVAL, XML_PARSE_ERROR
from ..helpers import value_from_xml
from .handlers import EventEmitter


class NodeBase:
    """Base Object for Nodes and Groups/Scenes."""

    has_children = False

    def __init__(self, nodes, address, name, status, aux_properties=None):
        """Initialize a Group class."""
        self._nodes = nodes
        self.isy = nodes.isy
        self._id = address
        self._name = name
        self._notes = None
        self._aux_properties = aux_properties if aux_properties is not None else {}
        self._status = status
        self.status_events = EventEmitter()

    def __str__(self):
        """Return a string representation of the node."""
        return "{}({})".format(type(self).__name__, self._id)

    @property
    def status(self):
        """Return the current node state."""
        return self._status

    @status.setter
    def status(self, value):
        """Set the current node state and notify listeners."""
        if self._status != value:
            self._status = value
            self.status_events.notify(self._status)
        return self._status

    @property
    def aux_properties(self):
        """Return the aux properties that were in the Node Definition."""
        return self._aux_properties

    @property
    def address(self):
        """Return the Node ID."""
        return self._id

    @property
    def name(self):
        """Return the name of the Node."""
        return self._name

    def parse_notes(self):
        """Parse the notes for a given node."""
        notes_xml = self.isy.conn.request(
            self.isy.conn.compile_url(["nodes", self._id, "notes"]), ok404=True
        )
        spoken = None
        if notes_xml is not None and notes_xml != "":
            try:
                notesdom = minidom.parseString(notes_xml)
            except:
                self.isy.log.error("%s: Node Notes %s", XML_PARSE_ERROR, notes_xml)
            else:
                spoken = value_from_xml(notesdom, "spoken")
        return {"spoken": spoken}

    @property
    def spoken(self):
        """Return the text of the Spoken property inside the group notes."""
        self._notes = self.parse_notes()
        return self._notes["spoken"]

    def off(self):
        """Turn off the nodes/group in the ISY."""
        return self.send_cmd("DOF")

    def on(self, val=None):
        """
        Turn the node on.

        |  [optional] val: The value brightness value (0-255) for the node.
        """
        if val is None or type(self).__name__ == "Group":
            cmd = "DON"
        elif int(val) > 0:
            cmd = "DON"
            val = str(val) if int(val) <= 255 else None
        else:
            cmd = "DOF"
            val = None
        return self.send_cmd(cmd, val)

    def update(self, wait_time=0, hint=None, xmldoc=None):
        """Update the group with values from the controller."""
        pass

    def send_cmd(self, cmd, val=None, uom=None, query=None):
        """Send a command to the device."""
        value = str(val) if val is not None else None
        _uom = str(uom) if uom is not None else None
        req = ["nodes", str(self._id), "cmd", cmd]
        if value:
            req.append(value)
        if _uom:
            req.append(_uom)
        req_url = self.isy.conn.compile_url(req, query)
        if not self.isy.conn.request(req_url):
            self.isy.log.warning(
                "ISY could not send %s command to %s.",
                COMMAND_FRIENDLY_NAME.get(cmd),
                self._id,
            )
            return False
        self.isy.log.debug(
            "ISY command %s sent to %s.", COMMAND_FRIENDLY_NAME.get(cmd), self._id
        )

        # Calculate hint to use if status is updated
        hint = self.status
        if cmd in ["DON", "DFON"]:
            if val is not None:
                hint = val
            elif "OL" in self._aux_properties:
                hint = self._aux_properties["OL"].get("value")
            else:
                hint = 255
        if cmd in ["DOF", "DFOF"]:
            hint = 0
        self.update(UPDATE_INTERVAL, hint=hint)
        return True

