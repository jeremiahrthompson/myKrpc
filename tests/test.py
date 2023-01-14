from modules import ui, server


conn = server.Connect().conn
ui = ui.UserInterface(conn)
ui.start()
