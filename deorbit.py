
class Deorbit:

    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel = this_conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
        self.apoapsis = this_conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.altitude = this_conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    def deorbit(self):
        self.calculate_burn()

    def calculate_burn(self):
        vessels = self.conn.space_center.vessels
        for target_vessel in vessels:
            if target_vessel.name == 'Landing Pad':
                print(target_vessel.name)
                # target_longitude = self.conn.add_stream(getattr, target_vessel.flight(), 'longitude')
                while True:
                    print(target_vessel.flight().longitude)
        while True:
            print(self.vessel.orbit.longitude_of_ascending_node)
