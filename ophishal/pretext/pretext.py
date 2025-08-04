# pretext/pretext.py
from pathlib import Path
from dataclasses import dataclass
from ophishal.context.context import Context
from ophishal.common.config import BaseConfig

class Pretext(BaseConfig):
    require = {
        "campaign_identifier":str,
        "vector":str,
        "source":dict,
        "targets":list,
        "persuasion_mechanisms":list,
        "language":str,
        "language_style":list,
        "topic":str,
        "phish_type":str,
        "email_subject":str,
        "email_body":str,
        "selected_template":str,
        "attachment":str
    }
    def parse(self, config:dict):

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


@dataclass
class PretextSource:
    type: str
    uid: str


@dataclass
class Target:
    type: str
    uid: str