const API_BASE = 'http://127.0.0.1:5000';

const viewContainer = document.getElementById('view-container');

// ---------------------------------------------------------
// UTILS
// ---------------------------------------------------------
function getPlotlyLayout(yTitle, extra = {}) {
    return {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#94a3b8', family: 'Inter' },
        margin: { t: 20, r: 20, l: 50, b: 40 },
        xaxis: { 
            gridcolor: 'rgba(255,255,255,0.05)',
            zerolinecolor: 'rgba(255,255,255,0.05)'
        },
        yaxis: { 
            title: yTitle,
            gridcolor: 'rgba(255,255,255,0.05)',
            zerolinecolor: 'rgba(255,255,255,0.05)'
        },
        ...extra
    };
}
