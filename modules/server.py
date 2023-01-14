import yaml
import krpc


class Connect:
    def __init__(self):
        self.config = self.get_configs()
        self.conn = self.get_connection()

    @staticmethod
    def get_configs():
        with open('configs/server.yaml', 'r') as infile:
            return yaml.safe_load(infile)

    def get_connection(self):
        return krpc.connect(name=self.config['name'],
                            address=self.config['address'],
                            rpc_port=self.config['rpc_port'],
                            stream_port=self.config['stream_port'])
