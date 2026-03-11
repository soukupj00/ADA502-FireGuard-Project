import { MapContainer, TileLayer, Rectangle, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { LatLngExpression, LatLngBoundsExpression } from 'leaflet';
import { useZones } from '@/hooks/use-zones';
import { useMemo } from 'react';
import Geohash from 'latlon-geohash';

interface MapViewProps {
  center?: LatLngExpression;
  zoom?: number;
}

export function MapView({ center = [58.359375, 10.546875] as LatLngExpression, zoom = 6 }: MapViewProps) {
  const { zones, isLoading, isError } = useZones();

  const getColor = (riskScore: number) => {
    if (riskScore >= 80) return '#ef4444'; // red-500
    if (riskScore >= 50) return '#f97316'; // orange-500
    if (riskScore >= 20) return '#eab308'; // yellow-500
    return '#22c55e'; // green-500
  };

  const mapData = useMemo(() => {
    if (!zones) return [];

    console.group('Map Data Debug');
    console.log('Total features:', zones.features.length);

    const processedData = zones.features.map((feature, index) => {
      const { geohash, risk_score, name, risk_category } = feature.properties;
      
      if (!geohash) {
          console.warn(`Feature at index ${index} missing geohash`, feature);
          return null;
      }

      try {
          const bounds = Geohash.bounds(geohash);

          const leafletBounds: LatLngBoundsExpression = [
            [bounds.sw.lat, bounds.sw.lon],
            [bounds.ne.lat, bounds.ne.lon]
          ];
    
          return {
            id: geohash,
            name,
            bounds: leafletBounds,
            riskScore: risk_score,
            riskCategory: risk_category
          };
      } catch (e) {
          console.error(`Invalid geohash: ${geohash}`, e);
          return null;
      }
    }).filter((item): item is NonNullable<typeof item> => item !== null);

    console.log('Processed map data:', processedData);
    console.groupEnd();

    return processedData;
  }, [zones]);

  if (isLoading) {
    return (
        <div className="h-full w-full flex items-center justify-center bg-muted/20 min-h-[400px] animate-pulse">
            <span className="text-muted-foreground font-medium">Loading map data...</span>
        </div>
    );
  }

  if (isError) {
    return (
        <div className="h-full w-full flex flex-col items-center justify-center bg-red-50 text-red-500 p-4 text-center min-h-[400px]">
            <p className="font-bold">Error loading map data</p>
            <p className="text-sm">Please try again later.</p>
        </div>
    );
  }

  return (
    <div className="h-full w-full relative z-0">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        scrollWheelZoom={true} 
        style={{ height: '100%', width: '100%', minHeight: '400px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {mapData.map((data) => (
          <Rectangle
            key={data.id}
            bounds={data.bounds}
            pathOptions={{ 
              color: getColor(data.riskScore),
              fillColor: getColor(data.riskScore),
              fillOpacity: 0.5,
              weight: 1,
              stroke: false // Remove stroke to make gaps less visible if they are caused by border width
            }}
          >
            <Popup>
              <div className="text-sm p-1 min-w-[150px]">
                <h3 className="font-semibold text-base mb-2">{data.name}</h3>
                <div className="grid grid-cols-[auto_1fr] gap-x-2 gap-y-1 text-xs">
                    <span className="text-muted-foreground font-medium">Geohash:</span>
                    <span className="font-mono text-right">{data.id}</span>
                    
                    <span className="text-muted-foreground font-medium">Risk Score:</span>
                    <span className={`font-bold text-right ${data.riskScore > 50 ? 'text-red-600' : 'text-green-600'}`}>
                        {data.riskScore.toFixed(1)}
                    </span>
                    
                    <span className="text-muted-foreground font-medium">Category:</span>
                    <span className="capitalize text-right">{data.riskCategory}</span>
                </div>
              </div>
            </Popup>
          </Rectangle>
        ))}
      </MapContainer>
    </div>
  );
}
