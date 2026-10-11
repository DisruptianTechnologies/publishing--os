const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit & { token?: string }): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...options?.headers,
    },
  });
  const json = await res.json();
  if (!res.ok) throw new ApiError(json.error?.code || 'unknown', json.error?.message || 'Request failed', res.status);
  return json.data as T;
}

class ApiError extends Error {
  constructor(public code: string, message: string, public status: number) { super(message); }
}

// Project types
export interface Project {
  id: string; name: string; description: string; project_type: string;
  status: string; target_market: string; idea_description: string;
  created_at: string; updated_at: string;
}

export interface Artifact {
  id: string; artifact_type: string; name: string; description: string;
  current_version: number; approval_state: string; compliance_state: string;
  created_at: string; updated_at: string;
}

export interface ApprovalRequest {
  id: string; project_id: string; approval_type: string; title: string;
  description: string; requested_by: string; risk_score: number;
  evidence_summary: string; expected_external_effect: string;
  estimated_cost_usd: number; expires_at: string | null; status: string;
  artifact_id: string | null; created_at: string;
}

export interface MarketplaceAccount {
  id: string; marketplace: string; name: string; auth_status: string;
  rate_limit_remaining: number; last_synced_at: string | null;
}

export interface MarketplaceListing {
  id: string; project_id: string; account_id: string; marketplace: string;
  title: string; price_usd: number; status: string; listing_url: string | null;
}

export interface Subscriber {
  id: string; email: string; first_name: string; last_name: string;
  source: string; status: string; tags: string[]; created_at: string;
}

export interface ContentDraft {
  id: string; platform: string; draft_type: string; title: string;
  body: string; policy_status: string; status: string;
}

export interface Chapter {
  chapter_number: number;
  title: string;
  status: string;
  word_count: number;
  target_word_count: number;
  flesch_score: number;
  content: string;
  notes: string[];
}

export interface CoverDimensions {
  page_count: number;
  trim_size: string;
  paper_type: string;
  spine_width_inches: number;
  total_width_inches: number;
  total_height_inches: number;
  canvas_width_px: number;
  canvas_height_px: number;
  dpi: number;
  can_print_spine_text: boolean;
  boundaries: {
    back_cover_start_x: number;
    spine_start_x: number;
    spine_end_x: number;
    front_cover_start_x: number;
  };
  barcode_box: {
    width_inches: number;
    height_inches: number;
    margin_from_bottom_inches: number;
    margin_from_spine_inches: number;
    recommended_location: string;
  };
}

export interface CompilationResult {
  project_id: string;
  title: string;
  author: string;
  total_chapters: number;
  total_words: number;
  compiled_artifacts: Array<{
    artifact_id: string;
    version: number;
    format: string;
    size_bytes: number;
    checksum: string;
  }>;
  compiled_at: string;
}

export const api = {
  projects: {
    list: (token?: string) => request<Project[]>('/api/v1/projects', { token }),
    create: (data: Partial<Project>, token?: string) => request<Project>('/api/v1/projects', { method: 'POST', body: JSON.stringify(data), token }),
    get: (id: string, token?: string) => request<Project>(`/api/v1/projects/${id}`, { token }),
    update: (id: string, data: Partial<Project>, token?: string) => request<Project>(`/api/v1/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data), token }),
    startWorkflow: (id: string, workflow_type: string, config: Record<string,unknown> = {}, token?: string) =>
      request(`/api/v1/projects/${id}/workflows`, { method: 'POST', body: JSON.stringify({ workflow_type, config }), token }),
    listArtifacts: (id: string, token?: string) => request<Artifact[]>(`/api/v1/projects/${id}/artifacts`, { token }),
  },
  approvals: {
    list: (token?: string) => request<ApprovalRequest[]>('/api/v1/approvals', { token }),
    approve: (id: string, reason: string, token?: string) => request(`/api/v1/approvals/${id}/approve`, { method: 'POST', body: JSON.stringify({ decision: 'approved', reason }), token }),
    reject: (id: string, reason: string, token?: string) => request(`/api/v1/approvals/${id}/reject`, { method: 'POST', body: JSON.stringify({ decision: 'rejected', reason }), token }),
  },
  marketplace: {
    listAccounts: (token?: string) => request<MarketplaceAccount[]>('/api/v1/marketplace/accounts', { token }),
    listListings: (projectId?: string, token?: string) => request<MarketplaceListing[]>(`/api/v1/marketplace/listings${projectId ? `?project_id=${projectId}` : ''}`, { token }),
    preflight: (data: { project_id: string; package_type: string }, token?: string) =>
      request('/api/v1/marketplace/preflight', { method: 'POST', body: JSON.stringify(data), token }),
    publish: (data: { project_id: string; account_id: string; job_type: string; payload: Record<string, unknown> }, token?: string) =>
      request('/api/v1/marketplace/publish', { method: 'POST', body: JSON.stringify(data), token }),
  },
  audience: {
    listSubscribers: (token?: string) => request<Subscriber[]>('/api/v1/audience/subscribers', { token }),
    registerSubscriber: (data: { email: string; first_name?: string; consent_granted?: boolean }, token?: string) =>
      request<Subscriber>('/api/v1/audience/subscribers', { method: 'POST', body: JSON.stringify(data), token }),
    listDrafts: (token?: string) => request<ContentDraft[]>('/api/v1/audience/drafts', { token }),
    createDraft: (data: { platform: string; draft_type: string; title: string; body: string }, token?: string) =>
      request<ContentDraft>('/api/v1/audience/drafts', { method: 'POST', body: JSON.stringify(data), token }),
  },
  compilation: {
    compile: (projectId: string, data: { title?: string; author?: string; output_formats?: string[]; trim_size?: string; paper_type?: string }, token?: string) =>
      request<CompilationResult>(`/api/v1/projects/${projectId}/compile`, { method: 'POST', body: JSON.stringify(data), token }),
    getCoverDimensions: (projectId: string, data: { page_count: number; trim_size?: string; paper_type?: string }, token?: string) =>
      request<CoverDimensions>(`/api/v1/projects/${projectId}/cover/dimensions`, { method: 'POST', body: JSON.stringify(data), token }),
  },
  writing: {
    listChapters: (projectId: string, token?: string) =>
      request<Chapter[]>(`/api/v1/projects/${projectId}/chapters`, { token }),
    assist: (projectId: string, chapterNum: number, data: { action: string; text: string }, token?: string) =>
      request<any>(`/api/v1/projects/${projectId}/chapters/${chapterNum}/assist`, { method: 'POST', body: JSON.stringify(data), token }),
  },
};

export { ApiError };
