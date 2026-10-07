const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2
});

const initialStocks = [
  { symbol: 'NVDA', name: 'NVIDIA', price: 136.22, change: 2.18, history: [112, 118, 120, 124, 128, 131, 136.22] },
  { symbol: 'MSFT', name: 'Microsoft', price: 428.85, change: 0.93, history: [405, 411, 414, 417, 421, 425, 428.85] },
  { symbol: 'AMD', name: 'Advanced Micro Devices', price: 171.48, change: 1.76, history: [155, 158, 163, 166, 168, 170, 171.48] },
  { symbol: 'PLTR', name: 'Palantir', price: 31.94, change: 2.52, history: [27.2, 28.1, 28.8, 29.5, 30.3, 31.1, 31.94] },
  { symbol: 'META', name: 'Meta Platforms', price: 528.76, change: 1.14, history: [500, 504, 510, 515, 520, 524, 528.76] },
  { symbol: 'GOOGL', name: 'Alphabet', price: 176.41, change: -0.34, history: [182, 181, 180, 179, 178, 177, 176.41] },
  { symbol: 'CRM', name: 'Salesforce', price: 282.50, change: 0.81, history: [270, 272, 275, 279, 280, 281, 282.5] },
  { symbol: 'IBM', name: 'IBM', price: 182.40, change: 0.66, history: [175, 176, 178, 179, 180, 181, 182.4] },
  { symbol: 'AAPL', name: 'Apple', price: 214.36, change: 1.42, history: [198, 201, 205, 207, 210, 212, 214.36] },
  { symbol: 'AMZN', name: 'Amazon', price: 187.55, change: 1.08, history: [175, 178, 181, 183, 185, 186, 187.55] }
];

const state = {
  cash: 22000,
  holdings: [
    { symbol: 'NVDA', shares: 24, avgCost: 128.2 },
    { symbol: 'MSFT', shares: 18, avgCost: 401.1 },
    { symbol: 'AMD', shares: 22, avgCost: 152.9 },
    { symbol: 'PLTR', shares: 40, avgCost: 28.7 }
  ],
  marketRunning: false,
  selectedSymbol: 'NVDA',
  activity: [
    { action: 'Bought 24 NVDA', type: 'buy', time: new Date().toISOString() },
    { action: 'Bought 18 MSFT', type: 'buy', time: new Date(Date.now() - 3600000).toISOString() },
    { action: 'Bought 22 AMD', type: 'buy', time: new Date(Date.now() - 7200000).toISOString() }
  ],
  stocks: structuredClone(initialStocks)
};

const elements = {
  portfolioValue: document.getElementById('portfolio-value'),
  portfolioChange: document.getElementById('portfolio-change'),
  cashValue: document.getElementById('cash-value'),
  investedValue: document.getElementById('invested-value'),
  positionsCount: document.getElementById('positions-count'),
  buyingPower: document.getElementById('buying-power'),
  chartTitle: document.getElementById('chart-title'),
  chartPrice: document.getElementById('chart-price'),
  watchlist: document.getElementById('watchlist'),
  holdingsTable: document.getElementById('holdings-table'),
  symbolSelect: document.getElementById('symbol-select'),
  sideSelect: document.getElementById('side-select'),
  sharesInput: document.getElementById('shares-input'),
  orderTotal: document.getElementById('order-total'),
  estimatedAvailable: document.getElementById('estimated-available'),
  orderForm: document.getElementById('order-form'),
  moversList: document.getElementById('movers-list'),
  activityLog: document.getElementById('activity-log'),
  priceChart: document.getElementById('price-chart'),
  marketToggle: document.getElementById('market-toggle'),
  resetBtn: document.getElementById('reset-btn')
};

function formatCurrency(value) {
  return currency.format(value);
}

function getStockBySymbol(symbol) {
  return state.stocks.find((stock) => stock.symbol === symbol);
}

function getHoldingBySymbol(symbol) {
  return state.holdings.find((holding) => holding.symbol === symbol);
}

function calculatePortfolioBalance() {
  const invested = state.holdings.reduce((total, holding) => {
    const stock = getStockBySymbol(holding.symbol);
    return total + (stock ? stock.price * holding.shares : 0);
  }, 0);

  const total = state.cash + invested;
  const priorValue = state.holdings.reduce((totalValue, holding) => {
    const stock = getStockBySymbol(holding.symbol);
    return totalValue + (stock ? (stock.price - stock.change * 0.7) * holding.shares : 0);
  }, state.cash);

  return { invested, total, change: total - priorValue };
}

