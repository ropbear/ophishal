# ophishal/cli.py
import sys
import argparse
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
from ophishal.engagement.engagement import Engagement


PKG_NAME = "ophishal"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def resolve_template_path(name_or_path: str) -> Path:
    p = Path(name_or_path)
    if p.exists():
        return p
    candidate = TEMPLATE_DIR / name_or_path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Template not found: {name_or_path}")

def get_jinja_env(search_path: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(search_path)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

def generate_html_from_template(eng: Engagement, args: object) -> str:
    template_path = Path(args.template) if args.template is not None else eng.template
    env = get_jinja_env(template_path.parent)
    try:
        tmpl = env.get_template(template_path.name)
    except TemplateNotFound as e:
        raise FileNotFoundError(f"Template not found: {template_path}") from e

    return tmpl.render(
        sender=eng.sender,
        target=eng.targets[0].first_name if len(eng.targets) == 1 else "all",
        subject=eng.subject,
        url=args.malicious_url
    )

def generate_attachment_from_template(eng: Engagement, args: object) -> str:
    template_path = resolve_template_path(args.attach_template)
    env = get_jinja_env(template_path.parent)
    try:
        tmpl = env.get_template(template_path.name)
    except TemplateNotFound as e:
        raise FileNotFoundError(f"Attachment template not found: {template_path}") from e

    return tmpl.render(**args.attach_params)

def output_data(content: str, path: Path | None):
    if not path:
        sys.stdout.write(html)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def cmd_render(args) -> int:
    eng = Engagement(filepath=Path(args.config))

    html = generate_html_from_template(eng, args)

    #TODO: properly pass through attachment
    if args.attach_template:
        attachment = generate_attachment_from_template(eng, args)
        if args.out_attach:
            print(attachment)
        else:
            print("Attachment generated (use --out-attach to write to a file).")

    if args.attach:
        if args.out_attach:
            src = Path(args.attach)
            if not src.exists():
                raise FileNotFoundError(f"Attachment not found: {src}")
            print(src.read_text(encoding="utf-8"))
        else:
            print("Attachment provided (use --out-attach to write to a file).")

    print(html)



    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ophishal",
        description="Automate phishing engagements with JSON configuration and Jinja templates"
    )
    p.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose (INFO)"
    )
    p.add_argument(
        "-vv",
        "--very-verbose",
        action="store_true",
        help="Very verbose (DEBUG)"
    )

    sub = p.add_subparsers(
        dest="command",
        required=False
    )

    pr = sub.add_parser(
        "render",
        help="Build the phishing lure from a configuration file and command line options"
    )
    pr.add_argument(
        "--config",
        required=True,
        help="Path to configuration file"
    )
    pr.add_argument(
        "--template",
        help="Override HTML template file (path or name in package templates)"
    )
    pr.add_argument(
        "--attach",
        help="Use an existing file as attachment (pass-through, no variable replacement)"
    )
    pr.add_argument(
        "--attach-template",
        help="Use a template for an attachment"
    )
    pr.add_argument(
        "--attach-params",
        help="Parameters to send use with Jinja to fill in the template"
    )
    pr.add_argument(
        "--malicious-url",
        help="The URL pointing to the phishing infrastructure"
    )

    return p

def main(argv: list[str] | None = None) -> int:
    # for cli testing purposes
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(version(PKG_NAME))

    match args.command:
        case "render":
            return cmd_render(args)
        case _:
            print(f"Unknown command {args.command}")
    parser.print_help()
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
