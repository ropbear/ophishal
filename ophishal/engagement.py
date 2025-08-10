# ophishal/engagement/engagement.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
from ophishal.util import resolve_target
from ophishal.config import BaseConfig
from ophishal.models import Attachment
from ophishal.logging import create_logger

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def get_jinja_env(search_path: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(search_path)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

def _resolve_template_path(name_or_path: str) -> Path:
    p = Path(name_or_path)
    if p.exists():
        return p
    candidate = TEMPLATE_DIR / name_or_path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Template not found: {name_or_path}")


def _render_template(template: Path, params: dict) -> str:
    jinja_env = get_jinja_env(template.parent)
    try:
        tmpl = jinja_env.get_template(template.name)
    except TemplateNotFound as e:
        raise FileNotFoundError(f"Template not found: {template}") from e

    return tmpl.render(**params)

class Engagement(BaseConfig):
    require = {
        "campaign": str,
        "company": dict,
        "departments": list,
        "employees": list,
        "sender": str,
        "targets": list,
        "subject": str
    }
    logger = create_logger("engagement")


    def _parse(self, config: dict):
        self.subject = config["subject"]
        if "template" in config:
            self.template = _resolve_template_path(config["template"])
    
    def build(
        self,
        template: str | None = None,
        url: str | None = None,
        attachment: str | None = None, 
        attach_template: str | None = None,
        attach_params: dict | None = None
    ):
        """
        Sets the Engagement object html and attachment attributes using
        either the configuration file or the provided CLI arguments,
        or a combination of both.
        """
        #TODO: add ability to specify url and attachment attributes via config.json

        self.url = url
        if url is None:
            self.url = ""
            self.logger.warning("No URL for phishing infrastructure provided")

        # set attachment 
        if attachment is not None:
            self.attachment = _resolve_template_path(attachment)
        elif attach_template is not None:
            self.attach_template = _resolve_template_path(attach_template)
            self.attach_params = attach_params
            self.attachment = _render_template(self.attach_template, attach_params)
        else:
            self.attachment = None

        # set body
        if template is not None:
            self.template = _resolve_template_path(template)
        elif not hasattr(self, "template"):
            # template attribute was not set during _parse()
            self.logger.error("No template specified for building body")
            raise ValueError

        template_params = {
            "sender": self.sender,
            "targets": self.targets,
            "subject": self.subject,
            "url": self.url
        }
        self.body = _render_template(self.template, template_params)
