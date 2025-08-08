import { goto } from '$app/navigation'

const PROTECTED = new Set(['/imports', '/scenarios', '/management'])

export function handleError({ error }) {
  console.error(error)
}

export function start() {
  // simple client guard
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('fw_token') : null
  const path = typeof location !== 'undefined' ? location.pathname : ''
  if (PROTECTED.has(path) && !token) {
    goto('/login')
  }
}
