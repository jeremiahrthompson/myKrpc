class VesselControl:
    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel = this_conn.space_center.active_vessel
        self.altitude = this_conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    # reestablishing active vessel, reference frames and streams (primarily used after decoupling)
    def reestablish(self):
        self.vessel = self.conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
        self.apoapsis = self.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.altitude = self.conn.add_stream(getattr, self.vessel.flight(), 'surface_altitude')

    # adjusts throttle based on max q
    def adjust_throttle_max_q(self):
        if self.vessel.flight().dynamic_pressure > 12000:
            while self.vessel.flight().dynamic_pressure > 12000 and self.vessel.control.throttle > 0.1:
                self.vessel.control.throttle = self.vessel.control.throttle - .005
        elif self.vessel.flight().dynamic_pressure < 12000:
            while self.vessel.flight().dynamic_pressure < 12000 and self.vessel.control.throttle < 1:
                self.vessel.control.throttle = self.vessel.control.throttle + .005

    # adjusts throttle based on thrust to weight
    def adjust_throttle_twr(self, twr):
        if (self.thrust_weight() - twr) > .05:
            while self.thrust_weight() > twr and self.vessel.control.throttle > 0:
                self.vessel.control.throttle = self.vessel.control.throttle - .005
        elif (self.thrust_weight() - twr) < -.05:
            while self.thrust_weight() < twr and self.vessel.control.throttle < 1:
                self.vessel.control.throttle = self.vessel.control.throttle + .005

    # returns thrust to weight of active vessel
    def thrust_weight(self):
        return float(self.vessel.thrust / (self.vessel.mass * self.vessel.orbit.body.surface_gravity))

    # activates engines in the current stage if they are not already active
    def activate_current_stage_engines(self):
        # loop through all parts in current stage
        for part in self.get_current_stage_parts():
            # if part is engine and engine can activate or restart
            if part.engine is not None and part.engine.can_restart:
                # activate the engine
                part.engine.active = True

    # activates next stage if next stage contains at least 1 engine and stage is all engines or fairings
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

    # activates or decouples fairings and engines for continued flight
    def activate_or_decouple_engines_and_fairings(self):
        self.activate_current_stage_engines()
        self.activate_next_stage_engines()
        self.jettison_fairing()

    # jettisons fairings if altitude greater than 60000m and only fairings are in next stage
    def jettison_fairing(self):
        # check to see if vessel altitude is above 60000m
        if self.altitude() > 60000:
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

    # return all parts as a list that will be decoupled with next stage activation
    def get_decouple_stage_parts(self):
        return self.vessel.parts.in_decouple_stage(self.vessel.control.current_stage - 1)

    # activate next stage and reestablish streams, active vessel
    def activate_next_stage(self):
        self.vessel.control.activate_next_stage()
        self.reestablish()

    # return all parts as a list that are in the next stage
    def get_next_stage_parts(self):
        return self.vessel.parts.in_stage(self.vessel.control.current_stage - 1)

    # return all parts as a list that are in the current stage
    def get_current_stage_parts(self):
        return self.vessel.parts.in_stage(self.vessel.control.current_stage)

    # method used to autostage during ascent
    def autostage(self):
        # activate or decouple engines and fairings
        self.activate_or_decouple_engines_and_fairings()
        # decouple spent fuel tanks
        self.decouple_fuel_tanks()

    # decouple next stage fuel tanks in stage have Liquid Fuel or Oxidizer depleted
    def decouple_fuel_tanks(self):
        # loop through all parts that will be decoupled with next stage activation
        for part in self.get_decouple_stage_parts():
            # if the part can hold resource and the resource amount is 0 decouple the stage
            if (part.resources.has_resource("LiquidFuel")) and (part.resources.amount("LiquidFuel") == 0):
                self.activate_next_stage()
                break
            elif (part.resources.has_resource("Oxidizer")) and (part.resources.amount("Oxidizer") == 0):
                self.activate_next_stage()
                break

    # disengages autopilot then sets SAS to orbital prograde, if prograde not available with alt to stability assist.
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

    # checks to see if autopilot is active by checking for pitch error.  if this throws exception autopilot needs
    # activated.
    def engage_autopilot(self):
        try:
            self.vessel.auto_pilot.pitch_error
        except RuntimeError:
            print("    Engaging AutoPilot")
            self.vessel.auto_pilot.engage()
            pass