"""ISY Programs."""
from .folder import Folder


class Program(Folder):
    """
    Class representing a program on the ISY controller.

    |  programs: The program manager object.
    |  address: The ID of the program.
    |  pname: The name of the program.
    |  pstatus: The current status of the program.
    |  plastup: The last time the program was updated.
    |  plastrun: The last time the program was run.
    |  plastfin: The last time the program finished running.
    |  penabled: Boolean value showing if the program is enabled on the
                 controller.
    |  pstartrun: Boolean value showing if the if the program runs on
                  controller start up.
    |  prunning: Boolean value showing if the current program is running
                 on the controller.

    :ivar name: The name of the program.
    :ivar status: Watched property representing the current status of the
                  program.
    :ivar last_update: Watched property representing the last time the program
                      was updated.
    :ivar last_run: Watched property representing the last time the program was
                   run.
    :ivar last_finished: Watched property representing the last time the program
                        finished running.
    :ivar enabled: Watched property representing if the program is enabled on
                   the controller.
    :ivar run_at_startup: Watched property representing the if the program runs
                        on controller start up.
    :ivar running: Watched property representing if the current program is
                   running on the controller.
    """

    dtype = "program"

    def __init__(
        self,
        programs,
        address,
        pname,
        pstatus,
        plastup,
        plastrun,
        plastfin,
        penabled,
        pstartrun,
        prunning,
    ):
        """Initialize a Program class."""
        super(Program, self).__init__(programs, address, pname, pstatus)
        self.last_update = plastup
        self.last_run = plastrun
        self.last_finished = plastfin
        self.enabled = penabled
        self.run_at_startup = pstartrun
        self.running = prunning
        self.ran_then = 0
        self.ran_else = 0

    def update(self, wait_time=0, data=None):
        """
        Update the program with values on the controller.

        |  wait_time: [optional] Seconds to wait before updating.
        |  data: [optional] Data to update the object with.
        """
        if not self.noupdate:
            if data is not None:
                prunning = (data["plastrun"] >= data["plastup"]) or data["prunning"]
                self.last_update = data["plastup"]
                self.last_run = data["plastrun"]
                self.last_finished = data["plastfin"]
                self.enabled = data["penabled"]
                self.run_at_startup = data["pstartrun"]
                self.running = prunning
                # Update Status last and make sure the change event fires, but only once.
                if self.status != data["pstatus"]:
                    self.status = data["pstatus"]
                else:
                    # Status didn't change, but something did, so fire the event.
                    self.status_events.notify(self.status)
            elif not self.isy.auto_update:
                self._programs.update(wait_time, address=self._id)

    @property
    def protocol(self):
        """Return the protocol for this entity."""
        return "program"
