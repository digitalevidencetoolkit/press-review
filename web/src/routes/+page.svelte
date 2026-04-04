<script>
  import ArticleCard from '$lib/ArticleCard.svelte'

  let { data } = $props()

  let digests = $derived(data.digests ?? [])
  let allArticles = $derived(
    digests.flatMap(d => d.articles.map(a => ({ ...a, _date: d.date })))
  )
  let allCitations = $derived(
    [...new Set(digests.flatMap(d => d.citations ?? []))]
  )
</script>

<svelte:head>
  <title>European Press Review</title>
  <meta name="description" content="A daily digest of European news on digital speech, content deletion, and online censorship." />
</svelte:head>

<nav>
  <span class="wordmark">European Press Review</span>
  {#if allArticles.length}
    <span class="nav-count">{allArticles.length} articles</span>
  {/if}
</nav>

{#if !allArticles.length}
  <div class="empty">
    <p>No press review available yet.</p>
  </div>
{:else}
  <header class="hero">
    <h1>European Press Review</h1>
    <p class="topic">Digital speech, content deletion &amp; online censorship</p>
  </header>

  <main>
    <div class="container">
      {#each allArticles as article (article.headline_en)}
        <ArticleCard {article} date={article._date} />
      {/each}
    </div>
  </main>

  {#if allCitations.length}
    <section class="citations">
      <div class="container">
        <p class="eyebrow">Sources</p>
        <ul>
          {#each allCitations as url}
            <li><a href={url} target="_blank" rel="noopener noreferrer">{url}</a></li>
          {/each}
        </ul>
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
  .nav-count {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #5b56b9;
    background: rgba(91, 86, 185, 0.15);
    border: 1px solid rgba(91, 86, 185, 0.3);
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
  }

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

  .eyebrow {
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4c4c72;
    margin-bottom: 0.875rem;
  }

  main {
    padding: 2.5rem 1.5rem;
  }

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

  .empty {
    text-align: center;
    padding: 8rem 2rem;
    color: #4c4c72;
    font-size: 0.9rem;
  }

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
