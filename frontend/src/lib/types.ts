export interface GeoJSONFeature {
    type: "Feature";
    geometry: {
        type: "Point";
        coordinates: [number, number];
    };
    properties: {
        geohash: string;
        name: string;
        is_regional: boolean;
        risk_score: number;
        risk_category: string;
        last_updated: string;
    };
}

export interface GeoJSONResponse {
    type: "FeatureCollection";
    features: GeoJSONFeature[];
}
