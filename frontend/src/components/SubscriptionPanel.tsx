import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { LocationSubscriber } from "@/components/LocationSubscriber"
import RiskAlertsWidget from "@/components/RiskAlertsWidget"
import { cn } from "@/lib/utils"

interface SubscriptionPanelProps {
  isSelectionMode: boolean
  selectedLocation: { lat: number; lng: number } | null
  onSubscriptionSuccess: () => void
}

export function SubscriptionPanel({
  isSelectionMode,
  selectedLocation,
  onSubscriptionSuccess,
}: SubscriptionPanelProps) {
  return (
    <div className="flex flex-col gap-8">
      <Card
        className={cn(
          "shadow-sm transition-all duration-300",
          selectedLocation
            ? "border-primary ring-2 ring-primary ring-inset"
            : ""
        )}
      >
        <CardHeader className="pb-4">
          <CardTitle>Subscribe to Area</CardTitle>
          <CardDescription>
            {isSelectionMode
              ? "Click the map to select coordinates"
              : "Click 'Select Area' on the map to pick a new location"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LocationSubscriber
            selectedLat={selectedLocation?.lat ?? null}
            selectedLon={selectedLocation?.lng ?? null}
            onSuccess={onSubscriptionSuccess}
          />
        </CardContent>
      </Card>

      <Card className="flex-1 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle>My Subscriptions</CardTitle>
          <CardDescription>
            Manage your personalized risk alerts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RiskAlertsWidget />
        </CardContent>
      </Card>
    </div>
  )
}
