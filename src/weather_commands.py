import os
import requests
import json
from discord import Interaction
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
        "rain": "🌧️",
        "thunderstorm": "⛈",
        "snow": "❄️",
        "mist": "🌫️",
}

class WeatherCommands(Group):
    def __init__(self):
        super().__init__(name="weather", description="weather commands")

    def update_region(self, interaction: Interaction, region: str, lat, lon) -> None:
        path: str = os.path.join(str(interaction.user.id), "weather_region.json")
        with open(path, 'w') as f:
            f.write(f"[\"{region}\",{lat},{lon}]")

    def set_default_region(self, interaction: Interaction):
        self.update_region(interaction, "Cupertino", 37.3228934, -122.0322895)

    def load_region(self, interaction: Interaction):
        return load_json(interaction, "weather_region.json")

    def update_weather_today(self, interaction: Interaction, region):
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={region[1]}&lon={region[2]}&appid={API_2_5}&units=metric")

        weather_data = json.loads(response.text)

        temp = weather_data["main"]["temp"]
        temp_max = weather_data["main"]["temp_max"]
        temp_min = weather_data["main"]["temp_min"]

        description = weather_data["weather"][0]["description"]
        day_icon = day_icons[description]

        path: str = os.path.join(str(interaction.user.id), "weather_today.json")
        with open(path, 'w') as f:
            f.write(f"{{\"name\":\"{weather_data["name"]}\",\"temp\":{temp},\"temp_max\":{temp_max},\"temp_min\":{temp_min},\"description\":\"{description}\",\"icon\":\"{day_icon}\"}}")

    @command(name="region", description="change region")
    @describe(region="region name")
    async def region(self, interaction: Interaction, region: str) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        reg = self.load_region(interaction)
        if reg and reg[0].lower() == region.lower():
            await interaction.response.send_message(f"weahter - {region} has been seted")
            return

        try:
            response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={region}&limit={1}&appid={API_2_5}")
            response.raise_for_status()
            cor = json.loads(response.text)[0]
            self.update_region(interaction, region, cor["lat"], cor["lon"])
            reg = self.load_region(interaction)
            self.update_weather_today(interaction, reg)
            await interaction.response.send_message(f"weahter - {region} {cor["lat"]} {cor["lon"]}")
        except requests.exceptions.HTTPError:
            await interaction.response.send_message(f"not found region {region}")

    @command(name="today", description="today's weather")
    async def today(self, interaction: Interaction) -> None:
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
        if not os.path.exists(path) or update_today_is_today(interaction):
            try:
                self.update_weather_today(interaction, region)
            except requests.exceptions.HTTPError:
                await interaction.response.send_message(f"not found region {region}")

        today = load_json(interaction, "weather_today.json")
        if today == None:
            await interaction.response.send_message("weather - not found wather_today.json")
            return
        await interaction.response.send_message(f"My Location\n{today["name"]}\n{today["temp"]:.2f}℃  {today["icon"]} - {today["description"]}\n{today["temp_min"]:.2f}℃ - {today["temp_max"]:.2f}℃")

    @command(name="forecast", description="forecast")
    async def forecast(self, interaction: Interaction) -> None:
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

        try:
            response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={region[1]}&lon={region[2]}&appid={API_2_5}&units=metric")
            forecast = json.loads(response.text)["list"]
            result = ""
            for weather_data in forecast:
                temp = weather_data["main"]["temp"]
                description = weather_data["weather"][0]["description"]
                day_icon = day_icons[description]
                time = weather_data["dt_txt"]

                result += f"[{time}]  {day_icon} {temp:.2f}℃  - {description}\n"
            await interaction.response.send_message(result)
        except requests.exceptions.HTTPError:
            await interaction.response.send_message(f"not found region {region}")

