import { FilingStatus, DeductionType } from './tax';

export interface Form1040TaxpayerInfo {
    firstName: string;
    lastName: string;
    ssn: string;
    spouseFirstName?: string;
    spouseLastName?: string;
    spouseSSN?: string;
    filingStatus: FilingStatus;
    includePlatformData?: Record<string, boolean>;
    includeTrackedExpenses?: boolean;
    address: {
        street: string;
        city: string;
        state: string;
        zipCode: string;
    };
}

export interface Form1040Income {
    wages: number;
    interest: number;
    dividends: number;
    business: number;
    capitalGains: number;
    otherIncome: number;
    totalIncome: number;
}

export interface Form1040Adjustments {
    selfEmploymentTax: number;
    healthInsurance: number;
    retirementContributions: number;
    otherAdjustments: number;
    totalAdjustments: number;
}

export interface Form1040Credits {
    qualifyingChildren: number;
    childTaxCredit: number;
    earnedIncomeCredit: number;
    otherCredits: number;
    totalCredits: number;
}

export interface Form1040Payments {
    federalWithheld: number;
    estimatedTaxPaid: number;
    otherPayments: number;
    totalPayments: number;
}

export interface Form1040Data {
    year: number;
    taxpayerInfo: Form1040TaxpayerInfo;
    income: Form1040Income;
    adjustments: Form1040Adjustments;
    credits: Form1040Credits;
    payments: Form1040Payments;
    schedules?: {
        scheduleC?: boolean;
        scheduleE?: boolean;
        scheduleF?: boolean;
    };
}
