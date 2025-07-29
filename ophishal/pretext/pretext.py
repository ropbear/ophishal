import json
from pathlib import Path
from dataclasses import dataclass

class Pretext:
    def __init__(self, config:dict=None, filepath:Path=None):
        if filepath is not None and config is not None:
            raise ValueError("Can't have both config and filepath")
        elif filepath is not None:
            config = self.__from_file(filepath)

        self.source = PretextSource(**config["source"])
        self.targets = [Target(**t) for t in config["targets"]]

        self.campaign_identifier    = config["campaign_identifier"]
        self.vector                 = config["vector"]
        self.persuasion_mechanisms  = config["persuasion_mechanisms"]
        self.language_style         = config["language_style"]
        self.topic                  = config["topic"]
        self.phish_type             = config["phish_type"]
        self.email_subject          = config["email_subject"]
        self.email_body             = config["email_body"]
        self.selected_template      = config["selected_template"]

    def __from_file(self, filepath:Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)


@dataclass
class PretextSource:
    type: str
    uid: str


@dataclass
class Target:
    type: str
    uid: str