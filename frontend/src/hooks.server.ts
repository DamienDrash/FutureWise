import type { Handle } from '@sveltejs/kit'

const PROTECTED = new Set(['/imports', '/scenarios', '/management'])

export const handle: Handle = async ({ event, resolve }) => {
    const path = event.url.pathname
    if (PROTECTED.has(path)) {
        const token = event.cookies.get('access_token')
        if (!token) {
            return new Response(null, { status: 302, headers: { Location: '/login' } })
        }
    }
    return resolve(event)
}
