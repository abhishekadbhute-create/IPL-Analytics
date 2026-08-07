// ---------------------------------------------------------
// NLP SEARCH LOGIC & AI ROUTER RENDERING ENGINE (WITH PLOTLY GRAPHS)
// ---------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('nlp-search-input');
    const searchBtn = document.getElementById('nlp-search-btn');

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', handleSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });
    }
});

async function handleSearch() {
    const searchInput = document.getElementById('nlp-search-input');
    const query = searchInput ? searchInput.value.trim() : '';
    if (!query) return;

    showLoading();

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'API Error');

        hideLoading();
        scrollToResults();
        renderResult(query, data);

    } catch (error) {
        console.error('NLP Search Error:', error);
        hideLoading();
        scrollToResults();
        renderErrorState(error.message);
    }
}

function showLoading() {
    const loadingBox = document.getElementById('loading-box');
    if (!loadingBox) return;
    loadingBox.classList.remove('hidden');
    
    const loadStepTitle = document.getElementById('load-step-title');
    const loadStepSub = document.getElementById('load-step-sub');
    const loadProgressFill = document.getElementById('load-progress-fill');

    const steps = [
        { t: "Analyzing IPL database...", s: "Filtering ball-by-ball deliveries (2008-present)", f: "30%" },
        { t: "Finding relevant matches...", s: "Matching entity relationships", f: "65%" },
        { t: "Building interactive graphs...", s: "Generating Plotly chart traces & metric grids", f: "100%" }
    ];
    let i = 0;
    if (loadStepTitle) loadStepTitle.innerText = steps[0].t;
    if (loadStepSub) loadStepSub.innerText = steps[0].s;
    if (loadProgressFill) loadProgressFill.style.width = steps[0].f;

    clearInterval(window.loadTimer);
    window.loadTimer = setInterval(() => {
        i++;
        if (i < steps.length) {
            if (loadStepTitle) loadStepTitle.innerText = steps[i].t;
            if (loadStepSub) loadStepSub.innerText = steps[i].s;
            if (loadProgressFill) loadProgressFill.style.width = steps[i].f;
        } else {
            clearInterval(window.loadTimer);
        }
    }, 300);
}

function hideLoading() {
    clearInterval(window.loadTimer);
    const loadingBox = document.getElementById('loading-box');
    if (loadingBox) loadingBox.classList.add('hidden');
}

