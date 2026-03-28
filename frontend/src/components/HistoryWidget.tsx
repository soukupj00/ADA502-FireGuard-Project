import { useState, useEffect } from "react"
import { fetchHistory } from "@/lib/api"
import type { FireRiskReading } from "@/lib/types"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import { cn } from "@/lib/utils"

export function HistoryWidget({ geohashes }: { geohashes?: string }) {
  const [history, setHistory] = useState<FireRiskReading[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Default to today and yesterday
  const [startDate, setStartDate] = useState<Date | undefined>(() => {
    const d = new Date()
    d.setHours(d.getHours() - 12)
    return d
  })

  const [endDate, setEndDate] = useState<Date | undefined>(new Date())

  const loadHistory = async () => {
    setIsLoading(true)
    setError(null)
    try {
      // Use proper ISO string format for backend
      const startIso = startDate ? startDate.toISOString() : undefined
      const endIso = endDate ? endDate.toISOString() : undefined

      const data = await fetchHistory(startIso, endIso, geohashes)

      // Sort by prediction_timestamp descending (newest first)
      const sortedData = data.sort(
        (a, b) =>
          new Date(b.prediction_timestamp).getTime() -
          new Date(a.prediction_timestamp).getTime()
      )

      setHistory(sortedData)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError("Failed to load history")
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadHistory()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Load initially

  return (
    <Card className="mt-8 border-muted/40 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle>Risk History</CardTitle>
        <CardDescription>
          View past fire risk values. Select a custom date range to filter.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="grid flex-1 gap-2">
            <label className="text-sm font-medium">From Date</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !startDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {startDate ? (
                    format(startDate, "PPP")
                  ) : (
                    <span>Pick a date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={startDate}
                  onSelect={setStartDate}
                />
              </PopoverContent>
            </Popover>
          </div>
          <div className="grid flex-1 gap-2">
            <label className="text-sm font-medium">To Date</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !endDate && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {endDate ? format(endDate, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={endDate}
                  onSelect={setEndDate}
                />
              </PopoverContent>
            </Popover>
          </div>
          <Button onClick={loadHistory} disabled={isLoading}>
            {isLoading ? "Loading..." : "Apply Filter"}
          </Button>
        </div>

        {error && <div className="mb-4 text-red-500">{error}</div>}

        <div className="max-h-100 overflow-auto rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Location (Geohash)</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>TTF</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.length === 0 && !isLoading ? (
                <TableRow>
                  <TableCell
                    colSpan={5}
                    className="h-24 text-center text-muted-foreground"
                  >
                    No history found for the selected range.
                  </TableCell>
                </TableRow>
              ) : (
                history.map((record, index) => (
                  <TableRow
                    key={`${record.geohash}-${record.prediction_timestamp}-${index}`}
                  >
                    <TableCell>
                      {new Date(record.prediction_timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {record.geohash}
                    </TableCell>
                    <TableCell>
                      {record.risk_score !== null
                        ? record.risk_score.toFixed(1)
                        : "N/A"}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          record.risk_category === "High" ||
                          record.risk_category === "Extreme"
                            ? "bg-red-100 text-red-800"
                            : record.risk_category === "Moderate"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-green-100 text-green-800"
                        }`}
                      >
                        {record.risk_category || "Unknown"}
                      </span>
                    </TableCell>
                    <TableCell>
                      {record.ttf !== null ? record.ttf : "N/A"}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
