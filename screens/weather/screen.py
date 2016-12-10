import os
import sys
import time
from datetime import datetime

import forecastio

from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class WeatherScreen(Screen):

    def __init__(self, **kwargs):
        super(WeatherScreen, self).__init__(**kwargs)
        self.key = kwargs["params"]["key"]
        self.locations = kwargs["params"]["locations"]
        self.flt = self.ids.weather_float
        self.flt.remove_widget(self.ids.weather_base_box)
        self.scrmgr = self.ids.weather_scrmgr
        self.running = False
        self.scrid = 0
        self.myscreens = [x["Name"] for x in self.locations]

    def on_enter(self):
        # If the screen hasn't been displayed before then let's load up
        # the locations
        if not self.running:
            for location in self.locations:

                # Create the necessary URLs for the data
                lat = location["lat"]
                lng = location["long"]
                current_time = datetime.now()

                call = forecastio.load_forecast(self.key, lat, lng)
                forecast  = call.daily();

                ws = WeatherSummary(forecast=forecast, name=self.name)

                # and add to our screen manager.
                self.scrmgr.add_widget(ws)

            # set the flag so we don't do this again.
            self.running = True

        else:
            # Fixes bug where nested screens don't have "on_enter" or
            # "on_leave" methods called.
            for c in self.scrmgr.children:
                if c.name == self.scrmgr.current:
                    c.on_enter()

    def on_leave(self):
        # Fixes bug where nested screens don't have "on_enter" or
        # "on_leave" methods called.
        for c in self.scrmgr.children:
            if c.name == self.scrmgr.current:
                c.on_leave()

    def next_screen(self, rev=True):
        a = self.myscreens
        n = -1 if rev else 1
        self.scrid = (self.scrid + n) % len(a)
        self.scrmgr.transition.direction = "up" if rev else "down"
        self.scrmgr.current = a[self.scrid]

class WeatherSummary(Screen):
    """Screen to show weather summary for a selected location."""
    location = StringProperty("")

    def __init__(self, **kwargs):
        super(WeatherSummary, self).__init__(**kwargs)
        self.name = kwargs["name"]
        self.forecast = kwargs["forecast"]
        self.nextupdate = 0
        self.timer = None
        self.bx_forecast = self.ids.bx_forecast

    def on_enter(self):
        # Check if the next update is due
        if (time.time() > self.nextupdate):
            dt = 0.5
        else:
            dt = self.nextupdate - time.time()

        self.timer = Clock.schedule_once(self.getData, dt)

    def on_leave(self):
        Clock.unschedule(self.timer)

    def getData(self, *args):
        # Clear the screen of existing widgets
        self.bx_forecast.clear_widgets()
        top5 = self.forecast.data[1:6]
        for day in top5:
            days = True
            frc = WeatherForecastDay(summary=day)
            self.bx_forecast.add_widget(frc)

        if days:
            dt = 60 * 60
        else:
            dt = 5 * 60
        self.nextupdate = time.time() + dt
        self.timer = Clock.schedule_once(self.getData, dt)

class WeatherForecastDay(BoxLayout):
    """Custom widget to show daily forecast summary."""
    weather = StringProperty("")
    icon_url = StringProperty("")
    day = StringProperty("")

    def __init__(self, **kwargs):
        super(WeatherForecastDay, self).__init__(**kwargs)
        self.buildText(kwargs["summary"])

    def buildText(self, summary):
        fc = {}
        self.day = summary.time.strftime("%A")
        fc["su"] = summary.summary
        fc["hg"] = summary.temperatureMax
        fc["lw"] = summary.temperatureMin
        fc["po"] = summary.precipProbability
        self.icon_url = summary.icon
        self.weather = ("{su}\nHigh: {hg}{dg}\n"
                        "Low: {lw}\nRain: {po}%").format(dg="C", **fc)
