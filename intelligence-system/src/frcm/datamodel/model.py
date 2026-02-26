from __future__ import annotations

import datetime
from pathlib import Path

from pydantic import BaseModel


class WeatherDataPoint(BaseModel):
    """A single data point of weather data."""

    temperature: float
    humidity: float
    wind_speed: float
    timestamp: datetime.datetime

    @classmethod
    def csv_header(cls) -> str:
        """Returns the CSV header for the data point."""
        return "timestamp,temperature,humidity,wind_speed"

    def csv_line(self) -> str:
        """Returns the CSV line for the data point."""
        return (
            f"{self.timestamp.isoformat()},{self.temperature},"
            f"{self.humidity},{self.wind_speed}"
        )

    @classmethod
    def from_csv_line(cls, line: str) -> WeatherDataPoint:
        """Creates a WeatherDataPoint from a CSV line."""
        split_line = line.split(",")
        if len(split_line) != 4:
            raise ValueError(
                "Given line has unexpexted format! Expects"
                "<timestamp:datetime,temperature:float,humidity:float,wind_speed:float>"
            )
        ts = datetime.datetime.fromisoformat(split_line[0])
        temp = float(split_line[1])
        hum = float(split_line[2])
        ws = float(split_line[3])
        return WeatherDataPoint(
            timestamp=ts, temperature=temp, humidity=hum, wind_speed=ws
        )


class WeatherData(BaseModel):
    """A collection of weather data points."""

    data: list[WeatherDataPoint]

    def to_json(self) -> str:
        """Returns the JSON representation of the data."""
        return self.model_dump_json()

    def write_csv(self, target: Path) -> None:
        """Writes the data to a CSV file."""
        with open(target, "w+") as handle:
            handle.write(WeatherDataPoint.csv_header())
            handle.write("\n")
            for d in self.data:
                handle.write(d.csv_line())
                handle.write("\n")

    @classmethod
    def read_csv(cls, src: Path) -> WeatherData:
        """Reads the data from a CSV file."""
        result = []
        with open(src, "rt") as handle:
            for line in handle.readlines()[1:]:
                result.append(WeatherDataPoint.from_csv_line(line))
        return WeatherData(data=result)


class FireRisk(BaseModel):
    """A single data point of fire risk."""

    timestamp: datetime.datetime
    ttf: float

    @classmethod
    def csv_header(cls) -> str:
        """Returns the CSV header for the data point."""
        return "timestamp,ttf"

    def csv_line(self) -> str:
        """Returns the CSV line for the data point."""
        return f"{self.timestamp.isoformat()},{self.ttf}"


class FireRiskPrediction(BaseModel):
    """A collection of fire risk predictions."""

    firerisks: list[FireRisk]

    def __str__(self) -> str:
        """Returns the string representation of the data."""
        return "\n".join(
            [FireRisk.csv_header()] + [r.csv_line() for r in self.firerisks]
        )

    def write_csv(self, target: Path) -> None:
        """Writes the data to a CSV file."""
        with open(target, "w+") as handle:
            handle.write(FireRisk.csv_header())
            handle.write("\n")
            for r in self.firerisks:
                handle.write(r.csv_line())
                handle.write("\n")
