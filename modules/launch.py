from modules import control


class Launch:

    def __init__(self, conn=None, params=None):
        self.conn = conn
        self.params = params
        self.control = self.get_control()
        self.go = self.get_go()
        self.name = self.get_name()
        self.version = self.get_version()
        self.apoapsis = self.get_apoapsis()
        self.heading = self.get_heading()

    def get_control(self):
        return control.Control(self.conn, self.params)

    def get_go(self):
        go = self.params['go']
        if (go == 'False') or (go is None) or (not go):
            return False
        return True

    def get_name(self):
        name = self.params['name']
        if (name is None) or (name == ''):
            return 'unknown_name'
        return name

    def get_version(self):
        version = self.params['version']
        if (version is None) or (version == '') or (version == 0):
            return 1
        return version

    def get_apoapsis(self):
        apoapsis = self.params['apoapsis']
        if (type(apoapsis) is not int) or (apoapsis is None) or (apoapsis < 72000):
            return 100000
        elif (type(apoapsis) is int) and (apoapsis > 72000):
            return apoapsis
        return 100000

    def get_heading(self):
        heading = self.params['heading']
        if (type(heading) is not int) or (heading is None) or (heading < 0) or (heading > 360):
            return 90
        elif (type(heading) is int) and (heading >= 0) and (heading <= 360):
            return heading
        return 90

    def start(self):
        if self.go:
            self.control.launch()
        else:
            print('Launch not started')
