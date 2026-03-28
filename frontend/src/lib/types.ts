export interface GeoJSONProperties {
  geohash: string
  name: string | null
  is_regional: boolean
  risk_score: number | null
  risk_category: string | null
  last_updated: string | null
}

export interface GeoJSONFeature {
  type: "Feature"
  geometry: {
    type: "Point"
    coordinates: [number, number]
  }
  properties: GeoJSONProperties
}

export interface RiskLevel {
  category: string
  score_range: string
  description: string
}

export interface RiskLegend {
  title: string
  description: string
  levels: RiskLevel[]
}

export interface GeoJSONResponse {
  type: "FeatureCollection"
  features: GeoJSONFeature[]
  risk_legend?: RiskLegend
}

export interface FireRiskReading {
  geohash: string
  latitude: number
  longitude: number
  risk_score: number | null
  risk_category: string | null
  ttf: number | null
  prediction_timestamp: string
  updated_at: string | null
  risk_legend?: RiskLegend
}

export interface StreamRiskData {
  location_id: string
  risk_level: string
  risk_score: number
  ttf: number
  timestamp: string
}

export interface SubscriptionRequest {
  latitude?: number | null
  longitude?: number | null
  geohash?: string | null
}

export interface SubscriptionResponse {
  geohash: string
  status: string
  message: string
  current_risk: number | null
}

export interface ApiError {
  response?: {
    data?: {
      detail?: string
    }
  }
  message: string
}

export interface GeoSearchResult {
  location: {
    x: number // longitude
    y: number // latitude
    label: string // formatted address
    bounds: [
      [number, number], // southWest
      [number, number], // northEast
    ]
    raw: unknown // Raw response from provider
  }
}
