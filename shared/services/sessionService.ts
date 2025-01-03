export interface SessionData {
  userId: string;
  deviceInfo: string;
  lastActivity: Date;
}

export class SessionService {
  private static instance: SessionService;
  
  static getInstance(): SessionService {
    if (!SessionService.instance) {
      SessionService.instance = new SessionService();
    }
    return SessionService.instance;
  }

  async createSession(data: SessionData): Promise<string> {
    const response = await fetch('/api/auth/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error('Failed to create session');
    }
    
    const result = await response.json();
    return result.sessionId;
  }
}
