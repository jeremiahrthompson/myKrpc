from modules import ui
from modules import server


conn = server.Connect().conn
ui = ui.UserInterface(conn)
ui.start()
