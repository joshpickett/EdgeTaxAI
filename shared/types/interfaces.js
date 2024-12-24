export interface TripData {
    startLocation: string;
    endLocation: string;
    purpose: string;
    recurring: boolean;
}

export interface MileageRecord {
    id: string;
    userId: string;
    distance: number;
    taxDeduction: number;
    date: string;
}

export interface MileageHistory {
    userId: string;
    records: MileageRecord[];
}

export interface ApiError {
    message: string;
    statusCode: number;
}
