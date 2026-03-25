import useSWR from "swr"
import { apiClient } from "@/lib/api"
import type { GeoJSONResponse } from "@/lib/types"

const fetcher = async (url: string) => {
  const res = await apiClient.get(url)
  return res.data
}

export function useSubscriptions() {
  const { data, error, isLoading, mutate } = useSWR<GeoJSONResponse>(
    "/users/me/subscriptions/",
    fetcher
  )

  return {
    subscriptions: data,
    isLoading,
    isError: error,
    mutate, // Export mutate to easily trigger a re-fetch after a new subscription or deletion
  }
}
