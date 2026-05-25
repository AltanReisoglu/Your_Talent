export type HookSummary = {
  events?: unknown[];
  [key: string]: unknown;
};

export type InvokeRequest = {
  user_id: string;
  session_id: string;
  message: string;
};

export type InvokeResponse = {
  user_id: string;
  session_id: string;
  thread_id: string;
  response: string;
  hooks?: HookSummary | null;
};

export type WikiPageSummary = {
  path: string;
  title: string;
  summary: string;
  category: string;
  last_updated: string;
  review_status: string;
  related: string[];
};

export type WikiSearchResponse = {
  results: WikiPageSummary[];
};

export type WikiPageResponse = {
  page: {
    path: string;
    title: string;
    content: string;
    frontmatter: Record<string, unknown>;
    sources: string[];
    related: string[];
    last_updated: string;
    review_status: string;
  };
};

export type IngestSubmissionRequest = {
  user_id: string;
  type: "note" | "url" | "excerpt" | "attachment";
  content: string;
  notes?: string;
};

export type IngestSubmissionResponse = {
  submission_id: string;
  status: "queued" | "running" | "completed" | "blocked" | "failed";
  message: string;
};

export type AccountDeleteResponse = {
  status: "requested";
  effective_after: string;
  retained_data_notice: string;
};

type ApiErrorShape = {
  error?: {
    code?: string;
    message?: string;
    retryable?: boolean;
  };
};

export class FinWikiApiError extends Error {
  readonly code: string;
  readonly retryable: boolean;
  readonly status: number;

  constructor(message: string, code: string, retryable: boolean, status: number) {
    super(message);
    this.name = "FinWikiApiError";
    this.code = code;
    this.retryable = retryable;
    this.status = status;
  }
}

const DEFAULT_BASE_URL = "http://localhost:8000";

export function getApiBaseUrl(): string {
  const configured = process.env.EXPO_PUBLIC_FINWIKI_API_BASE_URL;
  return (configured && configured.trim()) || DEFAULT_BASE_URL;
}

function url(path: string, params?: Record<string, string | number | undefined>): string {
  const base = getApiBaseUrl().replace(/\/$/, "");
  const query = params
    ? Object.entries(params)
        .filter(([, value]) => value !== undefined && String(value).trim() !== "")
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
        .join("&")
    : "";
  return `${base}${path}${query ? `?${query}` : ""}`;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
  params?: Record<string, string | number | undefined>
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url(path, params), {
      ...init,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(init?.headers ?? {})
      }
    });
  } catch (error) {
    throw new FinWikiApiError(
      error instanceof Error ? error.message : "Network request failed.",
      "network_error",
      true,
      0
    );
  }

  const text = await response.text();
  const data = text ? (JSON.parse(text) as T & ApiErrorShape) : ({} as T & ApiErrorShape);
  if (!response.ok || data.error) {
    const error = data.error ?? {};
    throw new FinWikiApiError(
      error.message ?? `FinWiki API returned HTTP ${response.status}.`,
      error.code ?? "api_error",
      Boolean(error.retryable),
      response.status
    );
  }
  return data as T;
}

export function invokeFinWiki(request: InvokeRequest): Promise<InvokeResponse> {
  return requestJson<InvokeResponse>("/invoke", {
    method: "POST",
    body: JSON.stringify(request)
  });
}

export function searchWiki(query: string, limit = 10): Promise<WikiSearchResponse> {
  return requestJson<WikiSearchResponse>("/wiki/search", undefined, { q: query, limit });
}

export function loadWikiPage(path: string): Promise<WikiPageResponse> {
  return requestJson<WikiPageResponse>("/wiki/page", undefined, { path });
}

export function submitIngest(request: IngestSubmissionRequest): Promise<IngestSubmissionResponse> {
  return requestJson<IngestSubmissionResponse>("/ingest-submissions", {
    method: "POST",
    body: JSON.stringify(request)
  });
}

export function requestAccountDeletion(
  userId: string,
  confirmation: boolean
): Promise<AccountDeleteResponse> {
  return requestJson<AccountDeleteResponse>("/account/delete", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, confirmation })
  });
}
