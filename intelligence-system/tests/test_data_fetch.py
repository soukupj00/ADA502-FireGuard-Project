import asyncio

from met_api import fetch_weather
from risk_calculator import calculate_risk


async def test() -> None:
    print("--- Testing Fetch ---")
    # Use Bergen coordinates
    data = await fetch_weather(60.3913, 5.3221)

    if data:
        print("✅ Fetch Successful")
        print(f"Received {len(data['properties']['timeseries'])} timesteps")

        print("\n--- Testing Calculation ---")
        try:
            result = calculate_risk(data)
            if result:
                print("Calculation Successful!")
                print(f"Time to Flashover (TTF): {result['ttf']}")
            else:
                print("❌ Calculation returned None")
        except Exception as e:
            print(f"❌ Calculation Crashed: {e}")
    else:
        print("❌ Fetch Failed")


if __name__ == "__main__":
    asyncio.run(test())
