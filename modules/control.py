import time


class Control:
    def __init__(self, conn=None, params=None):
        self.conn = conn
        self.params = params
        self.vessel = self.get_active_vessel()
        self.clamps = False
        self.refframe = self.get_refframe()
        self.flight = self.get_flight()
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    def get_refframe(self):
        return self.vessel.orbit.body.reference_frame

    def get_flight(self):
        return self.vessel.flight(self.refframe)

    def get_active_vessel(self):
        return self.conn.space_center.active_vessel

    def reestablish(self):
        self.vessel = self.get_active_vessel()

    def engage_autopilot_if_not_engaged(self):
        try:
            self.vessel.auto_pilot.pitch_error
        except RuntimeError:
            self.vessel.auto_pilot.engage()
            pass

    def activate_current_stage_engines(self):
        for part in self.get_current_stage_parts():
            if part.engine is not None and part.engine.can_restart:
                part.engine.active = True

    def get_current_stage_parts(self):
        return self.vessel.parts.in_stage(self.vessel.control.current_stage)

    def get_next_stage_parts(self):
        return self.vessel.parts.in_stage(self.vessel.control.current_stage - 1)

    def set_pitch_heading(self, pitch, heading):
        self.engage_autopilot_if_not_engaged()
        self.vessel.auto_pilot.target_pitch_and_heading(pitch, heading)

    def release_clamps(self):
        for part in self.vessel.parts.launch_clamps:
            if part.decouple is not None:
                part.decouple()

    def activate_next_stage(self):
        self.vessel.control.activate_next_stage()

    def get_twr(self):
        return float(self.vessel.thrust / (self.vessel.mass * self.vessel.orbit.body.surface_gravity))

    def jettison_fairing(self):
        # check to see if vessel altitude is above 60000m
        if self.altitude() > 60000:
            print("    Jettisoning Fairings - above 60000m")
            # set jettison to true.
            jettison = True
            # loop through all parts decoupled in next stage
            for part in self.get_decouple_stage_parts():
                # if part is not a fairing set jettison to false
                if part.fairing is None:
                    jettison = False
            # if all parts in next stage are fairings then jettison stage
            if jettison:
                self.activate_next_stage()

    def activate_next_stage_engines(self):
        # set decouple to True
        decouple = True
        # set engine to False
        engine = False
        # loop through all parts in next stage
        for part in self.get_next_stage_parts():
            # if part is not an engine or fairing set decouple to False
            if part.engine is None and part.fairing is None:
                decouple = False
            # must have an engine in next stage to decouple
            if part.engine is not None:
                engine = True
        # if all parts in next stage have at least 1 engine and are all engines or fairings then decouple stage
        if decouple and engine:
            self.activate_next_stage()

    def activate_or_decouple_engines_and_fairings(self):
        self.activate_current_stage_engines()
        self.activate_next_stage_engines()
        self.jettison_fairing()

    def get_decouple_stage_parts(self):
        return self.vessel.parts.in_decouple_stage(self.vessel.control.current_stage - 1)

    def decouple_fuel_tanks(self):
        # loop through all parts that will be decoupled with next stage activation
        for part in self.get_decouple_stage_parts():
            # if the part can hold resource and the resource amount is 0 decouple the stage
            if (part.resources.has_resource("LiquidFuel")) and (part.resources.amount("LiquidFuel") == 0):
                self.activate_next_stage()
                print("    Decoupling Fuel Tank - Liquid Fuel Depleted")
                break
            elif (part.resources.has_resource("Oxidizer")) and (part.resources.amount("Oxidizer") == 0):
                self.activate_next_stage()
                print("    Decoupling Fuel Tank - Oxidizer Depleted")
                break

    def adjust_throttle_twr(self, twr):
        if (self.get_twr() - twr) > .05:
            while self.get_twr() > twr and self.vessel.control.throttle > 0:
                self.vessel.control.throttle = self.vessel.control.throttle - .005
        elif (self.get_twr() - twr) < -.05:
            while self.get_twr() < twr and self.vessel.control.throttle < 1:
                self.vessel.control.throttle = self.vessel.control.throttle + .005

    def autostage(self):
        self.activate_or_decouple_engines_and_fairings()
        self.decouple_fuel_tanks()

    def launch(self):
        self.countdown()
        self.ascent()

    def countdown(self):
        self.vessel.control.throttle = 0
        self.set_pitch_heading(90, self.params['heading'])
        seconds = self.params['seconds']
        clamps = self.vessel.parts.launch_clamps
        if clamps is not None and len(clamps) > 0:
            self.clamps = True
        for i in range(seconds, 0, -1):
            if i > 60:
                if i % 30 == 0:
                    print(f"T-{i}")
            elif i > 10:
                if i % 10 == 0:
                    print(f"T-{i}")
            elif i == 10:
                print(f"T-{i}")
            elif i == 9:
                print(f"T-{i}")
            elif i == 8:
                print(f"T-{i}")
            elif i == 7:
                print(f"T-{i}")
            elif i == 6:
                print(f"T-{i}")
            elif i == 5:
                print(f"T-{i}")
            elif i == 4:
                if self.clamps:
                    self.activate_next_stage()
                    self.vessel.control.throttle = .1
                print(f"T-{i}")
            elif i == 3:
                if self.clamps:
                    self.vessel.control.throttle = .2
                print(f"T-{i}")
            elif i == 2:
                if self.clamps:
                    self.vessel.control.throttle = .5
                print(f"T-{i}")
            elif i == 1:
                self.vessel.control.throttle = 1
                self.activate_next_stage()
                print(f"T-{i}")
            time.sleep(1)
        if self.clamps:
            while self.get_twr() < 1.2:
                pass
            self.activate_next_stage()

    def ascent(self):
        heading = self.params['heading']
        print(f"---------------- Liftoff of the {self.params['name']} ----------------")
        while self.flight.speed < 100:
            self.set_pitch_heading(90, heading)
            self.autostage()
            self.adjust_throttle_twr(1.7)

