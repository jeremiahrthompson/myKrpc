from modules import launch


class UserInterface:
    def __init__(self, conn):
        self.conn = conn
        self.launch = launch.Launch(conn)
        self.canvas = conn.ui.add_canvas()
        self.screen_size = self.canvas.rect_transform.size
        self.panel = self.canvas.add_panel()
        self.rect_size = (200, 200)
        self.launch_button = self.panel.add_button('Launch')
        self.launch_button_clicked = conn.add_stream(getattr, self.launch_button, 'clicked')
        self.launch_button_size = (60, 20)
        # self.circ_button = self.panel.add_button('Circularize')
        # self.circ_button_clicked = this_conn.add_stream(getattr, self.circ_button, 'clicked')
        # self.circ_button_size = (80, 20)
        # self.science_button = self.panel.add_button('Science')
        # self.science_button_clicked = this_conn.add_stream(getattr, self.science_button, 'clicked')
        # self.science_button_size = (60, 20)

    def start(self):
        self.build_panel()
        while True:
            if self.launch_button_clicked():
                self.launch_button.clicked = False
                self.launch.start(90, 100000)
            # if self.circ_button_clicked():
            #     self.circ_button.clicked = False
            #     self.circ.start()
            # if self.science_button_clicked():
            #     self.science_button.clicked = False
            #     self.science.start()

    def build_panel(self):
        rect = self.panel.rect_transform
        rect.size = self.rect_size
        rect.position = ((self.rect_size[0] / 2) + 3 - (self.screen_size[0] / 2), (self.screen_size[1] / 2) - 220)
        self.launch_button.rect_transform.size = self.launch_button_size
        self.launch_button.rect_transform.position = self.rect_position(self.launch_button_size, (3, 3))
        # self.circ_button.rect_transform.size = self.circ_button_size
        # self.circ_button.rect_transform.position = self.rect_position(self.circ_button_size, (66, 3))
        # self.science_button.rect_transform.size = self.science_button_size
        # self.science_button.rect_transform.position = self.rect_position(self.science_button_size, (3, 26))

    def rect_position(self, size, position):
        return (int(position[0] - (self.rect_size[0] / 2) + (size[0] / 2))), (int((self.rect_size[1] / 2) -
                                                                                  (size[1] / 2) - position[1]))
