from pid_controllers.pid import PID
from abc import abstractmethod
from configparser import ConfigParser
from typing import List

class Tuner(PID):
    
    load_from_config = False

    @property
    def __init__(self, load_from_config: bool):
        self.load_from_config = load_from_config
    
    @property
    @abstractmethod
    def load_config(self, config: dict[str, float]):
        pass
    
    @property
    @abstractmethod
    def get_config_names(self) -> List[str]:
        pass
    
    def load_system_dynamics(self, tuner_instance) -> dict[str, float]:
        tuner_name = str.split(tuner_instance.__module__, '.')[-1].lower()
        tuner_instance.__load_config(tuner_name, tuner_instance.get_config_names())
    
    def store_system_dynamics(self, tuner_instance, config: dict[str, float]):
        tuner_name = str.split(tuner_instance.__module__, '.')[-1].lower()
        tuner_instance.__store_config(tuner_name, config)
        
    @staticmethod
    def load_tuner_config(section: str, names: List[str]) -> dict:
        config = ConfigParser()
        config.read("tuner_config.ini")
        conf = {}
        if config.has_section(section):
            for name in names:
                conf[name] = config.get(section, name)
        return conf

    @staticmethod
    def store_tuner_config(section: str, config_map: dict):
        config = ConfigParser()
        config.read("tuner_config.ini")
        if not config.has_section(section):
            config.add_section(section)
        for name, val in config_map.items():
            config.set(section, name, str(val))
        with open("tuner_config.ini", "w") as f:
            config.write(f)
            