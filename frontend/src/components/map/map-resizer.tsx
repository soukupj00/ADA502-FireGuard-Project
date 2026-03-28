import { useEffect } from "react"
import { useMap } from "react-leaflet"

/**
 * A component that attaches a ResizeObserver to the Leaflet map container.
 * When the container's size changes (e.g. from CSS transitions like flex flex-1 changes),
 * it calls map.invalidateSize() so Leaflet can fetch the missing tiles and redraw correctly.
 */
export function MapResizer() {
  const map = useMap()

  useEffect(() => {
    const container = map.getContainer()

    const resizeObserver = new ResizeObserver(() => {
      // Invalidate the size to make Leaflet recalculate bounds and fetch tiles
      map.invalidateSize()
    })

    resizeObserver.observe(container)

    return () => {
      resizeObserver.disconnect()
    }
  }, [map])

  return null
}
