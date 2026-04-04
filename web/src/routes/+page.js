import { base } from '$app/paths'

export const ssr = false

export async function load({ fetch }) {
  try {
    const index = await fetch(`${base}/data/index.json`).then(r => r.json())
    if (!index.dates?.length) return { digests: [] }
    const digests = await Promise.all(
      index.dates.map(d => fetch(`${base}/data/${d}.json`).then(r => r.json()))
    )
    return { digests }
  } catch {
    return { digests: [] }
  }
}
