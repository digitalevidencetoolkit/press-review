<script>
  let { article } = $props()
</script>

<article>
  <div class="source">{article.source}</div>
  <h2>{article.headline_en}</h2>
  <p class="summary">{article.summary_en}</p>
  <div class="sig">{article.significance}</div>
</article>

<style>
  article {
    background: #fff;
    border: 1px solid #d5d5e4;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 0.875rem;
    transition: box-shadow 0.15s;
  }
  article:hover {
    box-shadow: 0 4px 24px rgba(28, 6, 46, 0.07);
  }
  .source {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5b56b9;
    margin-bottom: 0.5rem;
  }
  h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1.3;
    color: #1c1c2e;
    margin-bottom: 0.6rem;
  }
  .summary {
    font-size: 0.88rem;
    color: #4c4c72;
    line-height: 1.7;
    margin-bottom: 0.75rem;
  }
  .sig {
    font-size: 0.8rem;
    font-weight: 500;
    color: #1c1c2e;
    background: #ededf5;
    border-left: 3px solid #5b56b9;
    padding: 0.5rem 0.75rem;
    border-radius: 0 0.375rem 0.375rem 0;
    line-height: 1.5;
  }
</style>
