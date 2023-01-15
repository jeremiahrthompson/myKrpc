class Control:
    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel = self.get_active_vessel()
        self.altitude = self.get_surface_altitude_stream()

    def get_refframe(self):
        return self.vessel.orbit.body.reference_frame

    def get_active_vessel(self):
        return self.conn.space_center.active_vessel

    def get_surface_altitude_stream(self):
        return self.conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    def reestablish(self):
        self.vessel = self.get_active_vessel()