function scrollToResults() {
    const resultsAnchor = document.getElementById('results-anchor');
    if (resultsAnchor) {
        resultsAnchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function renderResult(query, result) {
    const viewContainer = document.getElementById('view-container');
    if (!viewContainer) return;

    const { view_type, title, data } = result;
    if (!data) {
        viewContainer.innerHTML = `<div style="background: var(--bg-card); padding: 24px; border-radius: 12px;">No records found.</div>`;
        return;
    }

    const uniqueId = 'chart_' + Math.random().toString(36).substr(2, 9);

    let html = `
        <div style="margin-bottom: 24px;">
            <span class="sub-tag">— AI IPL ANALYTICS INSIGHT —</span>
            <h2 style="font-size: 28px; margin-top: 4px;">${title || 'Analytics Insight'}</h2>
            <p style="color: var(--text-muted); font-size: 14px;">Results for: "<em>${query}</em>"</p>
        </div>

        <div class="view-tabs-bar">
            <button class="view-tab-btn active" onclick="switchViewTab('${uniqueId}', 'chart')">📊 Interactive Chart</button>
            <button class="view-tab-btn" onclick="switchViewTab('${uniqueId}', 'table')">📋 Data Table</button>
            <button class="view-tab-btn" onclick="switchViewTab('${uniqueId}', 'cards')">⚡ Summary Cards</button>
        </div>

        <div id="${uniqueId}_chart_sec" class="chart-card-box">
            <div id="${uniqueId}_plotly" class="chart-container"></div>
        </div>

        <div id="${uniqueId}_table_sec" style="display: none;">
            ${Array.isArray(data) ? renderTable(data) : renderDictTable(data)}
        </div>

        <div id="${uniqueId}_cards_sec" style="display: none;">
            ${Array.isArray(data) ? renderArrayCards(data) : renderDict(data)}
        </div>
    `;

    viewContainer.innerHTML = html;

    // Render Plotly Chart
    setTimeout(() => {
        renderPlotlyChart(`${uniqueId}_plotly`, title || query, data);
    }, 100);
}

window.switchViewTab = function(uniqueId, mode) {
    const chartSec = document.getElementById(`${uniqueId}_chart_sec`);
    const tableSec = document.getElementById(`${uniqueId}_table_sec`);
    const cardsSec = document.getElementById(`${uniqueId}_cards_sec`);

    if (chartSec) chartSec.style.display = (mode === 'chart') ? 'block' : 'none';
    if (tableSec) tableSec.style.display = (mode === 'table') ? 'block' : 'none';
    if (cardsSec) cardsSec.style.display = (mode === 'cards') ? 'block' : 'none';

    const btns = event.target.parentElement.querySelectorAll('.view-tab-btn');
    btns.forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    if (mode === 'chart') {
        const plotlyEl = document.getElementById(`${uniqueId}_plotly`);
        if (plotlyEl && window.Plotly) {
            Plotly.Plots.resize(plotlyEl);
        }
    }
};

function renderPlotlyChart(containerId, title, data) {
    const container = document.getElementById(containerId);
    if (!container || !window.Plotly) return;

    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDarkMode ? '#ffffff' : '#111111';
    const gridColor = isDarkMode ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';

    let traces = [];
    let layout = {
        title: { text: title, font: { family: 'Space Grotesk', size: 18, color: textColor } },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Inter', color: textColor },
        margin: { t: 50, r: 30, l: 50, b: 60 },
        autosize: true,
        xaxis: { gridcolor: gridColor, color: textColor },
        yaxis: { gridcolor: gridColor, color: textColor }
    };

    if (Array.isArray(data) && data.length > 0) {
        const keys = Object.keys(data[0]);
        let catKey = keys.find(k => typeof data[0][k] === 'string') || keys[0];
        let numKey = keys.find(k => typeof data[0][k] === 'number') || keys[1] || keys[0];

        const xVals = data.map(d => d[catKey]);
        const yVals = data.map(d => d[numKey]);

        if (catKey.toLowerCase().includes('season') || catKey.toLowerCase().includes('year')) {
            traces.push({
                x: xVals,
                y: yVals,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#ff5a1f', width: 3, shape: 'spline' },
                marker: { size: 8, color: '#ff5a1f', symbol: 'circle' },
                name: numKey.replace(/_/g, ' ').toUpperCase()
            });
        } else {
            traces.push({
                x: xVals,
                y: yVals,
                type: 'bar',
                marker: {
                    color: xVals.map((_, idx) => {
                        const colors = ['#ff5a1f', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];
                        return colors[idx % colors.length];
                    }),
                    line: { width: 0 }
                },
                name: numKey.replace(/_/g, ' ').toUpperCase()
            });
        }
    } else if (typeof data === 'object' && data !== null) {
        const numericEntries = Object.entries(data).filter(([k, v]) => typeof v === 'number');
        if (numericEntries.length > 0) {
            traces.push({
                x: numericEntries.map(([k]) => k.replace(/_/g, ' ').toUpperCase()),
                y: numericEntries.map(([, v]) => v),
                type: 'bar',
                marker: {
                    color: '#ff5a1f',
                    line: { width: 0 }
                }
            });
        } else {
            // Render text summary chart if no numeric entries
            container.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 40px;">
                    <div style="font-size: 48px; color: var(--primary-orange); margin-bottom: 12px;">📊</div>
                    <h3 style="font-family: var(--font-heading); font-size: 22px;">Executive Overview</h3>
                    <p style="color: var(--text-muted); max-width: 500px; margin-top: 8px;">Explore detailed breakdown metrics in the <strong>Summary Cards</strong> and <strong>Data Table</strong> tabs above.</p>
                </div>
            `;
            return;
        }
    }

    Plotly.newPlot(containerId, traces, layout, { responsive: true, displayModeBar: false });
}

function renderTable(dataArr) {
    if (dataArr.length === 0) return '<p>No data</p>';
    const headers = Object.keys(dataArr[0]);

    let ths = headers.map(h => `<th>${h.replace(/_/g, ' ').toUpperCase()}</th>`).join('');
    let trs = dataArr.map(row => {
        let tds = headers.map(h => `<td>${row[h]}</td>`).join('');
        return `<tr>${tds}</tr>`;
    }).join('');

    return `
        <div class="table-card-box">
            <table class="eyantra-data-table">
                <thead><tr>${ths}</tr></thead>
                <tbody>${trs}</tbody>
            </table>
        </div>
    `;
}

function renderDictTable(dictData) {
    const entries = Object.entries(dictData).filter(([k, v]) => typeof v !== 'object' || v === null);
    if (entries.length === 0) return renderDict(dictData);

    let trs = entries.map(([k, v]) => `
        <tr>
            <td style="font-weight: 600; text-transform: uppercase; font-family: var(--font-mono); font-size: 12px;">${k.replace(/_/g, ' ')}</td>
            <td style="font-weight: 700; color: var(--primary-orange);">${v}</td>
        </tr>
    `).join('');

    return `
        <div class="table-card-box">
            <table class="eyantra-data-table">
                <thead><tr><th>METRIC PARAMETER</th><th>ANALYSIS VALUE</th></tr></thead>
                <tbody>${trs}</tbody>
            </table>
        </div>
    `;
}

function renderArrayCards(dataArr) {
    let html = `<div class="results-grid">`;
    dataArr.forEach((item, idx) => {
        html += `
            <div class="stat-card-box">
                <span class="cool-badge">RANK #${idx + 1}</span>
                <div style="margin-top: 8px;">
                    ${Object.entries(item).map(([k, v]) => `
                        <div style="margin-bottom: 6px;">
                            <span class="stat-card-title">${k.replace(/_/g, ' ')}:</span>
                            <span style="font-weight: 700; font-size: 16px;">${v}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    html += `</div>`;
    return html;
}

function renderDict(dictData) {
    let html = `<div class="results-grid">`;
    const scalars = Object.entries(dictData).filter(([k, v]) => typeof v !== 'object' || v === null);
    scalars.forEach(([k, v]) => {
        html += `
            <div class="stat-card-box">
                <div class="stat-card-title">${k.replace(/_/g, ' ')}</div>
                <div class="stat-card-val">${v}</div>
                <span class="cool-badge">VERIFIED STAT</span>
            </div>
        `;
    });

    const complexes = Object.entries(dictData).filter(([k, v]) => typeof v === 'object' && v !== null);
    complexes.forEach(([k, v]) => {
        html += `<div style="grid-column: span 12; margin-top: 16px;">
            <h4 style="text-transform: capitalize; margin-bottom: 8px; font-family: var(--font-heading);">${k.replace(/_/g, ' ')}</h4>
            ${Array.isArray(v) ? renderTable(v) : renderDict(v)}
        </div>`;
    });

    html += `</div>`;
    return html;
}

function renderErrorState(errorMsg) {
    const viewContainer = document.getElementById('view-container');
    if (viewContainer) {
        viewContainer.innerHTML = `
            <div style="background: var(--bg-card); border: 2px solid #ef4444; border-radius: 12px; padding: 32px; text-align: center;">
                <h3 style="color: #ef4444;">API Execution Error</h3>
                <p style="color: var(--text-muted); margin-top: 8px;">${errorMsg}</p>
            </div>
        `;
    }
}
