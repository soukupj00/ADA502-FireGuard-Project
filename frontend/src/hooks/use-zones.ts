import useSWR from 'swr';
import { fetchZones } from '@/lib/api';
import type {GeoJSONResponse} from '@/lib/types';

export function useZones(regionalOnly: boolean = true) {
    const { data, error, isLoading } = useSWR<GeoJSONResponse>(
        ['/zones', regionalOnly],
        () => fetchZones(regionalOnly),
        {
            refreshInterval: 60000, // Refresh every minute
            revalidateOnFocus: false
        }
    );

    return {
        zones: data,
        isLoading,
        isError: error,
    };
}
