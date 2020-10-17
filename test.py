import ui
import server
import launch
import circularize
import deorbit

conn = server.Connect().conn
# deorbit = deorbit.Deorbit(conn)
# deorbit.deorbit()
launch = launch.Launch(conn)
launch.autostage()
