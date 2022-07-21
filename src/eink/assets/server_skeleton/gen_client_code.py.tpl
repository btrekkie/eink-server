# Script for generating the source code for the e-ink device. Whenever you
# change the client configuration or upgrade the eink-server library, you
# should rerun this script and upload the new software to your e-ink device.
# You can run this using the command "python3 gen_client_code.py".
$import_json$import_os$import_separator
from eink.generate import ClientCodeGenerator
from eink.generate import ClientConfig
${import_rotation}from eink.generate import StatusImages
from eink.generate import WebTransport

from my_server import MyServer

$read_secrets
def client_config():
    """Return the ``ClientConfig`` for this project."""
    status_images = StatusImages.create_default(
        MyServer.WIDTH, MyServer.HEIGHT)
    transport = WebTransport($url)
    config = ClientConfig(transport, status_images)
    config.add_wi_fi_network($ssid, $wi_fi_password)$set_rotation$set_palette
    return config


def gen_client_code():
    """Output the source code files for the client."""
    config = client_config()
$set_client_dir
    ClientCodeGenerator.gen(config, dir_)


if __name__ == '__main__':
    gen_client_code()
