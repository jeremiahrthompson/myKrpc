import os
import yaml


class Data:
    @staticmethod
    def get_active_vessel_params(name, version):
        # Checking if the configs/vessels directory exist or not
        if not os.path.exists("configs/vessels"):
            print("Error: configs/vessels directory not found.")
            return None
        try:
            # Opening the config file for the specific vessel and version
            with open(f"configs/vessels/{name}-{version}.yaml", "r") as infile:
                # Loading and returning the configuration
                return yaml.safe_load(infile)
        except FileNotFoundError:
            # If the config file not found
            print(f"Error: config file for vessel {name}-{version} not found.")
            return None
        except yaml.YAMLError as exc:
            # If there is a problem parsing the YAML file
            print(f"Error: Failed to parse YAML config file for vessel {name}-{version}")
            print(exc)
            return None

    @staticmethod
    def get_server_config():
        # Checking if the configs' directory exists or not
        if not os.path.exists("configs"):
            print("Error: configs directory not found.")
            return None
        try:
            # Opening the config file for the server
            with open("configs/server.yaml", "r") as infile:
                # Loading and returning the configuration
                return yaml.safe_load(infile)
        except FileNotFoundError:
            # If the config file not found
            print("Error: config file for server not found.")
            return None
        except yaml.YAMLError as exc:
            # If there is a problem parsing the YAML file
            print("Error: Failed to parse YAML config file for server")
            print(exc)
            return None
