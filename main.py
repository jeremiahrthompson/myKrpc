import ui
import server


conn = server.Connect().conn
ui = ui.UserInterface(conn)
ui.start()
