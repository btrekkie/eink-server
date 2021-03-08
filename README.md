# Description
`eink-server` is a framework for displaying content on an Inkplate e-ink
display. The Inkplate device connects to a server over Wi-Fi. Using Python 3
code, the server computes the content to display and then sends it to the e-ink
device in the form of an image. The display periodically queries the server for
updated content.

This approach has pros and cons, compared to doing all of the work on the
Inkplate device:

**Pros:**

* The content is computed on a more powerful device, which has much more memory,
  a faster CPU, non-volatile memory, etc.
* Code changes can be made remotely, without connecting the Inkplate to a PC and
  uploading new software.
* Code changes can be tested locally, without waiting a couple of minutes for
  the new software to be compiled and uploaded to the e-ink device. This makes
  the development process faster.
* Programming the content is arguably easier, because it is in Python, which is
  a higher-level language than C++.

**Cons:**

* Some setup is required.
* Displaying a clock is problematic.
* We cannot respond to touchpad or other Inkplate inputs.
* Some flexibility is sacrificed.

A server is implemented by subclassing the `Server` class. The base class
declares a `render()` method, which is overridden to return an image indicating
the content to display. Images are represented as Pillow library `Image`
objects. `Servers` also have methods indicating how often the content should be
updated. This informs the Inkplate device how often to query the server.

# Getting started
You can use the skeleton code generator to autogenerate your own Flask server:

* Make sure you have [the Arduino IDE](https://www.arduino.cc/en/software),
  [Python 3](https://www.python.org/downloads/), and pip installed. You can use
  [venv](https://docs.python.org/3/tutorial/venv.html) if you want, in which
  case you will have to make adjustments to the below instructions.

  ```bash
  python3 --version
  pip3 --version
  ```

* Set up the Arduino IDE to work with the Inkplate device:
  <https://e-radionica.com/en/blog/add-inkplate-6-to-arduino-ide/>.
* Obtain a fixed IP address or domain name for your PC. There are three options:
    * (recommended) Assign your computer a static local IP address (such as
      192.168.1.70), using your Wi-Fi modem/router's settings. If you do this,
      then your e-ink device will need to connect to the same Wi-Fi network as
      your PC.
    * Obtain a domain name for your computer, and forward web requests to your
      computer using port forwarding, through your Wi-Fi modem/router's
      settings. You can get a free domain name using a service such as
      [No-IP](https://www.noip.com/).
    * Obtain a static global IP address for your computer, and forward web
      requests to your computer using port forwarding, through your Wi-Fi
      modem/router's settings. Often, this is not possible, because it depends
      on your Internet service provider.

  The instructions for configuring your modem/router will depend on what model
  you have. If you look at your modem/router device, it should tell you a URL
  you can visit to configure it, such as http://192.168.1.255. Open this URL in
  your web browser and navigate around until you see the appropriate setting.

  Note: If you make your server available through a public domain or IP address
  (the second and third options), then anyone will be able to access it. This is
  because the `eink-server` library does not do any authentication.
* Set up the `eink-server` library:

  ```bash
  git clone https://github.com/btrekkie/eink-server.git
  cd eink-server
  pip3 install .
  ```

* Run the skeleton code generator, and follow the on-screen instructions. When
  prompted for the server URL, use the IP address or domain you assigned to your
  PC in a previous step.

  ```bash
  einkserver skeleton
  ```

* Install the server's dependencies:

  ```bash
  cd ~/eink_server
  pip3 install -r requirements.txt
  ```

* Run the Flask server. (If you entered in a port number other than 5000 when
  asked for the URL, you will need to specify the port number using the `-p`
  argument.)

  ```bash
  cd ~/eink_server
  flask run --host=0.0.0.0
  ```

* In another console, using the `connect` command, make sure you can connect to
  the server using the URL you supplied to the skeleton code generator:

  ```bash
  einkserver connect [URL of e-ink server]
  ```

  If the connection is successful, you should see a window with the default
  content. If the connection fails, the console will print an error. In that
  case, check the configuration of your modem/router, and make sure your Flask
  server is running.
* Run the Arduino IDE. Go to File -> Open.... Navigate to the client code
  directory you supplied to the skeleton code generator. Open the INO file in
  this directory.
* Connect your Inkplate device to your computer using a USB cable. Switch your
  e-ink display on.
* In the Arduino IDE, click the upload button (or go to Sketch -> Upload). If
  successful, the e-ink display should show the word "Connecting" briefly,
  followed by the default content.

Once you've set up your server, take a look at the Python code it generated. Now
you should modify it to suit your needs. (You do not need to read or modify the
client code.)

# Examples
* [`wikipedia`](samples/wikipedia): Displays the Wikipedia homepage. This can
  easily be modified to show another webpage. It requires the `google-chrome`
  command to be present in the path.
* [`weather`](samples/weather): Displays a five-day weather forecast, using the
  OpenWeatherMap API.
* [`slideshow`](samples/slideshow): Displays a slideshow of all of the images in
  a given directory.

# Documentation
See <https://btrekkie.github.io/eink-server/index.html> for API documentation.

# Possible future enhancements
These are ways that `eink-server` could be improved in the future:

* More transport mechanisms. For example, we could add support for Bluetooth and
  serial connections.
* Security. Perhaps it would be sufficient to encrypt the request and response
  payloads using AES with a randomly generated key. (My initial thought was to
  use HTTPS and basic authentication. But for some reason, if I try to stream an
  HTTPS response using `WiFiClientSecure.read`, and the response is larger than
  around 4 KB, then the attempt fails with a return value of `-1`.)

# Credits
* Icons made by [fjstudio](https://www.flaticon.com/authors/fjstudio) and
  [Smartline](https://www.flaticon.com/authors/Smartline) from
  [www.flaticon.com](https://www.flaticon.com/)
* The [Gentium Plus font](https://software.sil.org/gentium/) is licensed under
  the SIL Open Font License.
