import functools
import getpass
import json
import os
import re
import shutil
import socket
import string
import subprocess
import sys
from urllib.parse import urlparse

from .client_code_generator import ClientCodeGenerator
from .client_config import ClientConfig
from ..project.project import Project
from .rotation import Rotation
from .status_images import StatusImages
from .web_transport import WebTransport


class ServerCodeGenerator:
    """Generates skeleton code for an e-ink server."""

    @staticmethod
    def gen_skeleton():
        """Generate skeleton code for an e-ink server.

        We request information about the server using standard input and
        output.
        """
        ServerCodeGenerator._gen_skeleton(
            *ServerCodeGenerator._input_skeleton_params())

    @staticmethod
    def _input(prompt, default, validation_func, hidden=False):
        """Prompt the user for a string input.

        The basic procedure is something like this:

        * Display the prompt.
        * If nothing is entered, return the default value.
        * Otherwise, validate the value using validation_func.
        * If valid, return the value entered.
        * If invalid, print an error message and repeat.

        However, the ``_input`` method is responsible for the details.

        Arguments:
            prompt (str): Text to present to the user indicating what
                information to enter.
            default (str): The value to return if the user enters the
                empty string. If this is ``None``, then we return
                ``''``.
            validation_func (callable): A function for validating the
                result. If it raises a ``RuntimeError`` when we pass in
                the value the user entered, then that value is not
                permitted. Such errors should have messages that are
                suitable to display to the user.
            hidden (bool): Whether to hide the user's input as he enters
                it. This is useful for passwords.

        Returns:
            str: The value the user entered, or the default value.
        """
        if default is None:
            default = ''
        if prompt.endswith('\n'):
            prompt_with_default = '{:s}[{:s}] '.format(prompt, default)
        else:
            prompt_with_default = '{:s} [{:s}] '.format(prompt, default)

        while True:
            if hidden:
                value = getpass.getpass(prompt_with_default)
            else:
                value = input(prompt_with_default)

            if value == '':
                return default
            elif validation_func is None:
                return value

            try:
                validation_func(value)
            except RuntimeError as error:
                print()
                print(error.message)
                print()
            else:
                return value

    @staticmethod
    def _normalize_filename(filename):
        """Equivalent implementation is contractually guaranteed."""
        return os.path.abspath(os.path.expanduser(filename))

    @staticmethod
    def _validate_server_dir(dir_):
        """Validate the server directory.

        Raise a ``RuntimeError`` if the specified user entry is not a
        valid server directory.

        Arguments:
            dir_ (str): The user entry.
        """
        try:
            absolute_dir = ServerCodeGenerator._normalize_filename(dir_)
        except OSError:
            raise RuntimeError(
                'Error normalizing the filename {:s}'.format(dir_))

        parent = os.path.dirname(absolute_dir)
        if not os.path.isdir(parent):
            raise ValueError(
                'The parent folder {:s} does not exist'.format(parent))

    @staticmethod
    def _validate_client_dir(server_dir, dir_):
        """Validate the client directory.

        Raise a ``RuntimeError`` if the specified user entry is not a
        valid client directory.

        Arguments:
            server_dir (str): The server directory.
            dir_ (str): The user entry.
        """
        try:
            absolute_dir = ServerCodeGenerator._normalize_filename(dir_)
        except OSError:
            raise RuntimeError(
                'Error normalizing the filename {:s}'.format(dir_))

        try:
            if (absolute_dir ==
                    ServerCodeGenerator._normalize_filename(server_dir)):
                raise ValueError(
                    'The client code directory may not be the same as the '
                    'server code directory')
        except OSError:
            pass

        parent = os.path.dirname(absolute_dir)
        try:
            if parent == ServerCodeGenerator._normalize_filename(server_dir):
                return
        except OSError:
            pass

        if not os.path.isdir(parent):
            raise ValueError(
                'The parent folder {:s} does not exist'.format(parent))

    @staticmethod
    def _validate_url(url):
        """Validate the server URL.

        Raise a ``ValueError`` if the specified user entry is not a
        valid server URL.

        Arguments:
            url (str): The user entry.
        """
        scheme = urlparse(url).scheme
        if scheme == 'https':
            raise ValueError(
                'The URL must begin with http://. HTTPS is currently not '
                'supported.')
        elif scheme != 'http':
            raise ValueError('The URL must begin with http://')

    @staticmethod
    def _validate_non_empty(value):
        """Validate an input that may not be empty.

        Raise a ``ValueError`` if the specified user entry is the empty
        string.

        Arguments:
            value (str): The user entry.
        """
        if not value:
            raise ValueError('Please enter a value')

    @staticmethod
    def _validate_rotation(rotation_str):
        """Validate the rotation.

        Raise a ``ValueError`` if the specified user entry is not a
        valid device rotation.

        Arguments:
            rotation_str (str): The user entry.
        """
        if rotation_str not in ['1', '2', '3', '4']:
            raise ValueError('The rotation must be 1 - 4')

    @staticmethod
    def _validate_positive_int(value):
        """Validate a positive integer.

        Raise a ``ValueError`` if the specified user entry is not a
        positive integer.

        Arguments:
            value (str): The user entry.
        """
        if not re.search(r'^[1-9]\d*$', value):
            raise ValueError('Please enter a positive integer')

    @staticmethod
    def _local_ip_address():
        """Return the device's local IP address, e.g. ``'192.168.1.70'``."""
        # Based on https://stackoverflow.com/a/28950776/10935386
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
        except InterruptedError:
            return '127.0.0.1'
        finally:
            s.close()

    @staticmethod
    def _ssid():
        """Return the SSID for the Wi-Fi network we are connected to, if any.

        Return ``None`` if we were unable to determine the SSID.
        """
        if os.name == 'nt' or sys.platform == 'darwin':
            if os.name == 'nt':
                command = ['Netsh', 'WLAN', 'show', 'interfaces']
            else:
                command = [
                    '/System/Library/PrivateFrameworks/Apple80211.framework/'
                    'Resources/airport',
                    '-I']

            try:
                output = subprocess.check_output(command).decode()
            except (
                    OSError, subprocess.CalledProcessError,
                    UnicodeDecodeError):
                return None
            for line in output.split('\n'):
                stripped_line = line.strip()
                if stripped_line.startswith('SSID'):
                    index = stripped_line.index(':')
                    return stripped_line[index + 2:]
            return None
        else:
            try:
                output = subprocess.check_output([
                    '/sbin/iwgetid', '-r']).decode()
            except (
                    OSError, subprocess.CalledProcessError,
                    UnicodeDecodeError):
                return None
            ssid = output.rstrip('\n')
            if ssid:
                return ssid
            else:
                return None

    @staticmethod
    def _input_skeleton_params():
        """Prompt the user for all of the parameters to ``_gen_skeleton``.

        The return value is a tuple with all of those parameters, in
        order.
        """
        local_ip_address = ServerCodeGenerator._local_ip_address()
        connected_ssid = ServerCodeGenerator._ssid()
        if os.name == 'nt':
            default_server_dir = os.path.join(
                os.path.expanduser('~'), 'Documents', 'eink_server')
        else:
            default_server_dir = os.path.join('~', 'eink_server')

        server_dir = ServerCodeGenerator._input(
            'Directory for the server code', default_server_dir,
            ServerCodeGenerator._validate_server_dir)
        client_dir = ServerCodeGenerator._input(
            'Directory for the client code',
            os.path.join(server_dir, 'client'),
            functools.partial(
                ServerCodeGenerator._validate_client_dir, server_dir))
        url = ServerCodeGenerator._input(
            'Server URL',
            'http://{:s}:5000/eink_server'.format(local_ip_address),
            ServerCodeGenerator._validate_url)
        ssid = ServerCodeGenerator._input(
            'Wi-Fi SSID for device to connect to', connected_ssid,
            ServerCodeGenerator._validate_non_empty)
        wi_fi_password = ServerCodeGenerator._input(
            'Password for Wi-Fi (leave blank if none)', None, None, True)

        rotation_str = ServerCodeGenerator._input(
            'Device rotation:\n'
            '1) Portrait right (bottom of device on right)\n'
            '2) Landscape upside down\n'
            '3) Portrait left (bottom of device on left)\n'
            '4) Landscape\n',
            '4', ServerCodeGenerator._validate_rotation)

        default_width = '800'
        default_height = '600'
        if (rotation_str == str(Rotation.LANDSCAPE.value) or
                rotation_str == str(Rotation.LANDSCAPE_UPSIDE_DOWN.value)):
            width_prompt = 'Device width in pixels'
            height_prompt = 'Device height in pixels'
        else:
            width_prompt = 'Device width in pixels, after rotation'
            height_prompt = 'Device height in pixels, after rotation'
            default_width, default_height = default_height, default_width
        width = ServerCodeGenerator._input(
            width_prompt, default_width,
            ServerCodeGenerator._validate_positive_int)
        height = ServerCodeGenerator._input(
            height_prompt, default_height,
            ServerCodeGenerator._validate_positive_int)
        return (
            server_dir, client_dir, url, ssid, wi_fi_password, rotation_str,
            width, height)

    @staticmethod
    def _eval_template(server_dir, filename, params):
        """Evaluate a source code template.

        This reads the template at
        assets/server_skeleton/[filename].tpl, performs string
        substitutions using ``string.Template.substitute(params)``, and
        stores the result in [server_dir]/[filename].

        Arguments:
            server_dir (str): The directory in which to store the
                resulting file.
            filename (str): The filename of the resulting file,
                excluding the directory.
            params (dict<str, str>): The parameters to the template.
        """
        input_filename = os.path.join(
            Project.server_skeleton_dir(), '{:s}.tpl'.format(filename))
        with open(input_filename, 'r') as file:
            template = file.read()

        contents = string.Template(template).substitute(params)
        output_filename = os.path.join(server_dir, filename)
        with open(output_filename, 'w') as file:
            file.write(contents)

    @staticmethod
    def _write_gen_client_code(
            server_dir, client_dir, url, ssid, wi_fi_password, rotation):
        """Write the contents of the gen_client_code.py file.

        This contains code for generating the client's source code.

        Arguments:
            server_dir (str): The directory in which to store the
                resulting file.
            client_dir (str): The directory in which the client code is
                stored.
            url (str): The server's URL.
            ssid (str): The SSID of the Wi-Fi network that the client
                should connect to.
            wi_fi_password (str): The password of the Wi-Fi network that
                the client should connect to. If this is ``''``, then
                there is no password.
            rotation (Rotation): The rotation to use when drawing to the
                Inkplate device.
        """
        import_os = ''
        import_separator = ''
        if not wi_fi_password:
            wi_fi_password_code = 'None'
            import_json = ''
            read_secrets = ''
        else:
            wi_fi_password_code = "_read_secrets()['wiFiPassword']"
            import_json = '\nimport json'
            import_os = '\nimport os'
            import_separator = '\n'
            read_secrets = (
                '\ndef _read_secrets():\n'
                '    """Return the JSON value stored in '
                'assets/secrets.json."""\n'
                '    project_dir = '
                'os.path.dirname(os.path.abspath(__file__))\n'
                '    secrets_filename = '
                "os.path.join(project_dir, 'assets', 'secrets.json')\n"
                "    with open(secrets_filename, 'r') as file:\n"
                '        return json.load(file)\n\n')

        if rotation == Rotation.LANDSCAPE:
            set_rotation = ''
            import_rotation = ''
        else:
            set_rotation = '\n    config.set_rotation(Rotation.{:s})'.format(
                rotation.name)
            import_rotation = 'from eink.generate import Rotation\n'

        if os.path.dirname(client_dir) != server_dir:
            set_client_dir = '    dir_ = {:s}'.format(repr(client_dir))
        else:
            set_client_dir = (
                '    project_dir = '
                'os.path.dirname(os.path.abspath(__file__))\n'
                '    dir_ = os.path.join(project_dir, {:s})'.format(
                    repr(os.path.basename(client_dir))))
            import_os = '\nimport os'
            import_separator = '\n'

        ServerCodeGenerator._eval_template(
            server_dir, 'gen_client_code.py', {
                'import_json': import_json,
                'import_os': import_os,
                'import_rotation': import_rotation,
                'import_separator': import_separator,
                'read_secrets': read_secrets,
                'set_client_dir': set_client_dir,
                'set_rotation': set_rotation,
                'ssid': repr(ssid),
                'url': repr(url),
                'wi_fi_password': wi_fi_password_code,
            })

    @staticmethod
    def _gen_client_code(
            client_dir, url, ssid, wi_fi_password, rotation, width, height):
        """Generate the client code for the skeleton.

        Arguments:
            client_dir (str): The directory in which to store the client
                code.
            url (str): The server's URL.
            ssid (str): The SSID of the Wi-Fi network that the client
                should connect to.
            wi_fi_password (str): The password of the Wi-Fi network that
                the client should connect to. If this is ``''``, then
                there is no password.
            rotation (Rotation): The rotation to use when drawing to the
                Inkplate device.
            width (str): The width of the Inkplate device, as a string,
                after applying the rotation suggested by ``rotation``.
            height (str): The height of the Inkplate device, as a
                string, after applying the rotation suggested by
                ``rotation``.
        """
        status_images = StatusImages.create_default(int(width), int(height))
        config = ClientConfig(WebTransport(url), status_images)
        if wi_fi_password:
            config.add_wi_fi_network(ssid, wi_fi_password)
        else:
            config.add_wi_fi_network(ssid, None)
        config.set_rotation(rotation)
        ClientCodeGenerator.gen(config, client_dir)

    @staticmethod
    def _gen_skeleton(
            server_dir, client_dir, url, ssid, wi_fi_password, rotation_str,
            width, height):
        """Generate a skeleton server.

        Arguments:
            server_dir (str): The directory in which to store the
                server.
            client_dir (str): The directory in which to store the client
                code.
            url (str): The server's URL.
            ssid (str): The SSID of the Wi-Fi network that the client
                should connect to.
            wi_fi_password (str): The password of the Wi-Fi network that
                the client should connect to. If this is ``''``, then
                there is no password.
            rotation_str (str): The rotation to use when drawing to the
                Inkplate device. This is the string representation of
                the value of the relevant ``Rotation``.
            width (str): The width of the Inkplate device, as a string,
                after applying the rotation suggested by
                ``rotation_str``.
            height (str): The height of the Inkplate device, as a
                string, after applying the rotation suggested by
                ``rotation_str``.
        """
        server_dir = ServerCodeGenerator._normalize_filename(server_dir)
        assets_dir = os.path.join(server_dir, 'assets')
        client_dir = ServerCodeGenerator._normalize_filename(client_dir)
        if not os.path.exists(server_dir):
            os.mkdir(server_dir)
        if not os.path.exists(assets_dir):
            os.mkdir(assets_dir)
        if not os.path.exists(client_dir):
            os.mkdir(client_dir)

        ServerCodeGenerator._eval_template(
            server_dir, 'my_server.py', {
                'height': height,
                'width': width,
            })

        parsed_url = urlparse(url)
        if parsed_url.path:
            path = parsed_url.path
        else:
            path = '/'
        ServerCodeGenerator._eval_template(
            server_dir, 'app.py', {'path': repr(path)})

        shutil.copy(
            os.path.join(Project.server_skeleton_dir(), 'requirements.txt'),
            os.path.join(server_dir, 'requirements.txt'))
        shutil.copy(
            os.path.join(Project.server_skeleton_dir(), 'GentiumPlus-R.ttf'),
            os.path.join(assets_dir, 'GentiumPlus-R.ttf'))
        shutil.copy(
            os.path.join(Project.server_skeleton_dir(), 'OFL.txt'),
            os.path.join(assets_dir, 'OFL.txt'))

        if wi_fi_password:
            secrets = {'wiFiPassword': wi_fi_password}
            with open(os.path.join(assets_dir, 'secrets.json'), 'w') as file:
                file.write(json.dumps(secrets, indent=4))
                file.write('\n')

        rotation = Rotation(int(rotation_str))
        ServerCodeGenerator._write_gen_client_code(
            server_dir, client_dir, url, ssid, wi_fi_password, rotation)
        ServerCodeGenerator._gen_client_code(
            client_dir, url, ssid, wi_fi_password, rotation, width, height)


if __name__ == '__main__':
    ServerCodeGenerator.gen_skeleton()
