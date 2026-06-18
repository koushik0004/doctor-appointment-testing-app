const BACKEND_BASE_URL =
  process.env.BACKEND_API_BASE_URL ?? "http://localhost:4001";

function buildBackendUrl(request: Request, pathSegments: string[]) {
  const incomingUrl = new URL(request.url);
  const backendUrl = new URL(
    `/api/${pathSegments.join("/")}`,
    BACKEND_BASE_URL,
  );

  backendUrl.search = incomingUrl.search;
  return backendUrl;
}

function buildHeaders(request: Request) {
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");
  return headers;
}

async function proxyRequest(
  request: Request,
  context: { params: Promise<{ path?: string[] }> },
) {
  const { path = [] } = await context.params;
  const backendUrl = buildBackendUrl(request, path);
  const init: RequestInit = {
    method: request.method,
    headers: buildHeaders(request),
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(request.method)) {
    init.body = await request.text();
  }

  const response = await fetch(backendUrl, init);
  return new Response(response.body, {
    status: response.status,
    headers: response.headers,
  });
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PATCH = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;

export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      Allow: "GET, POST, PATCH, PUT, DELETE, OPTIONS",
    },
  });
}
