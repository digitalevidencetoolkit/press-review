<script>
  import { base } from '$app/paths'
  import ArticleCard from '$lib/ArticleCard.svelte'

  let { data } = $props()

  let digest = $state(data.digest ?? null)
  let dates = $state(data.dates ?? [])
  let loading = $state(false)

  $effect(() => {
    digest = data.digest ?? null
    dates = data.dates ?? []
  })

  let activeDate = $derived(digest?.date ?? '')

  async function loadDate(d) {
    if (d === activeDate || loading) return
    loading = true
    try {
      digest = await fetch(`${base}/data/${d}.json`).then(r => r.json())
    } finally {
      loading = false
    }
  }
</script>

<svelte:head>
  <title>European Press Review{digest ? ` — ${digest.date}` : ''}</title>
  <meta name="description" content="A daily digest of European news on digital speech, content deletion, and online censorship." />
</svelte:head>

<nav>
  <span class="wordmark">European Press Review</span>
  {#if digest}
    <span class="nav-date">{digest.date}</span>
  {/if}
</nav>

{#if !digest}
  <div class="empty">
    <p>No press review available yet.</p>
  </div>
{:else}
  <header class="hero">
    <span class="label">{digest.date}</span>
    <h1>European Press Review</h1>
    <p class="topic">{digest.topic}</p>
  </header>

  <section class="overview">
    <div class="container">
      <p class="eyebrow">Editorial Overview</p>
      <p class="overview-text">{digest.editorial_overview}</p>
    </div>
  </section>

  <main class:loading>
    <div class="container">
      <p class="eyebrow">{digest.articles.length} article{digest.articles.length === 1 ? '' : 's'}</p>
      {#each digest.articles as article (article.headline_en)}
        <ArticleCard {article} />
      {/each}
    </div>
  </main>

  {#if digest.citations?.length}
    <section class="citations">
      <div class="container">
        <p class="eyebrow">Sources</p>
        <ul>
          {#each digest.citations as url}
            <li><a href={url} target="_blank" rel="noopener noreferrer">{url}</a></li>
          {/each}
        </ul>
      </div>
    </section>
  {/if}

  {#if dates.length > 1}
    <section class="archive">
      <div class="container">
        <p class="eyebrow">Archive</p>
        <div class="pills">
          {#each dates as d}
            <button
              class="pill"
              class:active={d === activeDate}
              onclick={() => loadDate(d)}
            >
              {d}
            </button>
          {/each}
        </div>
      </div>
    </section>
  {/if}
{/if}

<footer>
  European Press Review &middot; Powered by Perplexity Sonar Pro
</footer>

<style>
  :global(*, *::before, *::after) { box-sizing: border-box; margin: 0; padding: 0; }
  :global(body) {
    font-family: 'Inter', sans-serif;
    background: #f2f1f9;
    color: #1c1c2e;
    line-height: 1.6;
  }

  .container {
    max-width: 760px;
    margin: 0 auto;
    padding: 0 1.5rem;
  }

  /* Nav */
  nav {
    background: #1c062e;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
  }
  .wordmark {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #ededf5;
  }
  .nav-date {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #5b56b9;
    background: rgba(91, 86, 185, 0.15);
    border: 1px solid rgba(91, 86, 185, 0.3);
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
  }

  /* Hero */
  .hero {
    background: #1c062e;
    padding: 4rem 1.5rem 3.5rem;
    text-align: center;
    color: #fff;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
  }
  .label {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #5b56b9;
    background: rgba(91, 86, 185, 0.15);
    border: 1px solid rgba(91, 86, 185, 0.3);
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    margin-bottom: 1.25rem;
  }
  h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 5vw, 3.25rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0.75rem;
  }
  .topic {
    font-size: 0.9rem;
    color: #8b8ba9;
    max-width: 520px;
  }

  /* Eyebrow label */
  .eyebrow {
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4c4c72;
    margin-bottom: 0.875rem;
  }

  /* Overview */
  .overview {
    background: #f0f2dc;
    border-bottom: 1px solid #e0e4ba;
    padding: 2.5rem 1.5rem;
  }
  .overview-text {
    font-size: 1rem;
    line-height: 1.8;
    color: #1c1c2e;
  }

  /* Articles */
  main {
    padding: 2.5rem 1.5rem;
    transition: opacity 0.15s;
  }
  main.loading { opacity: 0.45; pointer-events: none; }

  /* Citations */
  .citations {
    padding: 0 1.5rem 2.5rem;
  }
  .citations ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }
  .citations a {
    font-size: 0.76rem;
    color: #5b56b9;
    text-decoration: none;
    word-break: break-all;
  }
  .citations a:hover { text-decoration: underline; }

  /* Archive */
  .archive {
    background: #fff;
    border-top: 1px solid #d5d5e4;
    padding: 2rem 1.5rem;
  }
  .pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .pill {
    font-family: 'Inter', sans-serif;
    font-size: 0.73rem;
    font-weight: 500;
    border: 1px solid #d5d5e4;
    border-radius: 999px;
    padding: 0.3rem 0.85rem;
    background: transparent;
    color: #4c4c72;
    cursor: pointer;
    transition: all 0.15s;
  }
  .pill:hover { border-color: #5b56b9; color: #5b56b9; }
  .pill.active { background: #5b56b9; border-color: #5b56b9; color: #fff; }

  /* Empty */
  .empty {
    text-align: center;
    padding: 8rem 2rem;
    color: #4c4c72;
    font-size: 0.9rem;
  }

  /* Footer */
  footer {
    background: #1c062e;
    text-align: center;
    padding: 1.5rem;
    font-size: 0.7rem;
    letter-spacing: 0.04em;
    color: #3b3b5a;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
  }
</style>
