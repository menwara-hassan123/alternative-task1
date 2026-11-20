import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHERAPI_KEY")
BASE_URL = "https://api.weatherapi.com/v1/current.json"


class WeatherReport:
    def __init__(self, city, country, local_time, temp, feels_like,
                 humidity, wind_kph, pressure, uv, description):
        self.city = city
        self.country = country
        self.local_time = local_time
        self.temp = temp
        self.feels_like = feels_like
        self.humidity = humidity
        self.wind_kph = wind_kph
        self.pressure = pressure
        self.uv = uv
        self.description = description

    @classmethod
    def from_json(cls, data):
        loc = data["location"]
        cur = data["current"]
        return cls(
            city=loc["name"],
            country=loc["country"],
            local_time=loc["localtime"],
            temp=cur["temp_c"],
            feels_like=cur["feelslike_c"],
            humidity=cur["humidity"],
            wind_kph=cur["wind_kph"],
            pressure=cur["pressure_mb"],
            uv=cur["uv"],
            description=cur["condition"]["text"],
        )

    def summary(self):
        line = "=" * 42
        return (
            f"{line}\n"
            f"  Weather Report: {self.city}, {self.country}\n"
            f"{line}\n"
            f"  Local Time  : {self.local_time}\n"
            f"  Condition   : {self.description}\n"
            f"  Temperature : {self.temp:.1f} °C (feels like {self.feels_like:.1f} °C)\n"
            f"  Humidity    : {self.humidity}%\n"
            f"  Wind Speed  : {self.wind_kph} km/h\n"
            f"  Pressure    : {self.pressure} mb\n"
            f"  UV Index    : {self.uv}\n"
            f"{line}"
        )


def fetch_weather(city):
    params = {"key": API_KEY, "q": city, "aqi": "no"}
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()  # يرمي error لو الطلب فشل
    return response.json()       # parsing الـ JSON


def main():
    if not API_KEY:
        sys.exit("Error: WEATHERAPI_KEY not found. Check your .env file.")

    city = input("Enter city name: ").strip() or "Cairo"

    try:
        data = fetch_weather(city)
        report = WeatherReport.from_json(data)
        print(report.summary())
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 400:
            print("City not found. Check the city name.")
        elif code in (401, 403):
            print("Invalid or disabled API key. Check your .env file.")
        else:
            print(f"API error: {code}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {type(e).__name__}")


if __name__ == "__main__":
    main()
