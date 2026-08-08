// ---------------------------------------------------------
// GLOBAL APP UTILITIES & UI CONTROLLERS
// ---------------------------------------------------------

const API_BASE = 'https://ipl-analytics-ca1e.onrender.com';

function toggleTheme() {
    const html = document.documentElement;
    const cur = html.getAttribute('data-theme');
    const newTheme = cur === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('eyantra_ipl_theme', newTheme);
}

function triggerPreset(q) {
    const input = document.getElementById('nlp-search-input');
    if (input) {
        input.value = q;
        if (typeof handleSearch === 'function') handleSearch();
    }
}

function triggerPresetSearch(q) {
    triggerPreset(q);
}

function triggerChipSearch(q) {
    triggerPreset(q);
}

function scrollToSection(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}
