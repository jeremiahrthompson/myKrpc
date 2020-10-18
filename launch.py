import time
import vessel_control


class Launch:

    # runs on class initialization, is passed connection from call.
    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel_control = vessel_control.VesselControl(this_conn)
        self.vessel = this_conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
        self.apoapsis = this_conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.altitude = this_conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')
        self.q = this_conn.add_stream(getattr, self.vessel.flight(), 'dynamic_pressure')

    # default method which calls all phases of launch to circularization
    def start(self, desired_heading, desired_apoapsis):
        self.liftoff(desired_heading)
        self.ascend(desired_apoapsis, desired_heading)
        print("****    Disengaging Launch Sequence    ****")

    # controls vessel during launch sequence and hands off after vessel speed is greater than 10m/s.
    def liftoff(self, heading):
        # start launch sequence if vessel altidude is below 100m
        if self.altitude() < 100:
            print("Launch Sequence")
            # set initial autopilot to the input heading and 90 pitch
            self.set_pitch_heading(90, heading)
            # begin countdown and engine warmup
            self.countdown()
            # don't release launch clamps until twr is greater than 1.1
            while self.vessel_control.thrust_weight() < 1.1:
                pass
            self.vessel_control.activate_next_stage()
            while self.flight.speed < 10:
                pass
            print("****    LIFTOFF    ****")
            print("****    of the    ****")
            print("****    " + self.vessel.name + "    ****")
            return True
        else:
            return False

    # begin countdown from 10 down to 1.
    def countdown(self):
        launch_call = "T - "
        for x in [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
            print(launch_call + str(x))
            if x == 2:
                # begin engine start up
                self.vessel.control.throttle = .2
                self.vessel_control.activate_next_stage()
            if x == 1:
                # throttle to full
                self.vessel.control.throttle = 1
            time.sleep(1)

    # methond that syncronizes ascent phases
    def ascend(self, target_orbit_alt, heading):
        print("    Ascending To:")
        print("    Heading = " + str(heading))
        print("    Target Orbit Altitude = " + str(target_orbit_alt) + "m")
        self.climb(heading)
        self.pitch_maneuver(heading)
        self.initial_injection(heading)
        self.secondary_injection(target_orbit_alt, heading)
        self.main_injection(target_orbit_alt, heading)
        self.final_injection(target_orbit_alt, heading)
        if self.vessel.orbit.apoapsis_altitude > (target_orbit_alt * .95):
            return True
        else:
            print("Apoapsis not reached.  Finalizing")
            return False

    def climb(self, heading):
        print("Climb")
        while self.flight.speed < 100:
            self.set_pitch_heading(90, heading)
            self.vessel_control.autostage()
            self.vessel_control.adjust_throttle_twr(1.3)

    def pitch_maneuver(self, heading):
        print("Pitch Maneuver")
        for x in range(1, 8):
            self.set_pitch_heading(90 - x, heading)
            self.vessel_control.autostage()
            self.vessel_control.adjust_throttle_twr(1.4)
            time.sleep(.5)

    def initial_injection(self, heading):
        print("Initial Injection")
        while self.altitude() < 20000:
            self.adjust_pitch(45, 20000, heading)
            self.vessel_control.autostage()
            self.vessel_control.adjust_throttle_twr(1.5)

    def secondary_injection(self, target_orbit_alt, heading):
        print("Secondary Injection")
        while self.altitude() < 45000:
            self.adjust_pitch(89, 45000, heading)
            self.vessel_control.autostage()
            self.vessel_control.adjust_throttle_twr(1.6)
            if self.vessel.orbit.apoapsis_altitude > target_orbit_alt:
                break

    def main_injection(self, target_orbit_alt, heading):
        print("Main Injection")
        while self.apoapsis() < (target_orbit_alt * .97):
            self.vessel_control.autostage()
            self.set_pitch_heading(0, heading)
            self.vessel_control.adjust_throttle_twr(2.2)
        self.vessel.control.throttle = 0

    def final_injection(self, target_orbit_alt, heading):
        print("Final Injection")
        self.set_pitch_heading(0, heading)
        self.vessel.auto_pilot.wait()
        while self.altitude() < 70100:
            self.set_pitch_heading(0, heading)
            self.vessel_control.autostage()
            if self.apoapsis() < target_orbit_alt:
                self.vessel.control.throttle = .1
            else:
                self.vessel.control.throttle = 0
        self.vessel.control.throttle = 0
        self.set_pitch_heading(0, heading)

    def set_pitch_heading(self, pitch, heading):
        self.vessel_control.engage_autopilot()
        self.vessel.auto_pilot.target_pitch_and_heading(pitch, heading)

    def adjust_pitch(self, target_pitch, target_altitude, heading):
        error_pitch = round((target_pitch - (self.flight.pitch - 15.3)) / target_pitch, 2)
        error_altitude = round((target_altitude - self.flight.surface_altitude) / target_altitude, 2)
        if error_pitch > error_altitude:
            self.set_pitch_heading((90 - (self.flight.pitch - 15.3) - .5), heading)