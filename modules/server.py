import krpc
from modules import data


class Connect:
    def __init__(self):
        self.data = data.Data()
        self.config = self.data.get_server_config()
        self.conn = self.get_connection()

    def get_connection(self):
        # Check that config variable is a dictionary and that it contains the correct keys
        if not isinstance(self.config, dict) or not all(k in self.config for k in ('name', 'address', 'rpc_port', 'stream_port')):
            raise ValueError("Missing required attribute(s) in self object.")
        # Check that each key in the config variable is not None
        if not all(self.config.get(k) is not None for k in ('name', 'address', 'rpc_port', 'stream_port')):
            raise ValueError("Missing required attribute(s) in self object.")
        # Attempt to connect with provided parameters
        return krpc.connect(name=self.config['name'],
                            address=self.config['address'],
                            rpc_port=self.config['rpc_port'],
                            stream_port=self.config['stream_port'])
