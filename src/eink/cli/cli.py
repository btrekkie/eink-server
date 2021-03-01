from argparse import ArgumentParser
import sys

from ..generate import ServerCodeGenerator
from ..server.simulator import Simulator


class Cli:
    """Implements a command-line interface for certain utilities."""

    @staticmethod
    def exec(cli_args):
        """Execute a command-line operation.

        Arguments:
            cli_args (list<str>): The arguments, excluding the program.
        """
        parsed_args = Cli._parse_args(cli_args)
        if parsed_args.command == 'skeleton':
            ServerCodeGenerator.gen_skeleton()
        else:
            Simulator.connect(parsed_args.url).show()

    @staticmethod
    def _parse_args(cli_args):
        """Return the results of parsing the specified command-line arguments.

        Arguments:
            cli_args (list<str>): The arguments, excluding the program.

        Returns:
            Namespace: The results.
        """
        parser = ArgumentParser(
            description='Utilities for the eink-server Python library.',
            prog='einkserver')
        subparsers = parser.add_subparsers(dest='command')
        subparsers.add_parser(
            'skeleton',
            description='Generate skeleton code for an e-ink server.')
        connect_parser = subparsers.add_parser(
            'connect',
            description='Connect to an e-ink server, and display what would '
            'be shown on the e-ink display.')
        connect_parser.add_argument(
            'url', help='the server URL to connect to', metavar='URL')

        parsed_args = parser.parse_args(cli_args)
        if parsed_args.command is None:
            # Ideally, we would use required=True instead. But that isn't
            # available until Python 3.7, and it's not worth increasing the
            # required version of Python.
            print(parser.format_usage(), end='', file=sys.stderr)
            print(
                'einkserver: error: the following arguments are required: '
                'command',
                file=sys.stderr)
            sys.exit(1)
        return parsed_args


def eink_server_cli():
    """Execute a command-line operation using the arguments ``sys.argv[1:]``.
    """
    Cli.exec(sys.argv[1:])


if __name__ == '__main__':
    eink_server_cli()
