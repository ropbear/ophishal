# ophishal/cli.py
import sys
import argparse
from pathlib import Path
from logging import DEBUG, INFO
from importlib.metadata import version, PackageNotFoundError
from ophishal.engagement import Engagement
from ophishal.logging import create_logger


PKG_NAME = "ophishal"


def output_data(content: str, path: Path | None):
    if not path:
        sys.stdout.write(html)

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def cmd_render(args) -> int:
    logger = create_logger("main:render")
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
    print(eng.body)

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
    )
    pr.add_argument(
        "--url",
        help="The URL pointing to the phishing infrastructure"
    )

    return p

def main(argv: list[str] | None = None) -> int:
    # for cli testing purposes
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.very_verbose:
        logging.setLevel(logging.DEBUG)
    elif args.verbose:
        logging.setLevel(logging.INFO)

    if args.version:
        print(f"ophishal v{version(PKG_NAME)}")
        return 0

    match args.command:
        case "render":
            return cmd_render(args)
        case _:
            print(f"Unknown command {args.command}")
    parser.print_help()
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
