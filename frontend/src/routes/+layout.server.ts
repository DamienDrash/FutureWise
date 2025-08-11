import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ locals }) => {
  // expose minimal user context to the layout for conditional UI
  const user = (locals as any).user || null
  return {
    user
  }
}


