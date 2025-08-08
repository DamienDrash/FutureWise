<script>
  const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  let health = '...'

  async function loadHealth() {
    try {
      const res = await fetch(`${apiBase}/health/ready`)
      const json = await res.json()
      health = json.status
    } catch (e) {
      health = 'error'
    }
  }

  loadHealth()
</script>

<main>
  <h1>FutureWise</h1>
  <p>Backend Health: {health}</p>
</main>

<style>
  main { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial; padding: 2rem; }
  h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
</style>
