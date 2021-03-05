import krpc


class Connect:
    def __init__(self):
        print("connecting")
        self.conn = krpc.connect()
        print("connected")
