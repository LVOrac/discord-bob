import os
import requests
import json
from discord import Interaction
from typing import Optional
from discord.app_commands import Choice, Group, command, describe, choices
from dotenv import load_dotenv
from user import load_json, user_initialized, update_today_is_today

load_dotenv()
API_2_5: str = str(os.getenv("WEATHER_API_2_5"))

day_icons = {
        "clear sky": "🔆",
        "few clouds": "🌤️",
        "overcast clouds": "🌥️",
        "scattered clouds": "☁",
        "broken clouds": "🌥️",
        "slower rain": "🌦️",
        "light rain": "🌦️",
        "moderate rain": "🌦️",
        "rain": "🌧️",
        "thunderstorm": "⛈",
        "snow": "❄️",
        "mist": "🌫️",
        "haze": "🌫️",
}

class WeatherCommands(Group):
    def __init__(self):
        super().__init__(name="weather", description="weather commands")

    def update_region(self, interaction: Interaction, region: str, lat, lon) -> None:
        path: str = os.path.join(str(interaction.user.id), "weather_region.json")
        with open(path, 'w') as f:
            f.write(f"[\"{region}\",{lat},{lon}]")

    def set_default_region(self, interaction: Interaction) -> None:
        self.update_region(interaction, "Cupertino", 37.3228934, -122.0322895)

    def load_region(self, interaction: Interaction):
        return load_json(interaction, "weather_region.json")

    def update_weather_today(self, interaction: Interaction, region) -> None:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={region[1]}&lon={region[2]}&appid={API_2_5}&units=metric")

        weather_data = json.loads(response.text)

        temp = weather_data["main"]["temp"]
        temp_max = weather_data["main"]["temp_max"]
        temp_min = weather_data["main"]["temp_min"]

        description = weather_data["weather"][0]["description"]
        day_icon = day_icons[description]

        path: str = os.path.join(str(interaction.user.id), "weather_today.json")
        with open(path, 'w') as f:
            f.write(f"{{\"name\":\"{weather_data['name']}\",\"temp\":{temp},\"temp_max\":{temp_max},\"temp_min\":{temp_min},\"description\":\"{description}\",\"icon\":\"{day_icon}\"}}")

    @command(name="help", description="show weather's functions")
    async def help(self, interaction: Interaction) -> None:
        help = """### Usage:
        /weather <Commands> [settings ...]
### Commands:
    - region <name> - Change weather's region
      - <ame> - regioin name
      - e.g. cuperino, CUPERTINO, SAN jose, ...; default is Cupertino
    - today [temp standard] - Display today's weather
      - <temp standard> - Celsius, Fahrenheit; default is Celsius
    - forecast [temp standard] - Display forecast
      - <temp standard> - Celsius, Fahrenheit; default is Celsius
"""
        await interaction.response.send_message(help)

    @command(name="region", description="change region")
    @describe(name="region name - cannot be a number")
    async def region(self, interaction: Interaction, name: str) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        if name.isdigit():
            await interaction.response.send_message(f"weather - region name cannot be a number '{name}'")
            return

        reg = self.load_region(interaction)
        if reg and reg[0].lower() == name.lower():
            await interaction.response.send_message(f"weahter - {name} has been seted")
            return

        try:
            response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={name}&limit={2}&appid={API_2_5}")
            response.raise_for_status()
            cor = json.loads(response.text)[0]
            self.update_region(interaction, name, cor["lat"], cor["lon"])
            reg = self.load_region(interaction)
            self.update_weather_today(interaction, reg)
            await interaction.response.send_message(f"weahter - region changed to {name}")
        except requests.exceptions.HTTPError:
            await interaction.response.send_message(f"not found region {name}")

    temp_standard = [
            Choice(name="Celsius", value="celsius"),
            Choice(name="Fahrenheit", value="fahrenheit")
        ]

    temp_icons = {
            temp_standard[0].name: "℃",
            temp_standard[1].name: "℉"
        }

    @command(name="today", description="today's weather")
    @describe(temp_standard="Temp Standard")
    @choices(temp_standard=temp_standard)
    async def today(self, interaction: Interaction, temp_standard: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        region = self.load_region(interaction)
        if region == None:
            self.set_default_region(interaction)
            region = self.load_region(interaction)

        if region == None:
            await interaction.response.send_message("weather - not found region. Please use /weather region to specify")
            return

        path: str = os.path.join(str(interaction.user.id), "weather_today.json")
        if not os.path.exists(path) or update_today_is_today():
            try:
                self.update_weather_today(interaction, region)
            except requests.exceptions.HTTPError:
                await interaction.response.send_message(f"not found region {region}")

        today = load_json(interaction, "weather_today.json")
        if today == None:
            await interaction.response.send_message("weather - not found wather_today.json")
            return

        if temp_standard == None:
            temp_standard = self.temp_standard[0]

        if temp_standard and temp_standard.name == self.temp_standard[1].name:
            today["temp"] = today["temp"] * 5.0 / 9 + 32
            today["temp_max"] = today["temp_max"] * 5.0 / 9 + 32
            today["temp_min"] = today["temp_min"] * 5.0 / 9 + 32
        icon = self.temp_icons[temp_standard.name]
        await interaction.response.send_message(f"My Location\n{today['name']}\n{today['temp']:.2f}{icon}  {today['icon']} - {today['description']}\n{today['temp_min']:.2f}{icon} - {today['temp_max']:.2f}{icon}")

    @command(name="forecast", description="forecast")
    @describe(temp_standard="Temp Standard")
    @choices(temp_standard=temp_standard)
    async def forecast(self, interaction: Interaction, temp_standard: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        region = self.load_region(interaction)
        if region == None:
            self.set_default_region(interaction)
            region = self.load_region(interaction)

        if region == None:
            await interaction.response.send_message("weather - not found region. Please use /weather region to specify")
            return

        if temp_standard == None:
            temp_standard = self.temp_standard[0]

        try:
            response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={region[1]}&lon={region[2]}&appid={API_2_5}&units=metric&cnt=60")
            forecast = json.loads(response.text)["list"]
            result = ""
            for weather_data in forecast:
                description = weather_data["weather"][0]["description"]
                day_icon = day_icons[description]
                time = weather_data["dt_txt"]

                temp = weather_data["main"]["temp"]
                if temp_standard and temp_standard.name == self.temp_standard[1].name:
                    temp = temp * 5.0 / 9 + 32
                result += f"[{time}]  {day_icon} {temp:.2f}{self.temp_icons[temp_standard.name]}  - {description}\n"
            await interaction.response.send_message(result)
        except requests.exceptions.HTTPError:
            await interaction.response.send_message(f"not found region {region}")

