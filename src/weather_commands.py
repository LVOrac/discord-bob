import os
import requests
import json
from discord import Interaction
from discord.app_commands import Group, command, describe
from dotenv import load_dotenv
from user import load_json, user_initialized

load_dotenv()
TOKEN: str = str(os.getenv("WEATHER_API_KEY"))

day_icons = {
        "clear sky": "🔆",
        "few clouds": "🌤️",
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

    def update_region(self, id: int, lat, lon) -> None:
        path: str = os.path.join(str(id), "weather_region.json")
        with open(path, 'w') as f:
            f.write(f"[{lat}, {lon}]")

    def set_default_region(self, id: int):
        self.update_region(id, 37.3228934, -122.0322895)

    def load_region(self, id: int):
        return load_json(id, "weather_region.json")

    @command(name="region", description="chage region")
    @describe(region="region name")
    async def region(self, interaction: Interaction, region: str) -> None:
        if msg := user_initialized(interaction.user.id):
            await interaction.response.send_message(msg)
            return

        try:
            response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={region}&limit={1}&appid={TOKEN}")
            response.raise_for_status()
            cor = json.loads(response.text)[0]
            self.update_region(interaction.user.id, cor["lat"], cor["lon"])
            await interaction.response.send_message("weahter - success")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                await interaction.response.send_message(f"not found region {region}")


    @command(name="show", description="today's weather")
    async def show(self, interaction: Interaction) -> None:
        if msg := user_initialized(interaction.user.id):
            await interaction.response.send_message(msg)
            return

        region = self.load_region(interaction.user.id)
        if region == None:
            self.set_default_region(interaction.user.id)
            region = self.load_region(interaction.user.id)

        if region == None:
            await interaction.response.send_message("weather - not found region. Please use /weather region to specify")
            return

        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={region[0]}&lon={region[1]}&appid={TOKEN}")

        weather_data = json.loads(response.text)

        temp = weather_data["main"]["temp"] - 273.15
        temp_max = weather_data["main"]["temp_max"] - 273.15
        temp_min = weather_data["main"]["temp_min"] - 273.15

        description = weather_data["weather"][0]["description"]
        day_icon = day_icons[description]

        await interaction.response.send_message(f"My Location\n{weather_data["name"]}\n{temp:.2f}℃  {day_icon} - {description}\n{temp_min:.2f}℃ - {temp_max:.2f}℃")
