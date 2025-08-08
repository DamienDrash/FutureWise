import type { Handle } from '@sveltejs/kit'

const PROTECTED_PREFIXES = ['/imports', '/scenarios', '/management']

export const handle: Handle = async ({ event, resolve }) => {
    const path = event.url.pathname
    if (PROTECTED_PREFIXES.some((p) => path === p || path.startsWith(p + '/'))) {
        const token = event.cookies.get('access_token')
        if (!token) {
            return new Response(null, { status: 302, headers: { Location: '/login' } })
        }
    }
    return resolve(event)
}
