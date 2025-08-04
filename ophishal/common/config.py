# common/config.py
import json
from pathlib import Path


class BaseConfig:
    require = {}
    def __init__(self, config:dict=None, filepath:Path=None):
        if filepath is not None and config is not None:
            raise ValueError("Can't have both config and filepath")

        if filepath is not None and isinstance(filepath, Path):
            if filepath.exists():
                config = self.__from_file(filepath)
            else:
                raise FileNotFoundError("Configuration file does not exist")
        
        if config is not None and isinstance(config, dict):
            for key in self.require.keys():
                if key not in config.keys():
                    raise AttributeError(
                        "Configuration missing keys: " + \
                        f"{list(set(self.require.keys()) - set(config.keys()))}"
                    )
                elif not isinstance(config[key], self.require[key]):
                    raise TypeError(
                        f"Key '{key}' should be  of type {self.require[key]}" + \
                        f", got {type(config[key])}"
                    )
        else:
            raise ValueError("No valid configuration parameter specified")

        self.parse(config)

    def __from_file(self, filepath:Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def parse(self, config:dict):
        """
        Classes which inherit this base class will use this function to
        parse out the details they need from the dictionary.
        """
        pass