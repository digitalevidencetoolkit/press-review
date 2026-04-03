import { base } from '$app/paths'

export const ssr = false

export async function load({ fetch }) {
  try {
    const index = await fetch(`${base}/data/index.json`).then(r => r.json())
    if (!index.dates?.length) return { digest: null, dates: [] }
    const digest = await fetch(`${base}/data/${index.dates[0]}.json`).then(r => r.json())
    return { digest, dates: index.dates }
  } catch {
    return { digest: null, dates: [] }
  }
}
