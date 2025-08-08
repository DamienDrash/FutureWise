import type { Handle } from '@sveltejs/kit'

const PROTECTED_PREFIXES = ['/imports', '/scenarios', '/management']

function decodeJwtPayload(token: string): any | null {
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    // base64url decode
    const b64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const json = Buffer.from(b64, 'base64').toString('utf-8')
    return JSON.parse(json)
  } catch {
    return null
  }
}

export const handle: Handle = async ({ event, resolve }) => {
  const path = event.url.pathname
  const token = event.cookies.get('access_token') || ''
  const payload = token ? decodeJwtPayload(token) : null
  if (payload) {
    event.locals.user = {
      user_id: String(payload.sub || ''),
      tenant_id: String(payload.tenant_id || ''),
      role: String(payload.role || 'viewer')
    }
  } else {
    event.locals.user = null
  }

  if (PROTECTED_PREFIXES.some((p) => path === p || path.startsWith(p + '/'))) {
    if (!token) {
      return new Response(null, { status: 302, headers: { Location: '/login' } })
    }
  }

  return resolve(event)
}
