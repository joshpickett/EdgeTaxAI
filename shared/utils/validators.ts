import { z } from 'zod';

export const AuthSchema = z.object({
  email: z.string().email().optional(),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/).optional(),
  otp: z.string().regex(/^\d{6}$/).optional(),
}).refine(data => data.email || data.phone, {
  message: "Either email or phone is required"
});

export class SharedValidator {
  static validateAuth(data: any) {
    try {
      AuthSchema.parse(data);
      return [];
    } catch (error) {
      return error.errors;
    }
  }
}
