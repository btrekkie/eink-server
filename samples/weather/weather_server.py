from datetime import datetime
from datetime import timedelta
import json
import os
import urllib

from eink.image import Palette
from eink.server import Server
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class WeatherServer(Server):
    """Displays a five-day weather forecast, using the OpenWeatherMap API.

    To use the OpenWeatherMap API, you must obtain an API key by signing
    up for an account. If this is for personal use, the free plan should
    offer more than enough API requests per month.
    """

    def __init__(
            self, latitude, longitude, api_key, imperial=False,
            width=800, height=600, palette=Palette.THREE_BIT_GRAYSCALE):
        """Initialize a new ``WeatherServer``.

        Arguments:
            latitude (float): The latitude of the location to show the
                weather for.
            longitude (float): The longitude of the location to show the
                weather for.
            api_key (str): The OpenWeatherMap API key to use.
            imperial (bool): Whether to display the results using
                imperial units, as opposed to metric units.
            width (int): The width of the display, after rotation.
            height (int): The height of the display, after rotation.
            palette (Palette): The palette to use. This must be a
                palette that the e-ink device supports.
        """
        self._latitude = latitude
        self._longitude = longitude
        self._api_key = api_key
        self._imperial = imperial
        self._width = width
        self._height = height
        self._palette = palette

    def update_time(self):
        return timedelta(minutes=30)

    def screensaver_time(self):
        return timedelta(hours=3)

    def palette(self):
        return self._palette

    def render(self):
        # Load the font
        dir_ = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_filename = os.path.join(
            dir_, 'src', 'eink', 'assets', 'server_skeleton',
            'GentiumPlus-R.ttf')
        font = ImageFont.truetype(font_filename, 50)

        # Fetch the weather forecast
        weather = self._fetch_weather()

        image = Image.new('L', (self._width, self._height), 255)
        draw = ImageDraw.Draw(image)
        x = (self._width // 2) - 250
        y = (self._height // 2) - 185

        # Render the weather forecast
        five_day_forecast = weather['daily'][:5]
        for index, day_forecast in enumerate(five_day_forecast):
            if index == 0:
                day_str = 'Today'
            elif index == 1:
                day_str = 'Tomorrow'
            else:
                # Compute the day of the week
                time = (
                    datetime.utcfromtimestamp(0) +
                    timedelta(seconds=day_forecast['dt']))
                day_str = time.strftime('%A')

            high = round(day_forecast['temp']['max'])
            low = round(day_forecast['temp']['min'])
            text = '{:s}: {:d}\u00b0 / {:d}\u00b0'.format(day_str, high, low)
            draw.text((x, y), text, fill=0, font=font)
            y += 70
        return image

    def _fetch_weather(self):
        """Fetch the weather forecast from the OpenWeatherMap One Call API.

        Return the JSON value for the response.
        """
        if self._imperial:
            units = 'imperial'
        else:
            units = 'metric'
        url = (
            'https://api.openweathermap.org/data/2.5/onecall?'
            'exclude=current,minutely,hourly,alerts&'
            'units={:s}&appid={:s}&lat={:s}&lon={:s}').format(
            units, self._api_key, str(self._latitude), str(self._longitude))

        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
