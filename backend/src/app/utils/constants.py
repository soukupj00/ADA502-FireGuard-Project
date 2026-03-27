from app.schemas import RiskLegend, RiskLevel

RISK_LEGEND_DATA = RiskLegend(
    levels=[
        RiskLevel(
            category="Low",
            score_range="0-30",
            description="Time to flashover is predicted to be greater than 30 minutes."
            "Normal conditions.",
        ),
        RiskLevel(
            category="Moderate",
            score_range="30-60",
            description="Time to flashover is predicted to be "
            "between 15 and 30 minutes."
            "Elevated caution is advised.",
        ),
        RiskLevel(
            category="High",
            score_range="60-80",
            description="Time to flashover is predicted to be between 5 and 15 minutes."
            "Significant risk of rapid fire spread.",
        ),
        RiskLevel(
            category="Extreme",
            score_range="80-100",
            description="Time to flashover is predicted to be under 5 minutes. "
            "Critical emergency conditions; immediate action required.",
        ),
    ]
)
