from modules import launch, data
import time


class UserInterface:
    def __init__(self, conn):
        self.conn = conn
        self.data = data.Data()
        self.gamescene = self.get_gamescene()
        self.active_vessel = self.get_active_vessel()
        self.active_vessel_full_name = self.get_active_vessel_full_name()
        self.active_vessel_name = self.get_active_vessel_name()
        self.active_vessel_version = self.get_active_vessel_version()
        self.active_vessel_situation = self.get_active_vessel_situation()
        self.active_vessel_params = self.get_active_vessel_params()
        self.launch = False

    def get_gamescene(self):
        return self.conn.krpc.current_game_scene

    def get_active_vessel(self):
        return self.conn.space_center.active_vessel

    def get_active_vessel_full_name(self):
        if self.active_vessel is not None:
            return self.active_vessel.name
        return None

    def get_active_vessel_name(self):
        if self.active_vessel_full_name is not None:
            return self.active_vessel_full_name.split('-')[0]
        return None

    def get_active_vessel_version(self):
        if self.active_vessel_full_name is not None:
            return self.active_vessel_full_name.split('-')[1]
        return None

    def get_active_vessel_situation(self):
        if self.active_vessel is not None:
            return self.active_vessel.situation
        return None

    def get_active_vessel_params(self):
        if self.active_vessel_name and self.active_vessel_version is not None:
            return self.data.get_active_vessel_params(self.active_vessel_name, self.active_vessel_version)

    def assess_launch(self):
        if self.gamescene is not None:
            if self.gamescene == self.gamescene.flight:
                if self.active_vessel_situation is not None:
                    if self.active_vessel_situation == self.active_vessel.situation.pre_launch:
                        return True

    def start(self):
        self.launch = self.assess_launch()
        canvas = self.conn.ui.add_canvas()
        screen_size = canvas.rect_transform.size
        panel = canvas.add_panel()
        rect = panel.rect_transform
        rect_size = (80, 30)
        rect.position = ((rect_size[0] / 2) + 3 - (screen_size[0] / 2), (screen_size[1] / 2) - 220)
        launch_button_clicked = lambda: False
        launch_button = lambda: False
        if self.launch:
            launch_button_size = (60, 20)
            launch_button = panel.add_button('Launch')
            launch_button_clicked = self.conn.add_stream(getattr, launch_button, 'clicked')
            launch_button.rect_transform.size = launch_button_size
            launch_button.rect_transform.position = self.rect_position(launch_button_size, (3, 3), rect_size)
        while True:
            if self.launch:
                if launch_button_clicked():
                    launch_button.clicked = False
                    launch_module = launch.Launch(self.conn, self.active_vessel_params)
                    launch_module.start()
            time.sleep(0.01)

    @staticmethod
    def rect_position(size, position, rect_size):
        return (int(position[0] - (rect_size[0] / 2) + (size[0] / 2))), (int((rect_size[1] / 2) -
                                                                             (size[1] / 2) - position[1]))
