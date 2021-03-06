import vessel_control
import time


class Science:

    def __init__(self, this_conn):
        self.conn = this_conn
        self.vessel_control = vessel_control.VesselControl(this_conn)
        self.vessel = this_conn.space_center.active_vessel
        self.part = self.get_laboratory_part()
        self.transmit_module = self.get_science_transmit_module()
        self.data_module = self.get_science_data_module()
        self.container_module = self.get_science_container_module()
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)

    def start(self):
        if float(self.data_module.get_field('Science')[:-4]) < 499:
            self.warp_to_data()
        self.transmit_science()

    def warp_to_data(self):
        self.start_warp(7)
        while float(self.data_module.get_field('Science')[:-4]) < 499:
            pass
        self.stop_warp()

    def transmit_science(self):
        if self.transmit_module.has_event('Transmit Science'):
            self.transmit_module.trigger_event('Transmit Science')
            self.start_warp(3)
            while float(self.data_module.get_field('Science')[:-4]) > 10:
                pass
            self.stop_warp()

    def start_warp(self, level):
        for interval in range(level):
            self.conn.space_center.rails_warp_factor = interval + 1
            time.sleep(.5)

    def stop_warp(self):
        self.conn.space_center.rails_warp_factor = 0

    def get_laboratory_part(self):
        for part in self.vessel.parts.all:
            if part.name == 'Large.Crewed.Lab':
                return part

    def get_science_transmit_module(self):
        for module in self.part.modules:
            if module.name == 'ModuleScienceLab':
                return module

    def get_science_data_module(self):
        for module in self.part.modules:
            if module.name == 'ModuleScienceConverter':
                return module

    def get_science_container_module(self):
        for module in self.part.modules:
            if module.name == 'ModuleScienceContainer':
                return module
