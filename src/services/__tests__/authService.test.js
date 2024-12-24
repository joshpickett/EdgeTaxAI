import { sendOneTimePassword, verifyOneTimePassword, getProfile, updateProfile } from '../authService';

describe('AuthService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    console.error = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('sendOneTimePassword', () => {
    const mockIdentifier = 'test@example.com';
    const mockResponse = { success: true, message: 'One-Time Password sent' };

    it('should send One-Time Password successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await sendOneTimePassword(mockIdentifier);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/send-one-time-password`,
        expect.objectContaining({
          method: 'POST',
          body: expect.any(String)
        })
      );
    });

    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(sendOneTimePassword(mockIdentifier)).rejects.toThrow('Failed to send One-Time Password');
      expect(console.error).toHaveBeenCalled();
    });

    it('should handle different One-Time Password types', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      await sendOneTimePassword(mockIdentifier, 'login');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining('"type":"login"')
        })
      );
    });
  });

  describe('verifyOneTimePassword', () => {
    const mockIdentifier = 'test@example.com';
    const mockOneTimePassword = '123456';
    const mockResponse = { success: true, token: 'test-token' };

    it('should verify One-Time Password successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      });

      const result = await verifyOneTimePassword(mockIdentifier, mockOneTimePassword);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/verify-one-time-password`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ identifier: mockIdentifier, one_time_password_code: mockOneTimePassword })
        })
      );
    });

    it('should handle invalid One-Time Password', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Invalid One-Time Password' })
      });

      await expect(verifyOneTimePassword(mockIdentifier, 'wrong-one-time-password'))
        .rejects.toThrow('Failed to verify One-Time Password');
    });
  });

  describe('getProfile', () => {
    const mockProfile = { id: 1, name: 'Test User' };

    it('should fetch profile successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockProfile)
      });

      const result = await getProfile();

      expect(result).toEqual(mockProfile);
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/profile`,
        expect.objectContaining({
          method: 'GET',
          credentials: 'include'
        })
      );
    });

    it('should handle unauthorized access', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Unauthorized' })
      });

      await expect(getProfile()).rejects.toThrow('Failed to fetch profile details');
    });
  });

  describe('updateProfile', () => {
    const mockProfileData = {
      fullName: 'New Name',
      email: 'new@example.com',
      phoneNumber: '1234567890'
    };

    it('should update profile successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ ...mockProfileData, id: 1 })
      });

      const result = await updateProfile(
        mockProfileData.fullName,
        mockProfileData.email,
        mockProfileData.phoneNumber
      );

      expect(result).toEqual(expect.objectContaining(mockProfileData));
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/profile`,
        expect.objectContaining({
          method: 'PUT',
          body: expect.any(String)
        })
      );
    });

    it('should handle validation errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ error: 'Invalid email format' })
      });

      await expect(updateProfile('Test', 'invalid-email', '123'))
        .rejects.toThrow('Failed to update profile');
    });
  });
});
