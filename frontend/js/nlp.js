// ---------------------------------------------------------
// NLP SEARCH LOGIC & AI ROUTER RENDERING ENGINE
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
        { t: "Building visualizations...", s: "Formatting data grids & chart traces", f: "100%" }
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

    let html = `
        <div style="margin-bottom: 24px;">
            <span class="sub-tag">— AI QUERY RESULT —</span>
            <h2 style="font-size: 28px; margin-top: 4px;">${title || 'Analytics Insight'}</h2>
            <p style="color: var(--text-muted); font-size: 14px;">Results for: "<em>${query}</em>"</p>
        </div>
    `;

    if (Array.isArray(data)) {
        html += renderTable(data);
    } else if (typeof data === 'object') {
        html += renderDict(data);
    } else {
        html += `<div>${data}</div>`;
    }

    viewContainer.innerHTML = html;
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

function renderDict(dictData) {
    let html = `<div class="results-grid">`;
    const scalars = Object.entries(dictData).filter(([k, v]) => typeof v !== 'object' || v === null);
    scalars.forEach(([k, v]) => {
        html += `
            <div class="stat-card-box">
                <div class="stat-card-title">${k.replace(/_/g, ' ')}</div>
                <div class="stat-card-val">${v}</div>
            </div>
        `;
    });

    const complexes = Object.entries(dictData).filter(([k, v]) => typeof v === 'object' && v !== null);
    complexes.forEach(([k, v]) => {
        html += `<div style="grid-column: span 12; margin-top: 16px;">
            <h4 style="text-transform: capitalize; margin-bottom: 8px;">${k.replace(/_/g, ' ')}</h4>
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
