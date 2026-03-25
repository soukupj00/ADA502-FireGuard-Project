// Defines the SVG patterns that can be used as fill colors
export function MapPatterns() {
  // To reduce the number of symbols by ~1/5th, we significantly increase the pattern box size.
  // 45x45 gives much more space between symbols than the old 20x20.
  // The symbols are centered in this new larger box.
  return (
    <svg
      style={{ width: 0, height: 0, position: "absolute" }}
      aria-hidden="true"
    >
      <defs>
        {/* Extreme Risk (Red) - Cross / X symbol */}
        <pattern
          id="pattern-cross"
          x="0"
          y="0"
          width="45"
          height="45"
          patternUnits="userSpaceOnUse"
        >
          <rect width="45" height="45" fill="#ef4444" fillOpacity="0.2" />
          <path
            d="M17,17 L28,28 M28,17 L17,28"
            stroke="#ef4444"
            strokeWidth="2.5"
            strokeLinecap="round"
          />
        </pattern>

        {/* High Risk (Orange) - Triangle symbol */}
        <pattern
          id="pattern-triangle"
          x="0"
          y="0"
          width="45"
          height="45"
          patternUnits="userSpaceOnUse"
        >
          <rect width="45" height="45" fill="#f97316" fillOpacity="0.2" />
          <path
            d="M22.5,15 L30,28 L15,28 Z"
            fill="none"
            stroke="#f97316"
            strokeWidth="2"
            strokeLinejoin="round"
          />
        </pattern>

        {/* Medium Risk (Yellow) - Circle symbol */}
        <pattern
          id="pattern-circle"
          x="0"
          y="0"
          width="45"
          height="45"
          patternUnits="userSpaceOnUse"
        >
          <rect width="45" height="45" fill="#eab308" fillOpacity="0.2" />
          <circle
            cx="22.5"
            cy="22.5"
            r="6"
            fill="none"
            stroke="#eab308"
            strokeWidth="2"
          />
        </pattern>

        {/* Low Risk (Green) - Plus symbol */}
        <pattern
          id="pattern-plus"
          x="0"
          y="0"
          width="45"
          height="45"
          patternUnits="userSpaceOnUse"
        >
          <rect width="45" height="45" fill="#22c55e" fillOpacity="0.2" />
          <path
            d="M22.5,15 L22.5,30 M15,22.5 L30,22.5"
            stroke="#22c55e"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </pattern>
      </defs>
    </svg>
  )
}
