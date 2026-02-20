import sys
from pathlib import Path

from frcm.datamodel.model import (
    FireRisk as FireRisk,
)
from frcm.datamodel.model import (
    FireRiskPrediction as FireRiskPrediction,
)
from frcm.datamodel.model import (
    WeatherData,
)
from frcm.datamodel.model import (
    WeatherDataPoint as WeatherDataPoint,
)
from frcm.fireriskmodel.compute import compute


def console_main() -> None:
    """The main entrypoint for the console application."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Wrong number of arguments provided! Please provide one reference to a"
            " CSV file with weatherdata to compute the fire risk"
        )
        sys.exit(1)

    file = Path(sys.argv[1])
    wd = WeatherData.read_csv(file)

    if len(wd.data) == 0:
        print(
            "Given file did not contain any data points! Please check the input"
            " format! Aborting..."
        )
        sys.exit(1)

    print(
        f"Computing FireRisk for given data in '{file.absolute()}'"
        f" ({len(wd.data)} datapoints)",
        end="\n\n",
    )

    risks = compute(wd)

    if len(sys.argv) == 3:
        output = Path(sys.argv[2])
        risks.write_csv(output)
        print(f"Calculated fire risks written to '{output.absolute()}'")
    else:
        print(risks)
