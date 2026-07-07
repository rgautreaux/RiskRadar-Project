from pydantic import BaseModel


class ForecastPeriodOut(BaseModel):
    date: str                           # "2024-05-15"
    day_name: str                       # "Monday"
    high_temp: float                    # 85.2  (°F)
    low_temp: float                     # 62.4  (°F)
    description: str                    # "moderate rain"
    weather_main: str                   # "Rain"
    icon_code: str                      # "10d"
    wind_mph: float                     # 12.5
    precip_chance: int                  # 75  (0-100 %)
    humidity: int                       # 60  (0-100 %)
    uvi: float                          # 4.2
