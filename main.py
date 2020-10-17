import ui
import server
import launch
import circularize

# launch = launch.Launch()
# launch.start(90, 100000)
conn = server.Connect().conn
circ = circularize.Circularize(conn)
launch = launch.Launch(conn)
ui = ui.UserInterface(conn)
ui.start()
# circularize = circularize.Circularize(conn)
# circularize.circularize()
