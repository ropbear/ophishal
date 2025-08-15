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
    logger = create_logger("output_data")
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
    logger = create_logger("command:email")
    eng = Engagement(filepath=Path(args.config))

    if eng is None:
        logger.critical("Failed to create Engagement object")
        return 1

    logger.debug("Calling Enagement.build()")
    # parsing of individual arguments handled in Engagement.build()
    eng.build(
        template=args.template,
        url=args.url,
        attachment=args.attachment,
        attach_template=args.attach_template,
        attach_params=args.attach_params,
        server=args.server
    )
    logger.debug("Engagement.build() complete")

    if args.attach_template is not None and eng.attachment is None:
        logger.warning("No attachment generated from template")
    logger.info("Built engagement")

    if eng.body is None:
        logger.error("Failed to create email body, halting")
        return 1

    if eng.attachment is None and eng.attach_template is not None:
        logger.warning("Failed to create attachment from template")
        return 1

    if args.output_body is not None:
        output_data(eng.body, args.output_body)
    
    if args.output_attach is not None:
        output_data(eng.attachment, args.output_attach)

    if args.dryrun:
        return 0
    if hasattr(eng, "server"):
        return send_email(eng)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ophishal",
        description="Automate phishing engagements with JSON configuration and Jinja templates"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose (INFO)"
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        action="store_true",
        help="Very verbose (DEBUG)"
    )

    cmds = parser.add_subparsers(
        dest="command",
        required=False
    )

    email_parser = cmds.add_parser(
        "email",
        help="Build a phishing email from the command line or configuration file"
    )
    email_parser.add_argument(
        "--config",
        required=True,
        help="Path to configuration file"
    )
    email_parser.add_argument(
        "--template",
        help="Override HTML template file (path or name in package templates)"
    )
    email_parser.add_argument(
        "--attachment",
        help="Use an existing file as attachment (pass-through, no variable replacement)"
    )
    email_parser.add_argument(
        "--attach-template",
        help="Use a template for an attachment"
    )
    email_parser.add_argument(
        "--attach-params",
        help="Parameters to send use with Jinja to fill in the template"
    )
    email_parser.add_argument(
        "--server",
        help="The server used to deliver the phish"
    )
    email_parser.add_argument(
        "--url",
        help="The URL pointing to the phishing infrastructure"
    )
    email_parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Do not send an email"
    )
    email_parser.add_argument(
        "--output-body",
        help="File to write rendered html body to"
    )
    email_parser.add_argument(
        "--output-attach",
        help="File to write rendered attachment to"
    )
    return parser

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
