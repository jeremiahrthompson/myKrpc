import time
import vessel_control


class Science:

    # runs on class initialization, is passed connection from call.
    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel_control = vessel_control.VesselControl(this_conn)
        self.vessel = this_conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
