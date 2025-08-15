# ophishal/engagement/engagement.py
import json
from pathlib import Path
import jinja2
from ophishal.util import resolve_uid
from ophishal.config import BaseConfig
from ophishal.log import create_logger

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def get_jinja_env(search_path: Path) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(search_path)),
        undefined=jinja2.StrictUndefined,
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
    logger = create_logger("engagement:render_template")
    jinja_env = get_jinja_env(template.parent)
    try:
        tmpl = jinja_env.get_template(template.name)
    except jinja2.exceptions.TemplateNotFound as e:
        logger.error("Template not found: %s", template)
        return None
    try:
        return tmpl.render(**params)
    except jinja2.exceptions.UndefinedError as e:
        logger.error("Variable missing from template parameters: %s", e)
        return None


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


    def _parse(self, config: dict):
        logger = create_logger("Engagement.parse")
        # required
        self.subject = config["subject"]

        # optional, can also be specified via command line which will override these values
        if "template" in config:
            self.template = _resolve_template_path(config["template"])
            logger.debug("Added template from configuration file")
        if "url" in config:
            self.url = config["url"]
            logger.debug("Added url from configuration file")
        if "attach_template" in config:
            self.attach_template = _resolve_template_path(config["attach_template"])
            logger.debug("Added attachment template from configuration file")
        if "attach_params" in config:
            self.attach_params = config["attach_params"]
            logger.debug("Added attachment template parameters from configuration file")
        if "attachment_file" in config:
            self.attachment = _resolve_template_path(config["attachment_file"]).read_bytes()
            logger.debug("Added attachment file from configuration file")
        if "server" in config:
            self.server = config["server"]
            logger.debug("Added server from configuration file")

    def build(
        self,
        template: str | None = None,
        url: str | None = None,
        attachment: str | None = None, 
        attach_template: str | None = None,
        attach_params: dict | None = None,
        server: str | None = None
    ):
        """
        Sets the Engagement object html and attachment attributes using
        either the configuration file or the provided CLI arguments,
        or a combination of both.
        """
        logger = create_logger("Engagement.build")

        if server is not None:
            self.server = server
        elif not hasattr(self, "server"):
            logger.error("No server specified, cannot send email")

        if url is not None:
            self.url = url
        elif not hasattr(self, "url"):
            self.url = ""
            logger.warning("No URL for phishing infrastructure provided")

        # allow attachment param to override all
        if attachment is not None:
            self.attachment = _resolve_template_path(attachment).read_bytes()
        elif attach_template is not None:
            self.attach_template = _resolve_template_path(attach_template)
            if attach_params is not None:
                self.attach_params = json.loads(attach_params)
            elif self.attach_params is None:
                self.attach_params = {}

        if self.attach_template is not None and not hasattr(self, "attachment"):
            self.attachment = _render_template(
                self.attach_template,
                self.attach_params
            )
            if self.attachment is None:
                logger.error("Failed to create attachment, no attachment")
            else:
                self.attachment = self.attachment.encode("utf-8")
        if not hasattr(self, "attachment"):
            self.attachment = None


        # set body
        if template is not None:
            self.template = _resolve_template_path(template)
        elif not hasattr(self, "template"):
            # template attribute was not set during _parse()
            logger.error("No template specified for building body")
            raise ValueError

        template_params = {
            "sender": self.sender,
            "targets": self.targets,
            "subject": self.subject,
            "url": self.url
        }
        self.body = _render_template(self.template, template_params)
        logger.debug("Created HTML body from template %s", self.template)