import { getToken } from "./auth";

const API_BASE_URL = "http://localhost:8001";

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as any),
  };

  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail: any = undefined;
    try {
      detail = await res.json();
    } catch {
      // ignore
    }
    const msg = detail?.detail || `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return (await res.json()) as T;
}

export async function login(email: string, password: string): Promise<{ access_token: string }> {
  return apiRequest("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function me(): Promise<any> {
  return apiRequest("/api/v1/auth/me");
}

export type WordOperation = {
  type: "replace_selection" | "insert_after_selection" | "insert_before_selection" | "comment_on_quote";
  new_text?: string | null;
  quote?: string | null;
  severity?: "info" | "warning" | "risk" | null;
  highlight?: boolean;
  comment?: { title?: string | null; body: string } | null;
};

export async function improveWriting(selectionText: string, instructions?: string): Promise<{ operations: WordOperation[] }>
{
  return apiRequest("/api/v1/word/improve-writing", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selection_text: selectionText, instructions }),
  });
}

export async function draftClause(payload: {
  clause_request: string;
  context_text?: string;
  style_instructions?: string;
}): Promise<{ operations: WordOperation[] }>
{
  return apiRequest("/api/v1/word/draft-clause", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function proofreadSelection(selectionText: string): Promise<{ operations: WordOperation[] }>
{
  return apiRequest("/api/v1/word/proofread", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selection_text: selectionText }),
  });
}
