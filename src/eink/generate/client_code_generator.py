import os
import shutil

from ..image import EinkGraphics
from ..image.image_data import ImageData
from ..project.project import Project
from ..server import Server
from ..server.server_io import ServerIO


class ClientCodeGenerator:
    """Generates client-side source code for the Inkplate device."""

    # The cached return value of _str_literal_list()
    _str_literal_list_cache = None

    @staticmethod
    def gen(config, dir_):
        """Generate client-side source code files for the Inkplate device.

        Arguments:
            config (ClientConfig): The configuration for the program.
            dir_ (str): The directory in which to store the resulting
                source code files. This directory must already exist.
        """
        ClientCodeGenerator._validate(config, dir_)
        ClientCodeGenerator._copy_static_files(dir_)
        ClientCodeGenerator._gen_dynamic_files(config, dir_)

    @staticmethod
    def _validate(config, dir_):
        """Raise if we detect an error in the specified arguments to ``gen``.
        """
        if not os.path.isdir(dir_):
            raise OSError('No such directory {:s}'.format(dir_))
        if not config._transports:
            raise ValueError('No Transports provided')
        if not config._wi_fi_networks:
            raise ValueError('No Wi-Fi networks provided')

        status_images = config._status_images
        images = status_images._images
        if status_images._initial_image_name not in images:
            raise ValueError(
                'StatusImages is missing the initial image {:s}'.format(
                    status_images._initial_image_name))
        if status_images._low_battery_image_name not in images:
            raise ValueError(
                'StatusImages is missing the low battery image {:s}'.format(
                    status_images._low_battery_image_name))

        for name, image in images.items():
            if (image.width != status_images._width or
                    image.height != status_images._height):
                raise ValueError(
                    'The size of the image {:s} does not match the size '
                    'passed to the StatusImages constructor'.format(name))
            if EinkGraphics._has_alpha(image):
                raise ValueError(
                    'Alpha channels are not supported. The image {:s} has an '
                    'alpha channel.'.format(image))

    @staticmethod
    def _copy_static_files(dir_):
        """Copy the static files to the specified directory.

        Copy the source code files for the client that are not generated
        programatically to the specified directory.
        """
        client_dir = Project.client_code_dir()
        for subfile in os.listdir(client_dir):
            if subfile == 'client.ino':
                output_subfile = '{:s}.ino'.format(
                    os.path.basename(os.path.abspath(dir_)))
                shutil.copy(
                    os.path.join(client_dir, subfile),
                    os.path.join(dir_, output_subfile))
            elif subfile.endswith(('.cpp', '.h', '.ino')):
                shutil.copy(
                    os.path.join(client_dir, subfile),
                    os.path.join(dir_, subfile))

    @staticmethod
    def _write_bytes_literal(file, bytes_, multiline):
        """Write C code for a literal byte array to the specified file.

        Arguments:
            file (file): The file object.
            bytes_ (bytes): The contents of the byte array.
            multiline (bool): Whether to format the results by writing
                line breaks as appropriate.
        """
        file.write('{')
        if multiline:
            file.write('\n    ')
            column = 4
        else:
            column = 1

        first = True
        for byte in bytes_:
            if not first:
                if not multiline or column < 73:
                    file.write(', ')
                    column += 2
                else:
                    file.write(',\n    ')
                    column = 4
            first = False

            file.write('0x{:02x}'.format(byte))
            column += 4

        if multiline:
            file.write('\n')
        file.write('}')

    @staticmethod
    def _str_literal_list():
        r"""Return a list of literal C string fragments for each character.

        The return value has 256 elements. The (i + 1)th element of the
        return value is for ``chr(i)``. For example, the element for the
        newline character may be ``'\\n'``, while the element for the
        dash character may be ``'-'``. The only escape sequences we use
        are non-numeric escape sequences and three-digit octal escape
        sequences such as ``'\123'``.
        """
        if ClientCodeGenerator._str_literal_list_cache is None:
            literal_list = []
            for i in range(0x20):
                literal_list.append('\\{:03o}'.format(i))
            for i in range(0x20, 0x7f):
                literal_list.append(chr(i))
            for i in range(0x7f, 0x100):
                literal_list.append('\\{:03o}'.format(i))

            escapes = [
                ('"', '\\"'), ('\\', '\\\\'), ('\a', '\\a'), ('\a', '\\a'),
                ('\b', '\\b'), ('\f', '\\f'), ('\n', '\\n'), ('\r', '\\r'),
                ('\t', '\\t'), ('\v', '\\v'),
            ]
            for char, escape in escapes:
                literal_list[ord(char)] = escape
            ClientCodeGenerator._str_literal_list_cache = literal_list
        return ClientCodeGenerator._str_literal_list_cache

    @staticmethod
    def _write_str_literal(file, bytes_):
        """Write C code for a literal string to the specified file.

        The string is null-terminated.

        Arguments:
            file (file): The file object.
            bytes_ (bytes): The C string.
        """
        literal_list = ClientCodeGenerator._str_literal_list()
        file.write('"')
        prev_literal = None
        for byte in bytes_:
            literal = literal_list[byte]
            if literal == '?' and prev_literal == '?':
                # Avoid the possibility of trigraphs
                literal = '\\?'
            file.write(literal)
            prev_literal = literal
        file.write('"')

    @staticmethod
    def _write_str_array(file, strs):
        """Write C code for a literal string array to the specified file.

        The strings are null-terminated.

        Arguments:
            file (file): The file object.
            strs (list<bytes>): The C strings. An element of ``None`` is
                permitted. We encode such elements as ``NULL``.
        """
        if not strs:
            file.write('{}')
            return

        file.write('{\n')
        first = True
        for str_ in strs:
            if not first:
                file.write(',\n')
            first = False
            file.write('    ')
            if str_ is not None:
                ClientCodeGenerator._write_str_literal(file, str_)
            else:
                file.write('NULL')
        file.write('\n}')

    @staticmethod
    def _write_int_array(file, values):
        """Write C code for a literal ``int`` array to the specified file.

        Arguments:
            file (file): The file object.
            values (list<int>): The integers.
        """
        file.write('{')
        first = True
        for value in values:
            if not first:
                file.write(', ')
            first = False
            file.write('{:d}'.format(value))
        file.write('}')

    @staticmethod
    def _write_generated_message(file):
        """Write a C comment indicating a file was generated programatically.

        Arguments:
            file (file): The file object to write the comment to.
        """
        file.write(
            '// Auto-generated by the Python class '
            'eink.generate.ClientCodeGenerator\n\n')

    @staticmethod
    def _write_secrets_cpp(file, config):
        """Write the contents of the secrets.cpp file.

        This contains all of the information that we would like to keep
        private. We should refrain from committing the file to a
        repository and from opening the file in a text editor.

        Arguments:
            file (file): The file object to write to.
            config (ClientConfig): The configuration for the program.
        """
        passwords = []
        for _, password in config._wi_fi_networks:
            if password is not None:
                passwords.append(password.encode())
            else:
                passwords.append(None)

        ClientCodeGenerator._write_generated_message(file)
        if None in passwords:
            file.write('#include <stddef.h>\n\n')
        file.write('#include "secrets_constants.h"\n\n\n')
        file.write('const char* WI_FI_PASSWORDS[] = ')
        ClientCodeGenerator._write_str_array(file, passwords)
        file.write(';\n')

    @staticmethod
    def _write_status_image_data_h(file, status_images):
        """Write the contents of the status_image_data.h file.

        This declares the constants that are provided in
        status_image_data.cpp.

        Arguments:
            file (file): The file object to write to.
            status_images (StatusImages): The status images for the
                program.
        """
        ClientCodeGenerator._write_generated_message(file)
        file.write(
            '#ifndef __STATUS_IMAGE_DATA_H__\n'
            '#define __STATUS_IMAGE_DATA_H__\n\n'
            '// The contents of each of the status image files, in the same '
            'order as\n'
            '// STATUS_IMAGE_DATA\n')
        for index in range(len(status_images._images)):
            file.write(
                'extern const char STATUS_IMAGE_DATA{:d}[];\n'.format(index))

        file.write(
            '\n// The number of bytes in each of the status image files, in '
            'the same order as\n'
            '// STATUS_IMAGE_DATA\n')
        for index in range(len(status_images._images)):
            file.write(
                'extern const int STATUS_IMAGE_DATA_LENGTH{:d};\n'.format(
                    index))
        file.write('\n#endif\n')

    @staticmethod
    def _render_status_image(image, quality, palette):
        """Render the specified status image.

        Arguments:
            image (image): The image.
            quality (int): The quality, as in the ``quality`` argument
                to ``StatusImages.set_image``.
            palette (Palette): The color palette to use.

        Returns:
            bytes: The contents of the image file for the image.
        """
        image = EinkGraphics.round(image, palette)
        png = ImageData.render_png(image, palette, True)
        if quality < 100:
            jpeg = ImageData.render_jpeg(image, quality)
            if len(jpeg) < len(png):
                return jpeg
        return png

    @staticmethod
    def _write_status_image_data_cpp(file, status_images, palette):
        """Write the contents of the status_image_data.cpp file.

        This contains the contents and sizes of the image files for the
        status images. We keep these in a separate file in order to
        improve the readability of generated.cpp.

        Arguments:
            file (file): The file object to write to.
            status_images (StatusImages): The status images for the
                program.
            palette (Palette): The color palette to use.
        """
        ClientCodeGenerator._write_generated_message(file)
        file.write('#include "status_image_data.h"\n\n')

        images = []
        for name, image in status_images._images.items():
            quality = status_images._quality[name]
            images.append((ServerIO.image_id(name), image, quality))

        sorted_images = sorted(images, key=lambda image: image[0])
        for index, (_, image, quality) in enumerate(sorted_images):
            image_data = ClientCodeGenerator._render_status_image(
                image, quality, palette)
            file.write('\n')
            file.write(
                'const int STATUS_IMAGE_DATA_LENGTH{:d} = {:d};\n'.format(
                    index, len(image_data)))
            file.write('const char STATUS_IMAGE_DATA{:d}[] = '.format(index))
            ClientCodeGenerator._write_bytes_literal(file, image_data, True)
            file.write(';\n')

    @staticmethod
    def _write_generated_h(file, config):
        """Write the contents of the generated.h file.

        This ``#includes`` the header files that declare all of the
        generated constants, and it defines all of the constants that
        are defined using ``#define``.

        Arguments:
            file (file): The file object to write to.
            config (ClientConfig): The configuration for the program.
        """
        ClientCodeGenerator._write_generated_message(file)
        file.write(
            '#ifndef __GENERATED_H__\n'
            '#define __GENERATED_H__\n\n'
            '#include "generated_constants.h"\n'
            '#include "secrets_constants.h"\n\n\n')
        file.write(
            '// The maximum number of elements in ClientState.requestTimesDs\n'
            '#define MAX_REQUEST_TIMES {:d}\n\n'.format(
                Server._MAX_REQUEST_TIMES))
        file.write(
            '// The number of bytes in an image ID, as in the return value of '
            'the Python\n'
            '// method ServerIO.image_id\n'
            '#define STATUS_IMAGE_ID_LENGTH {:d}\n\n'.format(
                ServerIO.STATUS_IMAGE_ID_LENGTH))
        file.write(
            '// The number of elements in the return value of '
            'requestTransports()\n'
            '#define TRANSPORT_COUNT {:d}\n\n'.format(len(config._transports)))
        file.write(
            '// The color palette to use\n'
            '#define PALETTE_{:s}\n\n'.format(config._palette._name))
        file.write('#endif\n')

    @staticmethod
    def _write_status_images(file, status_images):
        """Write the portion of the generated.cpp file for status images.

        Arguments:
            file (file): The file object to write to.
            status_images (StatusImages): The status images for the
                program.
        """
        image_id_to_name = {}
        for name in status_images._images.keys():
            image_id_to_name[ServerIO.image_id(name)] = name
        sorted_image_ids = sorted(list(image_id_to_name.keys()))
        image_count = len(sorted_image_ids)
        file.write(
            'const int STATUS_IMAGE_COUNT = {:d};\n'.format(image_count))

        file.write('const int STATUS_IMAGE_DATA_LENGTHS[] = {\n')
        for index in range(image_count):
            if index > 0:
                file.write(',\n')
            file.write('    STATUS_IMAGE_DATA_LENGTH{:d}'.format(index))
        file.write('\n};\n')

        file.write('const char* STATUS_IMAGE_DATA[] = {\n')
        for index in range(image_count):
            if index > 0:
                file.write(',\n')
            file.write('    STATUS_IMAGE_DATA{:d}'.format(index))
        file.write('\n};\n\n')

        for index, image_id in enumerate(sorted_image_ids):
            file.write('const char STATUS_IMAGE_ID{:d}[] = '.format(index))
            ClientCodeGenerator._write_bytes_literal(file, image_id, True)
            file.write(';\n')
        file.write('const char* STATUS_IMAGE_IDS[] = {\n')
        for index in range(image_count):
            if index > 0:
                file.write(',\n')
            file.write('    STATUS_IMAGE_ID{:d}'.format(index))
        file.write('\n};\n')

        # Compute STATUS_IMAGES_BY_TYPE
        image_name_to_index = {}
        for index, image_id in enumerate(sorted_image_ids):
            name = image_id_to_name[image_id]
            image_name_to_index[name] = index
        status_images_by_type = [
            status_images._initial_image_name,
            status_images._low_battery_image_name]
        status_image_indices = []
        for name in status_images_by_type:
            status_image_indices.append(image_name_to_index[name])

        file.write('const int STATUS_IMAGES_BY_TYPE[] = ')
        ClientCodeGenerator._write_int_array(file, status_image_indices)
        file.write(';\n')

    @staticmethod
    def _write_transports(file, transports):
        """Write the portion of the generated.cpp file for transports.

        Arguments:
            file (file): The file object to write to.
            transports (list<Transport>): The transports for the
                program, in the order the client should try to connect
                to them.
        """
        transport_urls = list([
            transport._url.encode() for transport in transports])
        file.write('const char* TRANSPORT_URLS[] = ')
        ClientCodeGenerator._write_str_array(file, transport_urls)
        file.write(';\n')

    @staticmethod
    def _write_generated_cpp(file, config):
        """Write the contents of the generated.cpp file.

        This provides all of the generated constants that don't have
        some special reason to be provided elsewhere.

        Arguments:
            file (file): The file object to write to.
            config (ClientConfig): The configuration for the program.
        """
        ClientCodeGenerator._write_generated_message(file)
        file.write(
            '#include "generated.h"\n'
            '#include "status_image_data.h"\n\n\n')
        file.write(
            'const int ROTATION = {:d};\n'.format(config._rotation.value))

        file.write('const char HEADER[] = ')
        ClientCodeGenerator._write_bytes_literal(file, ServerIO.HEADER, True)
        file.write(';\n')
        file.write(
            'const int HEADER_LENGTH = {:d};\n'.format(len(ServerIO.HEADER)))

        file.write('const char PROTOCOL_VERSION[] = ')
        ClientCodeGenerator._write_str_literal(file, ServerIO.PROTOCOL_VERSION)
        file.write(';\n')
        file.write(
            'const int PROTOCOL_VERSION_LENGTH = {:d};\n\n'.format(
                len(ServerIO.PROTOCOL_VERSION)))

        ClientCodeGenerator._write_status_images(file, config._status_images)
        file.write('\n')
        ClientCodeGenerator._write_transports(file, config._transports)
        file.write('\n')

        file.write(
            'const int WI_FI_NETWORK_COUNT = {:d};\n'.format(
                len(config._wi_fi_networks)))

        ssids = list([
            network[0].encode() for network in config._wi_fi_networks])
        file.write('const char* WI_FI_SSIDS[] = ')
        ClientCodeGenerator._write_str_array(file, ssids)
        file.write(';\n')

        networks_with_indices = []
        for index, (ssid, _) in enumerate(config._wi_fi_networks):
            networks_with_indices.append((ssid.encode(), index))
        sorted_networks = sorted(networks_with_indices)
        network_indices = list([network[1] for network in sorted_networks])
        file.write('const int WI_FI_NETWORK_INDICES[] = ')
        ClientCodeGenerator._write_int_array(file, network_indices)
        file.write(';\n')

    @staticmethod
    def _gen_dynamic_files(config, dir_):
        """Write the contents of all of the programatically generated files.

        Arguments:
            config (ClientConfig): The configuration for the program.
            dir_ (str): The directory in which to store the files.
        """
        # Contains the secret values
        with open(os.path.join(dir_, 'secrets.cpp'), 'w') as file:
            ClientCodeGenerator._write_secrets_cpp(file, config)

        # Declares constants for status_image_data.cpp
        with open(os.path.join(dir_, 'status_image_data.h'), 'w') as file:
            ClientCodeGenerator._write_status_image_data_h(
                file, config._status_images)

        # Contains the image files for the status images
        with open(os.path.join(dir_, 'status_image_data.cpp'), 'w') as file:
            ClientCodeGenerator._write_status_image_data_cpp(
                file, config._status_images, config._palette)

        # #includes the header files that declare the generated constants, and
        # defines all of the constants that use #define
        with open(os.path.join(dir_, 'generated.h'), 'w') as file:
            ClientCodeGenerator._write_generated_h(file, config)

        # Contains the rest of the generated constants
        with open(os.path.join(dir_, 'generated.cpp'), 'w') as file:
            ClientCodeGenerator._write_generated_cpp(file, config)
