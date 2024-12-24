export class TaxCalculationError extends Error {
    constructor(message: string, public readonly code: string) {
        super(message);
        this.name = 'TaxCalculationError';
    }
}

export class IRSComplianceError extends Error {
    constructor(message: string, public readonly code: string) {
        super(message);
        this.name = 'IRSComplianceError';
    }
}

export class DeductionValidationError extends Error {
    constructor(message: string, public readonly code: string) {
        super(message);
        this.name = 'DeductionValidationError';
    }
}

export class ReportGenerationError extends Error {
    constructor(message: string, public readonly code: string) {
        super(message);
        this.name = 'ReportGenerationError';
    }
}

export class ReportValidationError extends Error {
    constructor(message: string, public readonly code: string) {
        super(message);
        this.name = 'ReportValidationError';
    }
}
