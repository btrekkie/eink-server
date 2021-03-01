from flask import Flask
from flask import request

from my_server import MyServer


app = Flask(__name__)


@app.route($path, methods=['POST'])
def eink_server():
    """Flask endpoint for the e-ink server."""
    return MyServer.instance().exec(request.data)
