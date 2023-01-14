import time
import math
import vessel_control


class Circularize:

    # runs on class initialization, is passed connection from call.
    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel_control = vessel_control.VesselControl(this_conn)
        self.vessel = this_conn.space_center.active_vessel
        self.ref_frame = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.ref_frame)
        self.ut = this_conn.add_stream(getattr, this_conn.space_center, 'ut')

    def start(self):
        print("Circularize")
        calc_burn = self.calc_burn()
        burn_time = calc_burn[0]
        delta_v = calc_burn[1]
        node = self.time_warp(burn_time, delta_v)
        self.burn(burn_time, node)
        self.vessel_control.set_sas_orbital_prograde()

    def calc_burn(self):
        self.vessel = self.conn.space_center.active_vessel
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = r
        v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
        v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
        delta_v = v2 - v1
        f = self.vessel.available_thrust
        isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass
        m1 = m0 / math.exp(delta_v / isp)
        flow_rate = f / isp
        burn_time = (m0 - m1) / flow_rate
        return_values = (burn_time, delta_v)
        return return_values

    def time_warp(self, burn_time, delta_v):
        node = self.vessel.control.add_node(
            self.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)
        self.vessel_control.engage_autopilot()
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0, 1, 0)
        self.vessel.auto_pilot.wait()
        burn_ut = self.ut() + self.vessel.orbit.time_to_apoapsis - (burn_time / 2.)
        lead_time = 5
        self.conn.space_center.warp_to(burn_ut - lead_time)
        return node

    def burn(self, burn_time, node):
        time_to_apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'time_to_apoapsis')
        while time_to_apoapsis() - (burn_time / 2.) > 0:
            pass
        self.vessel.control.throttle = 1.0
        time.sleep(burn_time - 0.07)
        self.vessel.control.throttle = 0
        remaining_burn = self.conn.add_stream(node.remaining_burn_vector, node.reference_frame)
        self.vessel.auto_pilot.wait()
        self.vessel.control.throttle = .05
        while remaining_burn()[1] > .03:
            pass
        self.vessel.control.throttle = 0.0
        node.remove()