function renderSummary() {
  const { invested, total, change } = calculatePortfolioBalance();
  const currentStock = getStockBySymbol(state.selectedSymbol) || state.stocks[0];

  elements.portfolioValue.textContent = formatCurrency(total);
  elements.cashValue.textContent = formatCurrency(state.cash);
  elements.investedValue.textContent = formatCurrency(invested);
  elements.positionsCount.textContent = `${state.holdings.length} positions`;
  elements.buyingPower.textContent = formatCurrency(state.cash);

  const positive = change >= 0;
  elements.portfolioChange.textContent = `${positive ? '+' : '-'}${formatCurrency(Math.abs(change))} today`;
  elements.portfolioChange.className = positive ? 'gain' : 'loss';

  elements.chartTitle.textContent = currentStock.symbol;
  elements.chartPrice.textContent = formatCurrency(currentStock.price);
  elements.chartPrice.className = currentStock.change >= 0 ? 'price-pill gain' : 'price-pill loss';

  const orderTotal = Number(elements.sharesInput.value || 0) * currentStock.price;
  elements.orderTotal.textContent = formatCurrency(orderTotal);
  elements.estimatedAvailable.textContent = formatCurrency(state.cash);
}

function renderWatchlist() {
  elements.watchlist.innerHTML = state.stocks
    .slice()
    .sort((a, b) => Math.abs(b.change) - Math.abs(a.change))
    .map((stock) => {
      const active = stock.symbol === state.selectedSymbol ? 'active' : '';
      const isPositive = stock.change >= 0;
      return `
        <li class="watch-item ${active}" data-symbol="${stock.symbol}">
          <div class="watch-meta">
            <div class="symbol-row">
              <strong>${stock.symbol}</strong>
              <span class="subtle">${stock.name}</span>
            </div>
            <span class="subtle">${formatCurrency(stock.price)}</span>
          </div>
          <span class="${isPositive ? 'change-positive' : 'change-negative'}">
            ${isPositive ? '+' : ''}${stock.change.toFixed(2)}%
          </span>
        </li>
      `;
    })
    .join('');

  elements.watchlist.querySelectorAll('.watch-item').forEach((item) => {
    item.addEventListener('click', () => {
      state.selectedSymbol = item.dataset.symbol;
      renderAll();
    });
  });
}

function renderHoldings() {
  if (!state.holdings.length) {
    elements.holdingsTable.innerHTML = `
      <tr>
        <td colspan="5" class="subtle">No positions yet. Buy your first AI stock.</td>
      </tr>
    `;
    return;
  }

  elements.holdingsTable.innerHTML = state.holdings
    .map((holding) => {
      const stock = getStockBySymbol(holding.symbol);
      const currentValue = stock ? stock.price * holding.shares : 0;
      const pnl = stock ? (stock.price - holding.avgCost) * holding.shares : 0;
      return `
        <tr>
          <td>${holding.symbol}</td>
          <td>${holding.shares}</td>
          <td>${stock ? formatCurrency(stock.price) : '$0.00'}</td>
          <td>${formatCurrency(currentValue)}</td>
          <td class="${pnl >= 0 ? 'gain' : 'loss'}">${pnl >= 0 ? '+' : '-'}${formatCurrency(Math.abs(pnl))}</td>
        </tr>
      `;
    })
    .join('');
}

function renderMovers() {
  const movers = state.stocks
    .slice()
    .sort((a, b) => Math.abs(b.change) - Math.abs(a.change))
    .slice(0, 5);

  elements.moversList.innerHTML = movers
    .map((stock) => `
      <li class="mover-item">
        <div class="mover-meta">
          <strong>${stock.symbol}</strong>
          <span class="subtle">${stock.name}</span>
        </div>
        <span class="${stock.change >= 0 ? 'change-positive' : 'change-negative'}">
          ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}%
        </span>
      </li>
    `)
    .join('');
}

function renderActivity() {
  elements.activityLog.innerHTML = state.activity
    .slice(0, 6)
    .map((entry) => `
      <li class="activity-item">
        <strong>${entry.action}</strong>
        <time>${new Date(entry.time).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</time>
      </li>
    `)
    .join('');
}

function buildChartPath(values) {
  const width = 560;
  const height = 250;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;

  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * (height - 20) - 10;
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');
}

function renderChart() {
  const stock = getStockBySymbol(state.selectedSymbol) || state.stocks[0];
  const pathData = buildChartPath(stock.history);
  const lastPoint = stock.history[stock.history.length - 1];
  const firstPoint = stock.history[0];
  const slope = lastPoint - firstPoint;

  elements.priceChart.innerHTML = `
    <defs>
      <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%" stop-color="rgba(96, 165, 250, 0.5)" />
        <stop offset="100%" stop-color="rgba(96, 165, 250, 0.02)" />
      </linearGradient>
    </defs>
    <path d="${pathData} L 560 250 L 0 250 Z" fill="url(#chartFill)" opacity="0.9"></path>
    <path d="${pathData}" fill="none" stroke="${slope >= 0 ? '#60a5fa' : '#f87171'}" stroke-width="3" stroke-linecap="round"></path>
  `;
}

