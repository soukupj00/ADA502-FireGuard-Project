export const getRiskStyle = (riskScore: number, isRegional: boolean = true) => {
  let color = "#22c55e" // green
  let pattern: string

  if (riskScore >= 80) {
    color = "#ef4444" // red
    pattern = "cross" // extreme caution symbol
  } else if (riskScore >= 50) {
    color = "#f97316" // orange
    pattern = "triangle" // warning symbol
  } else if (riskScore >= 20) {
    color = "#eab308" // yellow
    pattern = "circle"
  } else {
    pattern = "none" // lowest warning
  }

  return {
    color,
    pattern,
    fillOpacity: isRegional ? 0.2 : 0.4, // Lowered base opacity since the pattern adds background color
    weight: isRegional ? 1 : 3, // Enable borders to see grid
    stroke: true, // Set to true to show borders for all
    dashArray: isRegional ? undefined : "5, 5",
  }
}

export const createPatternStyles = () => {
  return `
    .leaflet-interactive {
      /* Apply grid borders for better visibility */
      stroke-opacity: 0.8 !important;
    }

    /* Pattern definitions to use in SVG defs */
    .pattern-orange-triangle {
      fill: url(#orange-triangle) !important;
    }
    
    .pattern-red-cross {
      fill: url(#red-cross) !important;
    }
    
    .pattern-green-plus {
      fill: url(#green-plus) !important;
    }
  `
}
