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

// ---------------------------------------------------------
// INTERACTIVE MOUSE-MOVE & SCROLL PARALLAX CONTROLLER
// ---------------------------------------------------------
document.addEventListener('DOMContentLoaded', function initBgParallax() {
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;

    const bgContainer = document.getElementById('bg-parallax-container');
    const fig1 = document.getElementById('bg-fig-1');
    const fig2 = document.getElementById('bg-fig-2');
    const fig3 = document.getElementById('bg-fig-3');
    const fig4 = document.getElementById('bg-fig-4');
    const fig5 = document.getElementById('bg-fig-5');
    const fig6 = document.getElementById('bg-fig-6');
    const fig7 = document.getElementById('bg-fig-7');
    const fig8 = document.getElementById('bg-fig-8');
    const fig9 = document.getElementById('bg-fig-9');
    const fig10 = document.getElementById('bg-fig-10');
    const fig11 = document.getElementById('bg-fig-11');
    const fig12 = document.getElementById('bg-fig-12');

    window.addEventListener('mousemove', function (e) {
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        mouseX = (e.clientX / windowWidth - 0.5) * 2;
        mouseY = (e.clientY / windowHeight - 0.5) * 2;
    });

    function animate() {
        const scrollY = window.scrollY || window.pageYOffset || 0;

        // Smooth spring interpolation (lerp)
        targetX += (mouseX - targetX) * 0.06;
        targetY += (mouseY - targetY) * 0.06;

        if (bgContainer) {
            bgContainer.style.transform = `translate3d(${targetX * 10}px, ${targetY * 10}px, 0)`;
        }

        if (fig1) fig1.style.transform = `translate3d(${targetX * 35}px, ${targetY * 35 + scrollY * -0.15}px, 0) rotate(${targetX * 4}deg)`;
        if (fig5) fig5.style.transform = `translate3d(${targetX * -25}px, ${targetY * -25 + scrollY * -0.12}px, 0) rotate(${targetX * -3}deg)`;
        if (fig2) fig2.style.transform = `translate3d(${targetX * -30}px, ${targetY * -30 + scrollY * -0.1}px, 0) rotate(${targetX * -2}deg)`;
        if (fig6) fig6.style.transform = `translate3d(${targetX * 38}px, ${targetY * 38 + scrollY * -0.16}px, 0) rotate(${targetX * 4}deg)`;
        if (fig3) fig3.style.transform = `translate3d(${targetX * 40}px, ${targetY * 40 + scrollY * -0.18}px, 0) rotate(${targetX * 5}deg)`;
        if (fig7) fig7.style.transform = `translate3d(${targetX * -32}px, ${targetY * -32 + scrollY * -0.11}px, 0) rotate(${targetX * -4}deg)`;
        if (fig4) fig4.style.transform = `translate3d(${targetX * -35}px, ${targetY * -35 + scrollY * -0.13}px, 0)`;
        if (fig8) fig8.style.transform = `translate3d(${targetX * 36}px, ${targetY * 36 + scrollY * -0.17}px, 0) rotate(${targetX * 3}deg)`;
        if (fig9) fig9.style.transform = `translate3d(${targetX * -28}px, ${targetY * -28 + scrollY * -0.12}px, 0) rotate(${targetX * -3}deg)`;
        if (fig10) fig10.style.transform = `translate3d(${targetX * 34}px, ${targetY * 34 + scrollY * -0.15}px, 0) rotate(${targetX * 4}deg)`;
        if (fig11) fig11.style.transform = `translate3d(${targetX * -30}px, ${targetY * -30 + scrollY * -0.11}px, 0) rotate(${targetX * -2}deg)`;
        if (fig12) fig12.style.transform = `translate3d(${targetX * 36}px, ${targetY * 36 + scrollY * -0.16}px, 0) rotate(${targetX * 3}deg)`;

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
});

// =========================================================
// REFERENCE 1: REUSABLE VIEWPORT NUMERICAL COUNT-UP SYSTEM
// =========================================================
function formatNumberWithCommas(num) {
    return Math.floor(num).toLocaleString('en-US');
}

function animateCounter(element, duration = 1800) {
    const target = parseInt(element.getAttribute('data-counter-target') || '0', 10);
    const suffix = element.getAttribute('data-counter-suffix') || '+';

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        element.innerHTML = `${formatNumberWithCommas(target)}<span>${suffix}</span>`;
        return;
    }

    let startTime = null;
    const startValue = 0;

    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = startValue + (target - startValue) * easeProgress;

        element.innerHTML = `${formatNumberWithCommas(currentValue)}<span>${suffix}</span>`;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.innerHTML = `${formatNumberWithCommas(target)}<span>${suffix}</span>`;
        }
    }

    requestAnimationFrame(step);
}

function initCounterObserver() {
    const section = document.getElementById('achievements-section');
    if (!section) return;

    let hasAnimated = false;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasAnimated) {
                hasAnimated = true;
                const counters = section.querySelectorAll('.stat-num-giant[data-counter-target]');
                counters.forEach((counter, idx) => {
                    setTimeout(() => {
                        animateCounter(counter, 1800);
                    }, idx * 120);
                });
                observer.unobserve(section);
            }
        });
    }, { threshold: 0.2 });

    observer.observe(section);
}

