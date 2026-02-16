import datetime
import logging
from zoneinfo import ZoneInfo

from frcm.datamodel import model as dm
from frcm.fireriskmodel.compute import compute

logger = logging.getLogger(__name__)


def transform_met_data_to_model(met_json: dict) -> dm.WeatherData:
    """
    Parses the raw JSON from MET.no and converts it into the
    internal WeatherData object required by the FRCM compute function.
    """
    timeseries = met_json["properties"]["timeseries"]
    data_points = []

    for entry in timeseries:
        time_str = entry["time"]
        # MET.no uses 'Z' for UTC, fromisoformat handles +00:00
        dt = datetime.datetime.fromisoformat(time_str.replace("Z", "+00:00"))

        instant_details = entry["data"]["instant"]["details"]

        # Create WeatherDataPoint with fields matching the datamodel
        dp = dm.WeatherDataPoint(
            timestamp=dt,
            temperature=instant_details.get("air_temperature"),
            humidity=instant_details.get("relative_humidity"),
            wind_speed=instant_details.get("wind_speed", 0.0)
        )
        data_points.append(dp)

    # Wrap the list of points in the WeatherData container
    return dm.WeatherData(data=data_points)


def calculate_risk(met_json: dict):
    """
    Orchestrates the risk calculation:
    MET JSON -> WeatherData -> Compute() -> Result
    """
    try:
        # 1. Transform Data
        weather_data = transform_met_data_to_model(met_json)

        # 2. Run the FRCM Simulation
        # This returns a dm.FireRiskPrediction object containing a list of risks
        prediction_result = compute(weather_data)

        # 3. Extract the most relevant result
        # The compute function returns a simulation for the whole forecast period.
        # We take the first element as the "current" risk.
        if prediction_result.firerisks:
            current_risk = prediction_result.firerisks[0]

            return {
                "timestamp": current_risk.timestamp,
                "ttf": current_risk.ttf,  # Time To Flashover (Lower = Higher Risk)
            }

        return None

    except Exception as e:
        logger.error(f"Error in risk calculation: {e}")
        return None
