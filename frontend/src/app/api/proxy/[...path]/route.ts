/**
 * Next.js API Proxy Route
 *
 * This proxy route forwards all requests from the frontend to the backend API.
 *
 * Why this exists:
 * - Playwright MCP browser runs in isolated environment
 * - Browser's localhost cannot reach host's localhost:8004
 * - This proxy allows browser to call same-origin API routes
 * - Proxy runs on Next.js server which CAN reach localhost:8004
 *
 * Route: /api/proxy/[...path] -> http://localhost:8004/api/v1/[...path]
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8004/api/v1';

// Helper to forward headers from incoming request to backend
function getForwardHeaders(request: NextRequest): HeadersInit {
  const headers: HeadersInit = {};

  // Forward important headers
  const headersToForward = [
    'authorization',
    'content-type',
    'cookie',
    'x-csrf-token',
    'accept',
    'accept-language',
    'user-agent',
  ];

  headersToForward.forEach(header => {
    const value = request.headers.get(header);
    if (value) {
      headers[header] = value;
    }
  });

  return headers;
}

// Helper to build backend URL from path segments
function buildBackendUrl(pathSegments: string[], searchParams: URLSearchParams): string {
  const path = pathSegments.join('/');
  const query = searchParams.toString();
  const url = `${BACKEND_URL}/${path}`;
  return query ? `${url}?${query}` : url;
}

// GET handler
export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const backendUrl = buildBackendUrl(params.path, searchParams);

    console.log(`[PROXY GET] ${request.url} -> ${backendUrl}`);

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: getForwardHeaders(request),
    });

    // Get response body
    const data = await response.text();

    // Forward response with headers
    return new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json',
        // Forward CORS headers if present
        ...(response.headers.get('access-control-allow-origin') && {
          'access-control-allow-origin': response.headers.get('access-control-allow-origin')!,
        }),
        ...(response.headers.get('access-control-allow-credentials') && {
          'access-control-allow-credentials': response.headers.get('access-control-allow-credentials')!,
        }),
      },
    });
  } catch (error) {
    console.error('[PROXY GET ERROR]', error);
    return NextResponse.json(
      { error: 'Proxy request failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 502 }
    );
  }
}

// POST handler
export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const backendUrl = buildBackendUrl(params.path, searchParams);

    // Get request body
    const body = await request.text();

    console.log(`[PROXY POST] ${request.url} -> ${backendUrl}`);

    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: getForwardHeaders(request),
      body: body || undefined,
    });

    // Get response body
    const data = await response.text();

    // Forward response with headers
    return new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json',
        ...(response.headers.get('set-cookie') && {
          'set-cookie': response.headers.get('set-cookie')!,
        }),
      },
    });
  } catch (error) {
    console.error('[PROXY POST ERROR]', error);
    return NextResponse.json(
      { error: 'Proxy request failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 502 }
    );
  }
}

// PUT handler
export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const backendUrl = buildBackendUrl(params.path, searchParams);

    const body = await request.text();

    console.log(`[PROXY PUT] ${request.url} -> ${backendUrl}`);

    const response = await fetch(backendUrl, {
      method: 'PUT',
      headers: getForwardHeaders(request),
      body: body || undefined,
    });

    const data = await response.text();

    return new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('[PROXY PUT ERROR]', error);
    return NextResponse.json(
      { error: 'Proxy request failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 502 }
    );
  }
}

// PATCH handler
export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const backendUrl = buildBackendUrl(params.path, searchParams);

    const body = await request.text();

    console.log(`[PROXY PATCH] ${request.url} -> ${backendUrl}`);

    const response = await fetch(backendUrl, {
      method: 'PATCH',
      headers: getForwardHeaders(request),
      body: body || undefined,
    });

    const data = await response.text();

    return new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('[PROXY PATCH ERROR]', error);
    return NextResponse.json(
      { error: 'Proxy request failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 502 }
    );
  }
}

// DELETE handler
export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const backendUrl = buildBackendUrl(params.path, searchParams);

    console.log(`[PROXY DELETE] ${request.url} -> ${backendUrl}`);

    const response = await fetch(backendUrl, {
      method: 'DELETE',
      headers: getForwardHeaders(request),
    });

    const data = await response.text();

    return new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'content-type': response.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('[PROXY DELETE ERROR]', error);
    return NextResponse.json(
      { error: 'Proxy request failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 502 }
    );
  }
}

// OPTIONS handler (for CORS preflight)
export async function OPTIONS(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-CSRF-Token, Cookie',
      'Access-Control-Max-Age': '86400',
    },
  });
}