// =========================================================
// REFERENCE 2: FLOWCHART / TIMELINE PROGRESSIVE REVEAL SYSTEM
// =========================================================
function updateTimelinePaths() {
    const svg = document.getElementById('timeline-svg');
    const container = document.getElementById('timeline-grid');
    if (!svg || !container) return;

    const cards = Array.from(container.querySelectorAll('.timeline-card'));
    if (cards.length < 5) return;

    const containerRect = container.getBoundingClientRect();
    svg.setAttribute('width', containerRect.width);
    svg.setAttribute('height', containerRect.height);

    function getCardEdge(card, side) {
        const r = card.getBoundingClientRect();
        const left = r.left - containerRect.left;
        const top = r.top - containerRect.top;
        const width = r.width;
        const height = r.height;

        switch (side) {
            case 'right': return { x: left + width, y: top + height / 2 };
            case 'left': return { x: left, y: top + height / 2 };
            case 'bottom': return { x: left + width / 2, y: top + height };
            case 'top': return { x: left + width / 2, y: top };
            default: return { x: left + width / 2, y: top + height / 2 };
        }
    }

    const isDesktop = window.innerWidth >= 992;
    let pathData = [];

    if (isDesktop) {
        // Desktop 2-Row Flow: [1] -> [2] -> [3] -> (downward) -> [4] -> [5]
        const p1_out = getCardEdge(cards[0], 'right');
        const p2_in = getCardEdge(cards[1], 'left');
        const p2_out = getCardEdge(cards[1], 'right');
        const p3_in = getCardEdge(cards[2], 'left');
        const p3_out = getCardEdge(cards[2], 'bottom');
        const p4_in = getCardEdge(cards[3], 'top');
        const p4_out = getCardEdge(cards[3], 'right');
        const p5_in = getCardEdge(cards[4], 'left');

        pathData.push({ id: 'path-1-2', d: `M ${p1_out.x} ${p1_out.y} L ${p2_in.x} ${p2_in.y}` });
        pathData.push({ id: 'path-2-3', d: `M ${p2_out.x} ${p2_out.y} L ${p3_in.x} ${p3_in.y}` });

        const midY = (p3_out.y + p4_in.y) / 2;
        pathData.push({ id: 'path-3-4', d: `M ${p3_out.x} ${p3_out.y} C ${p3_out.x} ${midY}, ${p4_in.x} ${midY}, ${p4_in.x} ${p4_in.y}` });
        pathData.push({ id: 'path-4-5', d: `M ${p4_out.x} ${p4_out.y} L ${p5_in.x} ${p5_in.y}` });
    } else {
        // Mobile Vertical Flow: 1 -> 2 -> 3 -> 4 -> 5
        for (let i = 0; i < 4; i++) {
            const start = getCardEdge(cards[i], 'bottom');
            const end = getCardEdge(cards[i + 1], 'top');
            pathData.push({ id: `path-${i + 1}-${i + 2}`, d: `M ${start.x} ${start.y} L ${end.x} ${end.y}` });
        }
    }

    pathData.forEach(p => {
        const pathEl = document.getElementById(p.id);
        if (pathEl) {
            pathEl.setAttribute('d', p.d);
            const totalLen = pathEl.getTotalLength();
            pathEl.style.strokeDasharray = totalLen;
            if (!pathEl.dataset.drawn) {
                pathEl.style.strokeDashoffset = totalLen;
            }
        }
    });
}

function drawPath(pathId, duration = 400) {
    return new Promise(resolve => {
        const pathEl = document.getElementById(pathId);
        if (!pathEl) { resolve(); return; }

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            pathEl.style.strokeDashoffset = '0';
            pathEl.dataset.drawn = 'true';
            resolve();
            return;
        }

        const totalLen = pathEl.getTotalLength();
        pathEl.style.strokeDasharray = totalLen;

        let startTime = null;
        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 2);
            pathEl.style.strokeDashoffset = totalLen * (1 - easeProgress);

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                pathEl.style.strokeDashoffset = '0';
                pathEl.dataset.drawn = 'true';
                resolve();
            }
        }

        requestAnimationFrame(step);
    });
}

function revealTimelineCard(cardEl) {
    if (cardEl) {
        cardEl.classList.add('revealed');
    }
}

async function runTimelineSequence() {
    const container = document.getElementById('timeline-grid');
    if (!container) return;
    const cards = [
        container.querySelector('.timeline-card[data-stage="1"]'),
        container.querySelector('.timeline-card[data-stage="2"]'),
        container.querySelector('.timeline-card[data-stage="3"]'),
        container.querySelector('.timeline-card[data-stage="4"]'),
        container.querySelector('.timeline-card[data-stage="5"]')
    ];

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        cards.forEach(c => revealTimelineCard(c));
        ['path-1-2', 'path-2-3', 'path-3-4', 'path-4-5'].forEach(pId => {
            const p = document.getElementById(pId);
            if (p) { p.style.strokeDashoffset = '0'; p.dataset.drawn = 'true'; }
        });
        return;
    }

    revealTimelineCard(cards[0]);
    await new Promise(r => setTimeout(r, 250));

    await drawPath('path-1-2', 380);
    revealTimelineCard(cards[1]);
    await new Promise(r => setTimeout(r, 250));

    await drawPath('path-2-3', 380);
    revealTimelineCard(cards[2]);
    await new Promise(r => setTimeout(r, 250));

    await drawPath('path-3-4', 450);
    revealTimelineCard(cards[3]);
    await new Promise(r => setTimeout(r, 250));

    await drawPath('path-4-5', 380);
    revealTimelineCard(cards[4]);
}

function initTimelineObserver() {
    const section = document.getElementById('timeline-section');
    if (!section) return;

    let hasRun = false;

    window.addEventListener('resize', updateTimelinePaths);
    updateTimelinePaths();

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasRun) {
                hasRun = true;
                runTimelineSequence();
                observer.unobserve(section);
            }
        });
    }, { threshold: 0.15 });

    observer.observe(section);
}

document.addEventListener('DOMContentLoaded', function () {
    initCounterObserver();
    initTimelineObserver();
});
