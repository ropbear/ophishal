# ophishal/cli.py
import sys
import argparse
from pathlib import Path
from logging import DEBUG, INFO
from importlib.metadata import version, PackageNotFoundError
from ophishal.engagement import Engagement
from ophishal.log import create_logger, setLogLevel
from ophishal.email import send_email

PKG_NAME = "ophishal"


def output_data(content: str | bytes, path: str | None):
    logger = create_logger("main:output")
    logger.debug("Attempting to write to %s", path)
    if path is None or path == "-":
        logger.info("Writing to stdout")
        if type(content) == str:
            sys.stdout.write(content)
        else:
            sys.stdout.buffer.write(content)
        return

    path = Path(path)

    if path.exists():
        logger.warning("File already exists: %s", path)

    if type(content) == bytes:
        with open(path, "wb") as f:
            f.write(content)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

def cmd_email(args) -> int:
    logger = create_logger("main:email")
    eng = Engagement(filepath=Path(args.config))

    logger.debug("Calling Enagement.build()")
    eng.build(
        template=args.template,
        url=args.url,
        attachment=args.attachment,
        attach_template=args.attach_template,
        attach_params=args.attach_params
    )
    logger.debug("Engagement.build() complete")
    if args.attach_template is not None and eng.attachment is None:
        logger.warning("No attachment generated from template")
    logger.info("Built engagement")

    if args.output_email is not None:
        output_data(eng.body, args.output_email)
    
    if args.output_attach is not None:
        output_data(eng.attachment, args.output_attach)

    if args.output_only:
        return 0
    return send_email()


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
        "email",
        help="Build a phishing email from the command line or configuration file"
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
        "--attachment",
        help="Use an existing file as attachment (pass-through, no variable replacement)"
    )
    pr.add_argument(
        "--attach-template",
        help="Use a template for an attachment"
    )
    pr.add_argument(
        "--attach-params",
        help="Parameters to send use with Jinja to fill in the template"
    ) #TODO: make dependent on --attach-template
    pr.add_argument(
        "--url",
        help="The URL pointing to the phishing infrastructure"
    )
    pr.add_argument(
        "--output-only",
        action="store_true",
        help="Do not send an email, only output the render results"
    )
    pr.add_argument(
        "--output-email",
        help="File to write rendered email to"
    )
    pr.add_argument(
        "--output-attach",
        help="File to write rendered attachment to"
    )
    return p

def main(argv: list[str] | None = None) -> int:
    # for cli testing purposes
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.very_verbose:
        setLogLevel(DEBUG)
    elif args.verbose:
        setLogLevel(INFO)

    if args.version:
        print(f"ophishal v{version(PKG_NAME)}")
        return 0

    match args.command:
        case "email":
            return cmd_email(args)
        case _:
            print(f"Unknown command {args.command}")
    parser.print_help()
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
