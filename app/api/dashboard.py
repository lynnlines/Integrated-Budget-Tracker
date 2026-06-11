from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Budget Tracker Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    h1 { margin-bottom: 0.2em; }
    .panel { margin-bottom: 24px; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
    .metric { background: #f8f9fb; border-radius: 12px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .metric-title { font-size: 0.9rem; color: #666; margin-bottom: 8px; }
    .metric-value { font-size: 1.8rem; font-weight: 700; }
    .chart-card { background: #fff; border-radius: 12px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .chart-card h2 { margin-top: 0; }
    .footer { margin-top: 32px; font-size: 0.9rem; color: #555; }
  </style>
</head>
<body>
  <h1>Budget Tracker Dashboard</h1>
  <p id="status">Loading analytics...</p>

  <div class="panel metrics">
    <div class="metric"><div class="metric-title">Income (current month)</div><div class="metric-value" id="income">—</div></div>
    <div class="metric"><div class="metric-title">Spending (current month)</div><div class="metric-value" id="spend">—</div></div>
    <div class="metric"><div class="metric-title">Budget variance</div><div class="metric-value" id="variance">—</div></div>
  </div>

  <div class="panel chart-card">
    <h2>Category Breakdown</h2>
    <canvas id="categoryChart" height="200"></canvas>
  </div>

  <div class="panel chart-card">
    <h2>Monthly Income/Spending History</h2>
    <canvas id="historyChart" height="240"></canvas>
  </div>

  <div class="footer">
    <p>Data is loaded from the backend summary APIs. Update source transactions through `/api/v1/transactions/import` and `/api/v1/sheets/import`.</p>
  </div>

  <script>
    function formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value / 100);
    }

    function getLastMonthRange(months) {
      const now = new Date();
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      const start = new Date(now.getFullYear(), now.getMonth() - (months - 1), 1);
      return [start.toISOString().slice(0, 10), end.toISOString().slice(0, 10)];
    }

    async function loadDashboard() {
      const status = document.getElementById('status');
      try {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const [startDate, endDate] = getLastMonthRange(6);

        const summaryRes = await fetch(`/api/v1/summary/cache/monthly?year=${year}&month=${month}`);
        if (!summaryRes.ok) throw new Error('Unable to load current month summary');
        const summary = await summaryRes.json();

        document.getElementById('income').textContent = formatCurrency(summary.total_income_cents);
        document.getElementById('spend').textContent = formatCurrency(summary.total_spent_cents);
        document.getElementById('variance').textContent = summary.budget_variance_cents != null ? formatCurrency(summary.budget_variance_cents) : 'N/A';

        const labels = [];
        const spent = [];
        const income = [];
        const historyRes = await fetch(`/api/v1/summary/history?start_date=${startDate}&end_date=${endDate}`);
        if (!historyRes.ok) throw new Error('Unable to load history');
        const history = await historyRes.json();

        history.history.forEach(item => {
          labels.push(`${item.year}-${String(item.month).padStart(2,'0')}`);
          spent.push(Math.abs(item.total_spent_cents));
          income.push(item.total_income_cents);
        });

        const categoryLabels = summary.category_breakdown.map(item => item.category_name || 'Uncategorized');
        const categoryValues = summary.category_breakdown.map(item => Math.abs(item.amount_cents));

        new Chart(document.getElementById('historyChart'), {
          type: 'line',
          data: {
            labels,
            datasets: [
              { label: 'Income', data: income, borderColor: '#2d9cdb', backgroundColor: 'rgba(45, 156, 219, 0.2)', fill: true },
              { label: 'Spend', data: spent, borderColor: '#eb5757', backgroundColor: 'rgba(235, 87, 87, 0.2)', fill: true },
            ],
          },
          options: { responsive: true, scales: { y: { ticks: { callback: value => '$' + (value/100) } } } }
        });

        new Chart(document.getElementById('categoryChart'), {
          type: 'doughnut',
          data: {
            labels: categoryLabels,
            datasets: [{ data: categoryValues, backgroundColor: ['#2d9cdb', '#bb6bd9', '#56ccf2', '#f2994a', '#6fcf97', '#eb5757'] }],
          },
          options: { responsive: true }
        });

        status.textContent = `Showing current month and last 6 months of activity.`;
      } catch (error) {
        status.textContent = `Dashboard load failed: ${error.message}`;
      }
    }

    loadDashboard();
  </script>
</body>
</html>"""


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return HTMLResponse(DASHBOARD_HTML)
