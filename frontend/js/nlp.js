// ---------------------------------------------------------
// NLP SEARCH LOGIC
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
    const query = document.getElementById('nlp-search-input').value.trim();
    if (!query) return;

    viewContainer.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Asking AI Router...</p></div>`;

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'API Error');

        renderNLPResult(data);

    } catch (error) {
        console.error('NLP Error:', error);
        viewContainer.innerHTML = `<div class="card" style="text-align: center; color: #ef4444;"><i class="ph ph-warning-circle" style="font-size: 48px; margin-bottom: 16px;"></i><h3>AI Router Error</h3><p>${error.message}</p></div>`;
    }
}

function renderNLPResult(result) {
    const { view_type, title, data } = result;

    if (!data) {
        viewContainer.innerHTML = `<div class="card" style="color: #64748b;">No direct data returned. (This might be a plotting or print-only function in the backend.)</div>`;
        return;
    }
    
    if (data.error) {
        viewContainer.innerHTML = `<div class="card" style="color: #ef4444;">Error: ${data.error}</div>`;
        return;
    }

    let html = `<div class="dashboard-grid">`;

    if (view_type === 'player_stat') {
        const statValue = data.total_runs || data.average || data.boundary_percentage || 'N/A';
        html += `<div class="card stat-card" style="grid-column: span 12;"><div class="icon icon-blue"><i class="ph ph-chart-line-up"></i></div><h3>${title}</h3><div class="value">${statValue}</div><p style="color: var(--text-muted);">${data.player || ''}</p></div>`;
    } else if (view_type === 'bowler_stat') {
        const statValue = data.total_wickets || data.economy || data.bowling_average || 'N/A';
        html += `<div class="card stat-card" style="grid-column: span 12;"><div class="icon icon-green"><i class="ph ph-target"></i></div><h3>${title}</h3><div class="value">${statValue}</div><p style="color: var(--text-muted);">${data.player || ''}</p></div>`;
    } else if (view_type === 'team_stat') {
        const statValue = data.total_matches || data.total_wins || data.win_percentage || 'N/A';
        html += `<div class="card stat-card" style="grid-column: span 12;"><div class="icon icon-orange"><i class="ph ph-shield-chevron"></i></div><h3>${title}</h3><div class="value">${statValue}</div><p style="color: var(--text-muted);">${data.team || ''}</p></div>`;
    } else if (view_type === 'venue_stat') {
        const statValue = data.total_matches || data.average_first_innings_score || data.batting_first_win_percentage || 'N/A';
        html += `<div class="card stat-card" style="grid-column: span 12;"><div class="icon icon-purple"><i class="ph ph-map-pin"></i></div><h3>${title}</h3><div class="value">${statValue}</div><p style="color: var(--text-muted);">${data.venue || ''}</p></div>`;
    } else if (view_type === 'match_stat') {
        const statValue = data.chased_score ? `${data.chased_score} by ${data.winner}` : (data.margin ? `${data.margin} by ${data.winner}` : 'N/A');
        html += `<div class="card stat-card" style="grid-column: span 12;"><div class="icon icon-blue"><i class="ph ph-swords"></i></div><h3>${title}</h3><div class="value">${statValue}</div><p style="color: var(--text-muted);">${data.season || ''}</p></div>`;
    } else if (view_type === 'compare_batsmen_chart' || view_type === 'compare_bowlers_chart') {
        html += `<div class="card chart-card full-width"><div class="card-header"><h3>${title}</h3></div><div id="nlp-chart"></div></div>`;
    } else if (view_type.includes('chart')) {
        html += `<div class="card chart-card full-width"><div class="card-header"><h3>${title}</h3></div><div id="nlp-chart"></div></div>`;
    } else {
        html += `<div class="card" style="grid-column: span 12; overflow-x: auto;">`;
        html += renderGenericData(data);
        html += `</div>`;
    }

    html += `</div>`;
    viewContainer.innerHTML = html;

    // Render Plotly charts if necessary
    if (view_type === 'compare_batsmen_chart') {
        const p1 = data.player1; const p2 = data.player2;
        const stats = ['total_runs', 'average', 'strike_rate', 'fifties', 'centuries'];
        Plotly.newPlot('nlp-chart', [
            { name: p1.player || 'Player 1', x: stats, y: stats.map(s => p1[s] || 0), type: 'bar', marker: { color: '#3b82f6' } },
            { name: p2.player || 'Player 2', x: stats, y: stats.map(s => p2[s] || 0), type: 'bar', marker: { color: '#f97316' } }
        ], getPlotlyLayout('Value', { barmode: 'group' }));
    } else if (view_type === 'compare_bowlers_chart') {
        const p1 = data.player1; const p2 = data.player2;
        const stats = ['total_wickets', 'economy', 'bowling_average', 'four_wicket_hauls'];
        Plotly.newPlot('nlp-chart', [
            { name: p1.player || 'Player 1', x: stats, y: stats.map(s => p1[s] || 0), type: 'bar', marker: { color: '#3b82f6' } },
            { name: p2.player || 'Player 2', x: stats, y: stats.map(s => p2[s] || 0), type: 'bar', marker: { color: '#f97316' } }
        ], getPlotlyLayout('Value', { barmode: 'group' }));
    } else if (view_type === 'player_season_chart') {
        if(data.runs_by_season) {
            Plotly.newPlot('nlp-chart', [{ x: Object.keys(data.runs_by_season), y: Object.values(data.runs_by_season), type: 'scatter', line: {color:'#8b5cf6'} }], getPlotlyLayout('Runs'));
        }
    } else if (view_type === 'bowler_season_chart') {
        if(data.wickets_by_season) {
            Plotly.newPlot('nlp-chart', [{ x: Object.keys(data.wickets_by_season), y: Object.values(data.wickets_by_season), type: 'bar', marker: {color:'#10b981'} }], getPlotlyLayout('Wickets'));
        }
    }
}

// Helper to render complex JSON objects as HTML tables and lists
function renderGenericData(data) {
    if (Array.isArray(data)) {
        if (data.length === 0) return '<p>No data available</p>';
        if (typeof data[0] !== 'object' || data[0] === null) {
            return `<ul>${data.map(item => `<li>${item}</li>`).join('')}</ul>`;
        }
        
        // It's an array of objects, render a table
        const headers = Object.keys(data[0]);
        let tableHtml = `<table class="styled-table"><thead><tr>`;
        headers.forEach(h => {
            tableHtml += `<th>${h.replace(/_/g, ' ').toUpperCase()}</th>`;
        });
        tableHtml += `</tr></thead><tbody>`;
        
        data.forEach(row => {
            tableHtml += `<tr>`;
            headers.forEach(h => {
                let cellData = row[h];
                if (typeof cellData === 'object' && cellData !== null) cellData = JSON.stringify(cellData);
                tableHtml += `<td>${cellData}</td>`;
            });
            tableHtml += `</tr>`;
        });
        tableHtml += `</tbody></table>`;
        return tableHtml;
    } else if (typeof data === 'object' && data !== null) {
        let html = '';
        
        // Render scalar values first
        const scalars = Object.entries(data).filter(([k, v]) => typeof v !== 'object' || v === null);
        if (scalars.length > 0) {
            html += `<div style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px;">`;
            scalars.forEach(([k, v]) => {
                html += `<div style="background: var(--bg-color); padding: 12px 24px; border-radius: 8px; border: 1px solid var(--border-color); flex: 1; min-width: 150px;">
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">${k.replace(/_/g, ' ')}</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--text-color);">${v}</div>
                </div>`;
            });
            html += `</div>`;
        }
        
        // Render complex values (arrays or nested objects) below
        const complexes = Object.entries(data).filter(([k, v]) => typeof v === 'object' && v !== null);
        complexes.forEach(([k, v]) => {
            html += `<h4 style="margin-top: 16px; margin-bottom: 8px; color: var(--text-color); text-transform: capitalize;">${k.replace(/_/g, ' ')}</h4>`;
            if (Array.isArray(v)) {
                html += renderGenericData(v);
            } else {
                html += `<div style="background: var(--bg-color); padding: 12px; border-radius: 8px; border: 1px solid var(--border-color);">${renderGenericData(v)}</div>`;
            }
        });
        
        return html;
    }
    
    // Fallback for simple values
    return `<span>${data}</span>`;
}
