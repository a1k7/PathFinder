const BASE_URL = '/api/proxy';

export interface DecisionPayload {
  action: string;
  amount?: number;
  user: string;
  [key: string]: any;
}

export const api = {
  decide: async (data: DecisionPayload) => {
    try {
      const res = await fetch(`${BASE_URL}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision_data: data }),
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to submit decision:', err);
      throw err;
    }
  },

  verify: async (decision_id: string, receipt: any) => {
    try {
      const res = await fetch(`${BASE_URL}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision_id, receipt }),
      });
      return await res.json();
    } catch (err) {
      console.error('Verification error:', err);
      throw err;
    }
  },

  getAuditLogs: async () => {
    try {
      const res = await fetch(`${BASE_URL}/audit`, {
        cache: 'no-store',
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) return [];
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch (err) {
      console.warn('Audit logs backend currently unreachable via proxy:', err);
      return [];
    }
  },

  replay: async (decision_id: string) => {
    try {
      const res = await fetch(`${BASE_URL}/replay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision_id }),
      });
      return await res.json();
    } catch (err) {
      console.error('Replay error:', err);
      throw err;
    }
  },

  tamper: async (decision_id: string, field: string, value: any) => {
    try {
      const res = await fetch(`${BASE_URL}/tamper`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision_id, field, new_value:value }),
      });
      return await res.json();
    } catch (err) {
      console.error('Tamper simulation error:', err);
      throw err;
    }
  },

  reloadPolicy: async () => {
    try {
      const res = await fetch(`${BASE_URL}/policy/reload`, { method: 'POST' });
      return await res.json();
    } catch (err) {
      console.error('Policy reload error:', err);
      throw err;
    }
  },
};
