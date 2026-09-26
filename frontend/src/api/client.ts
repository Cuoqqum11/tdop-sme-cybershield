import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export interface Summary {
  total_alerts: number;
  total_incidents: number;
  system_status: string;
}

export interface Incident {
  id: number;
  title: string;
  status: string;
  risk_score: number;
  entity_type: string;
  entity_value: string;
  alert_count: number;
  explanation: string;
  recommended_action: string;
  first_seen: string;
  last_seen: string;
}

export interface ResponseAction {
  id: number;
  incident_id: number;
  action_type: string;
  status: string;
  mode: string;
  details: string | null;
}

export interface SMEProfile {
  id?: number;
  company_type: string;
  company_size: string;
  services: string;
  security_mode: string;
  language: string;
}

export const saveProfile = (data: SMEProfile) => api.post('/api/v1/onboarding/profile', data);
export const getProfile = () => api.get('/api/v1/onboarding/profile');
export const getSummary = () => api.get<Summary>('/api/v1/dashboard/summary');
export const getIncidents = () => api.get<Incident[]>('/api/v1/incidents');
export const getResponseHistory = () => api.get<ResponseAction[]>('/api/v1/response/history');
export const approveAction = (id: number) => api.post(`/api/v1/response/${id}/approve`);