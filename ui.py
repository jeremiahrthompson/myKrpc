import launch
import circularize


class UserInterface:

    def __init__(self, this_conn):
        self.conn = this_conn
        self.launch = launch.Launch(this_conn)
        self.circ = launch.Launch(this_conn)
        self.vessel = this_conn.space_center.active_vessel
        self.refframe = self.vessel.orbit.body.reference_frame
        self.flight = self.vessel.flight(self.refframe)
        self.canvas = this_conn.ui.add_canvas()
        self.screen_size = self.canvas.rect_transform.size
        self.vessel = this_conn.space_center.active_vessel
        self.panel = self.canvas.add_panel()
        self.rect_size = (200, 350)
        self.launch_button = self.panel.add_button('Launch')
        self.launch_button_clicked = this_conn.add_stream(getattr, self.launch_button, 'clicked')
        self.launch_button_size = (60, 20)

    def start(self):
        print("UI Start")
        self.build_panel()
        while True:
            if self.launch_button_clicked():
                self.launch.start(90, 100000)
                self.launch_button.clicked = False

    def build_panel(self):
        rect = self.panel.rect_transform
        rect.size = self.rect_size
        rect.position = ((self.rect_size[0] / 2) + 3 - (self.screen_size[0] / 2), (self.screen_size[1] / 2) - 220)

        self.launch_button.rect_transform.size = self.launch_button_size
        self.launch_button.rect_transform.position = self.rect_position(self.launch_button_size, (3, 3))

    def rect_position(self, size, position):
        return (int(position[0] - (self.rect_size[0] / 2) + (size[0] / 2))), (int((self.rect_size[1] / 2) -
                                                                                  (size[1] / 2) - position[1]))