function populateSymbolOptions() {
  elements.symbolSelect.innerHTML = state.stocks
    .map((stock) => `<option value="${stock.symbol}">${stock.symbol}</option>`)
    .join('');

  elements.symbolSelect.value = state.selectedSymbol;
}

function updateOrderEstimate() {
  const stock = getStockBySymbol(elements.symbolSelect.value);
  const shares = Number(elements.sharesInput.value || 0);
  const orderValue = stock ? stock.price * shares : 0;
  elements.orderTotal.textContent = formatCurrency(orderValue);
  elements.estimatedAvailable.textContent = formatCurrency(state.cash);
}

function handleTrade(event) {
  event.preventDefault();

  const symbol = elements.symbolSelect.value;
  const side = elements.sideSelect.value;
  const shares = Number(elements.sharesInput.value);
  const stock = getStockBySymbol(symbol);

  if (!stock || shares <= 0) {
    return;
  }

  const tradeValue = stock.price * shares;
  const existingHolding = getHoldingBySymbol(symbol);

  if (side === 'buy') {
    if (state.cash < tradeValue) {
      alert('Not enough cash to place this trade.');
      return;
    }

    state.cash -= tradeValue;
    if (existingHolding) {
      const totalShares = existingHolding.shares + shares;
      const totalCost = existingHolding.avgCost * existingHolding.shares + tradeValue;
      existingHolding.avgCost = totalCost / totalShares;
      existingHolding.shares = totalShares;
    } else {
      state.holdings.push({ symbol, shares, avgCost: stock.price });
    }

    state.activity.unshift({ action: `Bought ${shares} ${symbol}`, type: 'buy', time: new Date().toISOString() });
  } else {
    if (!existingHolding || existingHolding.shares < shares) {
      alert('You do not own enough shares to sell.');
      return;
    }

    state.cash += tradeValue;
    existingHolding.shares -= shares;

    if (existingHolding.shares === 0) {
      state.holdings = state.holdings.filter((holding) => holding.symbol !== symbol);
    }

    state.activity.unshift({ action: `Sold ${shares} ${symbol}`, type: 'sell', time: new Date().toISOString() });
  }

  renderAll();
}

function tickMarket() {
  state.stocks = state.stocks.map((stock) => {
    const drift = (Math.random() - 0.48) * 2.6;
    const nextPrice = Math.max(15, stock.price * (1 + drift / 100));
    const nextChange = Number(((nextPrice - stock.history[0]) / stock.history[0] * 100).toFixed(2));
    const history = [...stock.history, Number(nextPrice.toFixed(2))].slice(-14);

    return {
      ...stock,
      price: Number(nextPrice.toFixed(2)),
      change: nextChange,
      history
    };
  });

  renderAll();
}

function renderAll() {
  renderSummary();
  renderWatchlist();
  renderHoldings();
  renderMovers();
  renderActivity();
  renderChart();
  populateSymbolOptions();
  updateOrderEstimate();
}

function resetPortfolio() {
  state.cash = 22000;
  state.holdings = [
    { symbol: 'NVDA', shares: 24, avgCost: 128.2 },
    { symbol: 'MSFT', shares: 18, avgCost: 401.1 },
    { symbol: 'AMD', shares: 22, avgCost: 152.9 },
    { symbol: 'PLTR', shares: 40, avgCost: 28.7 }
  ];
  state.activity = [
    { action: 'Bought 24 NVDA', type: 'buy', time: new Date().toISOString() },
    { action: 'Bought 18 MSFT', type: 'buy', time: new Date(Date.now() - 3600000).toISOString() },
    { action: 'Bought 22 AMD', type: 'buy', time: new Date(Date.now() - 7200000).toISOString() }
  ];
  state.stocks = structuredClone(initialStocks);
  state.selectedSymbol = 'NVDA';
  elements.symbolSelect.value = 'NVDA';
  renderAll();
}

function toggleMarket() {
  state.marketRunning = !state.marketRunning;
  elements.marketToggle.textContent = state.marketRunning ? 'Pause market' : 'Start market';

  if (state.marketRunning) {
    window.marketTimer = setInterval(tickMarket, 2000);
  } else {
    clearInterval(window.marketTimer);
  }
}

elements.orderForm.addEventListener('submit', handleTrade);
elements.symbolSelect.addEventListener('change', () => {
  state.selectedSymbol = elements.symbolSelect.value;
  renderAll();
});
elements.sharesInput.addEventListener('input', updateOrderEstimate);
elements.marketToggle.addEventListener('click', toggleMarket);
elements.resetBtn.addEventListener('click', resetPortfolio);

renderAll();

window.addEventListener('beforeunload', () => {
  clearInterval(window.marketTimer);
});
