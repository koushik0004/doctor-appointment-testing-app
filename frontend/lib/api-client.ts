const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export type ApiRequestOptions = Omit<RequestInit, "body" | "headers"> & {
  body?: unknown;
  headers?: HeadersInit;
};

function extractErrorMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  if ("error" in payload && payload.error && typeof payload.error === "object") {
    const errorPayload = payload.error as Record<string, unknown>;

    if (typeof errorPayload.message === "string" && errorPayload.message.trim()) {
      return errorPayload.message;
    }
  }

  if ("detail" in payload) {
    const detail = (payload as Record<string, unknown>).detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail)) {
      const parts = detail
        .map((entry) => {
          if (typeof entry === "string") {
            return entry;
          }

          if (entry && typeof entry === "object") {
            const detailEntry = entry as Record<string, unknown>;

            if (typeof detailEntry.msg === "string") {
              return detailEntry.msg;
            }
          }

          return null;
        })
        .filter((message): message is string => Boolean(message));

      if (parts.length > 0) {
        return parts.join(", ");
      }
    }
  }

  return null;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message = extractErrorMessage(payload) ?? "Request failed";

    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { body, headers, ...restOptions } = options;
  const hasBody = body !== undefined;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...restOptions,
    headers: {
      Accept: "application/json",
      ...(hasBody ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    body: hasBody ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  return parseResponse<T>(response);
}

export const apiClient = {
  get: <T>(path: string, options?: ApiRequestOptions) =>
    apiRequest<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
    apiRequest<T>(path, { ...options, method: "POST", body }),
  patch: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
    apiRequest<T>(path, { ...options, method: "PATCH", body }),
};
