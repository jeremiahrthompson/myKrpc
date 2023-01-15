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
        return control.Control(self.conn)

    def get_go(self):
        go = self.params['go']
        if (go == 'False') or (go is None) or (not go):
            return False
        return True

    def get_name(self):
        name = self.params['name']
        if (name is None) or (name == ''):
            self.go = False
            return None
        return name

    def get_version(self):
        version = self.params['version']
        if (version is None) or (version == '') or (version == 0):
            self.go = False
            return None
        return version

    def get_apoapsis(self):
        apoapsis = self.params['apoapsis']
        if (type(apoapsis) is not int) or (apoapsis is None) or (apoapsis < 72000):
            self.go = False
            return 0
        elif (type(apoapsis) is int) and (apoapsis > 72000):
            return apoapsis
        self.go = False
        return 0

    def get_heading(self):
        heading = self.params['heading']
        if (type(heading) is not int) or (heading is None) or (heading < 0) or (heading > 360):
            print()
            self.go = False
            return 0
        elif (type(heading) is int) and (heading >= 0) and (heading <= 360):
            return heading
        self.go = False
        return 0

    def start(self):
        if self.go:
            print('Launching {}-{} to {}m at a heading of {}'.format(self.name, self.version, self.apoapsis, self.heading))
        else:
            print('Launch not started')
