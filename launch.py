import time
import circularize


class Launch:

    def __init__(self, this_conn):
        self.conn = this_conn
        self.circ = circularize.Circularize(this_conn)
        self.vessel = this_conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
        self.apoapsis = this_conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.altitude = this_conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    def reestablish(self):
        self.vessel = self.conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    def start(self, desired_heading, desired_apoapsis):
        if self.liftoff(desired_heading):
            if self.ascend(desired_apoapsis, desired_heading):
                self.circ.circularize()
                print("****    Disengaging Launch Sequence    ****")
            else:
                self.final_injection(desired_apoapsis, desired_heading)

    def liftoff(self, heading):
        if self.altitude() < 100:
            print("Launch Sequence")
            self.set_pitch_heading(90, heading)
            # launch_call = "T - "
            # for x in [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
            #     print(launch_call + str(x))
            #     if x == 3:
            #         self.vessel.control.throttle = .2
            #     if x == 2:
            #         self.vessel.control.throttle = .4
            #         self.vessel.control.activate_next_stage()
            #     if x == 1:
            #         self.vessel.control.throttle = 1
            #     time.sleep(1)
            self.vessel.control.activate_next_stage() # get rid of when using countdown
            self.vessel.control.throttle = 1 # get rid of when using countdown
            while self.thrust_weight() < 1.1:
                pass
            self.vessel.control.activate_next_stage()
            while self.flight.speed < 10:
                pass
            print("****    LIFTOFF    ****")
            print("****    of the    ****")
            print("****    " + self.vessel.name + "    ****")
            return True
        else:
            return False

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
            self.autostage()
            self.adjust_throttle_twr(1.4)

    def pitch_maneuver(self, heading):
        print("Pitch Maneuver")
        for x in range(1, 8):
            self.set_pitch_heading(90 - x, heading)
            self.autostage()
            self.adjust_throttle_twr(1.3)
            time.sleep(.5)

    def initial_injection(self, heading):
        print("Initial Injection")
        while self.altitude() < 20000:
            self.adjust_pitch(45, 20000, heading)
            self.autostage()
            self.adjust_throttle_twr(1.4)

    def secondary_injection(self, target_orbit_alt, heading):
        print("Secondary Injection")
        while self.altitude() < 45000:
            self.adjust_pitch(89, 45000, heading)
            self.autostage()
            self.adjust_throttle_twr(1.6)
            if self.vessel.orbit.apoapsis_altitude > target_orbit_alt:
                break

    def main_injection(self, target_orbit_alt, heading):
        print("Main Injection")
        while self.apoapsis() < (target_orbit_alt * .97):
            self.autostage()
            self.set_pitch_heading(0, heading)
            self.vessel.control.throttle = 1
        self.vessel.control.throttle = 0

    def final_injection(self, target_orbit_alt, heading):
        print("Final Injection")
        self.set_pitch_heading(0, heading)
        self.vessel.auto_pilot.wait()
        while self.altitude() < 70100:
            self.set_pitch_heading(0, heading)
            self.autostage()
            if self.apoapsis() < target_orbit_alt:
                self.vessel.control.throttle = .1
            else:
                self.vessel.control.throttle = 0
        self.vessel.control.throttle = 0
        self.set_pitch_heading(0, heading)

    def set_pitch_heading(self, pitch, heading):
        self.engage_autopilot()
        self.vessel.auto_pilot.target_pitch_and_heading(pitch, heading)

    def adjust_pitch(self, target_pitch, target_altitude, heading):
        error_pitch = round((target_pitch - (self.flight.pitch - 15.3)) / target_pitch, 2)
        error_altitude = round((target_altitude - self.flight.surface_altitude) / target_altitude, 2)
        if error_pitch > error_altitude:
            self.set_pitch_heading((90 - (self.flight.pitch - 15.3) - .5), heading)

    def adjust_throttle_twr(self, twr):
        if (self.thrust_weight() - twr) > .05:
            while self.thrust_weight() > twr and self.vessel.control.throttle > 0:
                self.vessel.control.throttle = self.vessel.control.throttle - .005
        elif (self.thrust_weight() - twr) < -.05:
            while self.thrust_weight() < twr and self.vessel.control.throttle < 1:
                self.vessel.control.throttle = self.vessel.control.throttle + .005

    def thrust_weight(self):
        return float(self.vessel.thrust / (self.vessel.mass * self.vessel.orbit.body.surface_gravity))

    def activate_stage_engines(self):
        self.reestablish()
        parts = self.vessel.parts.all
        next_stage = self.vessel.control.current_stage - 1
        for part in parts:
            if part.engine is not None and part.stage == next_stage:
                if part.engine.can_restart:
                    part.engine.active = True

    def autostage(self):
        self.activate_stage_engines()
        decoupled = False
        parts = self.vessel.parts.all
        current_stage = self.vessel.control.current_stage
        next_stage = current_stage - 1
        if next_stage >= 0:
            for part in parts:
                if (part.decouple_stage == next_stage) and (part.resources.has_resource("LiquidFuel")) and (
                        part.resources.amount("LiquidFuel") == 0):
                    print("    Activating Stage: " + str(next_stage))
                    self.vessel.control.activate_next_stage()
                    decoupled = True
                elif (part.decouple_stage == next_stage) and (part.resources.has_resource("Oxidizer")) and (
                        part.resources.amount("Oxidizer") == 0):
                    print("    Activating Stage: " + str(next_stage))
                    self.vessel.control.activate_next_stage()
                    decoupled = True
            if decoupled:
                self.reestablish()

    def set_sas_orbital_prograde(self):
        self.vessel.auto_pilot.disengage()
        self.vessel.control.sas = True
        try:
            self.vessel.control.speed_mode = self.vessel.control.speed_mode.orbit
        except RuntimeError:
            print('    Could not set Speed Mode - orbit')
            pass
        try:
            self.vessel.control.sas_mode = self.vessel.control.sas_mode.prograde
        except RuntimeError:
            print('    Could not set SAS Mode - prograde')
            self.vessel.control.sas_mode = self.vessel.control.sas_mode.stability_assist
            print('    Setting SAS Mode to - stability_assist')
            pass

    def engage_autopilot(self):
        try:
            self.vessel.auto_pilot.pitch_error
        except RuntimeError:
            print("    Engaging AutoPilot")
            self.vessel.auto_pilot.engage()
            pass
