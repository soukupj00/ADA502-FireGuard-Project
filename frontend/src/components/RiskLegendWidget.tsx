import type { RiskLegend } from "@/lib/types"

interface RiskLegendWidgetProps {
  legend?: RiskLegend | null
}

const getColorClasses = (category: string) => {
  const cat = category.toLowerCase()
  if (cat.includes("extreme") || cat.includes("very high"))
    return {
      bg: "bg-red-600",
      text: "text-red-700 dark:text-red-400",
      ring: "ring-red-600/20",
    }
  if (cat.includes("high"))
    return {
      bg: "bg-orange-500",
      text: "text-orange-700 dark:text-orange-400",
      ring: "ring-orange-600/20",
    }
  if (cat.includes("moderate") || cat.includes("medium"))
    return {
      bg: "bg-yellow-500",
      text: "text-yellow-700 dark:text-yellow-400",
      ring: "ring-yellow-600/20",
    }
  if (cat.includes("low"))
    return {
      bg: "bg-green-500",
      text: "text-green-700 dark:text-green-400",
      ring: "ring-green-600/20",
    }
  return {
    bg: "bg-gray-500",
    text: "text-gray-700 dark:text-gray-400",
    ring: "ring-gray-600/20",
  }
}

export function RiskLegendWidget({ legend }: RiskLegendWidgetProps) {
  if (legend) {
    return (
      <div className="grid grid-cols-1 gap-4 rounded-lg border bg-muted/20 p-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
        {legend.levels.map((level, i) => {
          const colors = getColorClasses(level.category)
          return (
            <div
              key={i}
              className="flex flex-col items-center justify-start gap-2 rounded-lg bg-background/50 p-3 text-center shadow-sm"
              title={level.description}
            >
              <div className="flex items-center gap-2">
                <div
                  className={`h-4 w-4 rounded shadow-sm ring-1 ${colors.bg} ${colors.ring}`}
                ></div>
                <span className={`font-bold ${colors.text}`}>
                  {level.category}
                </span>
              </div>
              <span className="flex-1 text-xs text-muted-foreground">
                {level.description}
              </span>
              <span className="mt-auto rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                Score: {level.score_range}
              </span>
            </div>
          )
        })}
      </div>
    )
  }

  // Fallback if no legend is provided by the API
  return (
    <div className="grid grid-cols-1 gap-4 rounded-lg border bg-muted/20 p-4 text-sm sm:grid-cols-2 md:grid-cols-4">
      <div className="flex items-center justify-center gap-2">
        <div className="h-4 w-4 rounded bg-red-500 shadow-sm ring-1 ring-red-600/20"></div>
        <span className="font-medium text-red-700 dark:text-red-400">
          High Risk
        </span>
      </div>
      <div className="flex items-center justify-center gap-2">
        <div className="h-4 w-4 rounded bg-orange-500 shadow-sm ring-1 ring-orange-600/20"></div>
        <span className="font-medium text-orange-700 dark:text-orange-400">
          Medium-High
        </span>
      </div>
      <div className="flex items-center justify-center gap-2">
        <div className="h-4 w-4 rounded bg-yellow-500 shadow-sm ring-1 ring-yellow-600/20"></div>
        <span className="font-medium text-yellow-700 dark:text-yellow-400">
          Medium-Low
        </span>
      </div>
      <div className="flex items-center justify-center gap-2">
        <div className="h-4 w-4 rounded bg-green-500 shadow-sm ring-1 ring-green-600/20"></div>
        <span className="font-medium text-green-700 dark:text-green-400">
          Low Risk
        </span>
      </div>
    </div>
  )
}
