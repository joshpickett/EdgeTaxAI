export interface Form1099KECData {
    // Payment Settlement Entity (PSE) Information
    pse: {
        name: string;
        tin: string;
        phone: string;
        address: {
            street: string;
            city: string;
            state: string;
            zipCode: string;
        };
    };
    
    // Payee Information
    payee: {
        name: string;
        tin: string;
        accountNumber?: string;
        address: {
            street: string;
            city: string;
            state: string;
            zipCode: string;
        };
    };
    
    // Transaction Information
    transactions: {
        grossAmount: number;
        cardNotPresent: number;
        paymentCardTransactions: number;
        thirdPartyNetwork: number;
        federalTaxWithheld: number;
        monthlyAmounts: {
            [key: string]: number; // month1 through month12
        };
    };
    
    // State Tax Information (Optional)
    stateTaxInfo?: {
        state: string;
        stateId: string;
        stateIncome: number;
        stateTaxWithheld: number;
    }[];
    
    // Form Metadata
    formMetadata: {
        taxYear: number;
        corrected: boolean;
        void: boolean;
        filerCategory: 'PSE' | 'EPF';
    };
}
