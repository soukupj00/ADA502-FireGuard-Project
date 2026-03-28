import { useState, useEffect } from "react"
import type { ApiError } from "@/lib/types"
import { subscribeToLocation } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import keycloak from "@/keycloak"
import { useSWRConfig } from "swr"
import { useLocationStream } from "@/hooks/use-location-stream"

interface LocationSubscriberProps {
  selectedLat: number | null
  selectedLon: number | null
  onSuccess?: () => void
}

export function LocationSubscriber({
  selectedLat,
  selectedLon,
  onSuccess,
}: LocationSubscriberProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [pendingGeohash, setPendingGeohash] = useState<string | null>(null)
  const { mutate } = useSWRConfig()

  const { riskData, error: streamError } = useLocationStream(pendingGeohash)

  useEffect(() => {
    if (riskData) {
      toast.info("Real-time risk data received!", {
        description: `Risk Level: ${riskData.risk_level} (Score: ${riskData.risk_score?.toFixed(2)})`,
      })
      // Clear pending geohash once data is received
      setPendingGeohash(null)
      // Re-fetch zones to show on map
      mutate(["/zones", false])
      mutate("/users/me/subscriptions/")
      if (onSuccess) onSuccess()
    }
  }, [riskData, mutate, onSuccess])

  useEffect(() => {
    if (streamError) {
      toast.error("Stream Error", {
        description:
          "Failed to receive real-time updates for the new location.",
      })
      setPendingGeohash(null)
    }
  }, [streamError])

  const handleSubscribe = async () => {
    // Safety check: is the user actually logged in?
    if (!keycloak.authenticated) {
      toast.error("Authentication Required", {
        description: "Please log in to subscribe to alerts.",
      })
      await keycloak.login()
      return
    }

    if (selectedLat === null || selectedLon === null) return

    setIsSubmitting(true)
    try {
      const response = await subscribeToLocation({
        latitude: selectedLat,
        longitude: selectedLon,
      })

      // The backend returns a status: "active" (already tracked) or "pending" (new zone)
      toast.success("Subscription Successful!", {
        description: response.message || "You are now tracking this location.",
      })

      // If the zone is newly created (pending), we wait for the stream
      if (response.status === "pending") {
        setPendingGeohash(response.geohash)
      } else {
        // If it was already active, we just refresh everything
        await mutate(["/zones", false])
        await mutate("/users/me/subscriptions/")
        if (onSuccess) onSuccess()
      }
    } catch (error: unknown) {
      const apiError = error as ApiError
      const message = apiError.message || "An unknown error occurred"
      const detail = apiError.response?.data?.detail

      toast.error("Subscription Failed", {
        description: detail || message,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col gap-2">
      {selectedLat !== null && selectedLon !== null ? (
        <p className="text-sm text-muted-foreground">
          Selected: {selectedLat.toFixed(4)}, {selectedLon.toFixed(4)}
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">
          Select a location on the map to subscribe.
        </p>
      )}

      {pendingGeohash && (
        <div className="mb-2 animate-pulse rounded bg-muted p-2 text-xs">
          Waiting for risk analysis...
        </div>
      )}

      <Button
        onClick={handleSubscribe}
        disabled={
          isSubmitting ||
          !!pendingGeohash ||
          selectedLat === null ||
          selectedLon === null
        }
      >
        {isSubmitting
          ? "Subscribing..."
          : pendingGeohash
            ? "Analyzing..."
            : "Subscribe to Alerts"}
      </Button>
    </div>
  )
}
