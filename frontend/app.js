/**
 * Frontend Dashboard — app.js
 * Loads results.json and renders charts, tables, and KPI cards.
 */

// --- Global state ---
let allContracts = [];
let filteredContracts = [];
let currentPage = 1;
const ROWS_PER_PAGE = 15;
let sortColumn = "risk_score";
let sortAsc = false;

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
    createParticles();
    loadResults();
});

// --- Background Particles ---
function createParticles() {
    const container = document.getElementById("bgParticles");
    const colors = ["#c084fc", "#60a5fa", "#ff6b9d", "#22d3ee", "#4dff88"];
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement("div");
        particle.className = "particle";
        const size = Math.random() * 4 + 2;
        particle.style.width = size + "px";
        particle.style.height = size + "px";
        particle.style.left = Math.random() * 100 + "%";
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.animationDuration = (Math.random() * 20 + 15) + "s";
        particle.style.animationDelay = (Math.random() * 10) + "s";
        container.appendChild(particle);
    }
}

// --- Load Data ---
async function loadResults() {
    try {
        const resp = await fetch("results.json");
        if (!resp.ok) throw new Error("results.json not found");
        const data = await resp.json();
        renderDashboard(data);
    } catch (err) {
        document.getElementById("loadingContainer").innerHTML =
            `<div style="text-align:center;padding:3rem;">
                <p style="font-size:1.2rem;color:#ff4d6a;margin-bottom:1rem;">❌ Could not load results.json</p>
                <p style="color:#a0a0cc;">Run the pipeline first:</p>
                <code style="display:block;margin-top:0.5rem;color:#22d3ee;">
                    python data/generate_data.py<br>
                    streamlit run dashboard/app.py
                </code>
                <p style="color:#6b6b99;margin-top:1rem;font-size:0.85rem;">
                    The Streamlit app will generate frontend/results.json automatically.
                </p>
            </div>`;
    }
}

// --- Render All ---
function renderDashboard(data) {
    document.getElementById("loadingContainer").style.display = "none";
    document.getElementById("mainContent").style.display = "block";

    allContracts = data.contracts || [];
    filteredContracts = [...allContracts];

    renderKPIs(data.summary);
    renderRiskDistChart(data.risk_distribution);
    renderDeptChart(data.department_stats);
    renderFeatureChart(data.feature_importance);
    renderVendorList(data.top_risky_vendors);
    populateDeptFilter(data.department_stats);
    renderTable();

    // Attach event listeners
    document.getElementById("searchInput").addEventListener("input", applyFilters);
    document.getElementById("riskFilter").addEventListener("change", applyFilters);
    document.getElementById("deptFilter").addEventListener("change", applyFilters);
}

// --- KPIs ---
function renderKPIs(summary) {
    animateCounter("kpiTotal", summary.total_contracts);
    animateCounter("kpiAnomalies", summary.total_anomalies);
    animateCounter("kpiHighRisk", summary.high_risk_count);
    animateValue("kpiAvgRisk", summary.avg_risk_score, 1);
    animateValue("kpiRate", summary.anomaly_rate, 1, "%");
}

function animateCounter(elementId, target) {
    const el = document.getElementById(elementId);
    let current = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const interval = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(interval);
        }
        el.textContent = current.toLocaleString();
    }, 30);
}

function animateValue(elementId, target, decimals, suffix = "") {
    const el = document.getElementById(elementId);
    let current = 0;
    const step = target / 40;
    const interval = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(interval);
        }
        el.textContent = current.toFixed(decimals) + suffix;
    }, 30);
}

// --- Risk Distribution Chart ---
function renderRiskDistChart(dist) {
    const ctx = document.getElementById("riskDistChart").getContext("2d");
    const labels = dist.bins.slice(0, -1).map((b, i) => `${b}-${dist.bins[i + 1]}`);
    const colors = dist.counts.map((_, i) => {
        const ratio = i / (dist.counts.length - 1);
        if (ratio < 0.5) return `rgba(77, 255, 136, ${0.4 + ratio * 0.6})`;
        if (ratio < 0.7) return `rgba(251, 146, 60, ${0.5 + (ratio - 0.5) * 1.5})`;
        return `rgba(255, 77, 106, ${0.5 + (ratio - 0.7) * 1.5})`;
    });

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Contracts",
                data: dist.counts,
                backgroundColor: colors,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(20,20,50,0.95)",
                    borderColor: "rgba(100,100,200,0.3)",
                    borderWidth: 1,
                    titleColor: "#e8e8ff",
                    bodyColor: "#a0a0cc",
                    cornerRadius: 8,
                    padding: 12
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(100,100,200,0.08)" },
                    ticks: { color: "#6b6b99", font: { size: 10 } }
                },
                y: {
                    grid: { color: "rgba(100,100,200,0.08)" },
                    ticks: { color: "#6b6b99" }
                }
            },
            animation: { duration: 1200, easing: "easeOutQuart" }
        }
    });
}

// --- Department Chart ---
function renderDeptChart(deptStats) {
    const ctx = document.getElementById("deptChart").getContext("2d");
    const sorted = [...deptStats].sort((a, b) => b.anomalies - a.anomalies);
    const labels = sorted.map(d => d.dept.replace("Ministry of ", "").replace("Department of ", ""));

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Anomalies",
                data: sorted.map(d => d.anomalies),
                backgroundColor: "rgba(255, 77, 106, 0.6)",
                borderRadius: 4,
                borderSkipped: false
            }, {
                label: "Total",
                data: sorted.map(d => d.total_contracts),
                backgroundColor: "rgba(96, 165, 250, 0.3)",
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: "#a0a0cc", font: { size: 11 } }
                },
                tooltip: {
                    backgroundColor: "rgba(20,20,50,0.95)",
                    borderColor: "rgba(100,100,200,0.3)",
                    borderWidth: 1,
                    cornerRadius: 8, padding: 12
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(100,100,200,0.08)" },
                    ticks: { color: "#6b6b99" }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: "#a0a0cc", font: { size: 11 } }
                }
            },
            animation: { duration: 1200, easing: "easeOutQuart" }
        }
    });
}

// --- Feature Importance Chart ---
function renderFeatureChart(features) {
    const ctx = document.getElementById("featureChart").getContext("2d");
    const sorted = [...features].sort((a, b) => a.importance - b.importance);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: sorted.map(f => f.feature),
            datasets: [{
                label: "Mean |SHAP|",
                data: sorted.map(f => f.importance),
                backgroundColor: sorted.map((_, i) => {
                    const hue = 260 + (i / sorted.length) * 60;
                    return `hsla(${hue}, 70%, 65%, 0.7)`;
                }),
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(20,20,50,0.95)",
                    borderColor: "rgba(100,100,200,0.3)",
                    borderWidth: 1,
                    cornerRadius: 8, padding: 12
                }
            },
            scales: {
                x: {
                    grid: { color: "rgba(100,100,200,0.08)" },
                    ticks: { color: "#6b6b99" }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: "#a0a0cc", font: { size: 11 } }
                }
            },
            animation: { duration: 1400, easing: "easeOutQuart" }
        }
    });
}

// --- Vendor List ---
function renderVendorList(vendors) {
    const list = document.getElementById("vendorList");
    list.innerHTML = "";
    vendors.forEach((v, i) => {
        const scoreClass = v.avg_risk >= 70 ? "score-high" : v.avg_risk >= 40 ? "score-medium" : "score-low";
        const el = document.createElement("div");
        el.className = "vendor-item";
        el.style.animationDelay = (i * 0.05) + "s";
        el.innerHTML = `
            <div class="vendor-info">
                <div class="vendor-name" title="${v.vendor_name}">${v.vendor_name}</div>
                <div class="vendor-meta">${v.contracts} contracts · ${v.anomalies} anomalies · ₹${formatAmount(v.total_amount)}</div>
            </div>
            <div class="vendor-score ${scoreClass}">${v.avg_risk.toFixed(1)}</div>
        `;
        list.appendChild(el);
    });
}

// --- Table ---
function renderTable() {
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";

    // Sort
    const sorted = [...filteredContracts].sort((a, b) => {
        let va = a[sortColumn], vb = b[sortColumn];
        if (typeof va === "string") va = va.toLowerCase();
        if (typeof vb === "string") vb = vb.toLowerCase();
        if (va < vb) return sortAsc ? -1 : 1;
        if (va > vb) return sortAsc ? 1 : -1;
        return 0;
    });

    // Paginate
    const start = (currentPage - 1) * ROWS_PER_PAGE;
    const page = sorted.slice(start, start + ROWS_PER_PAGE);

    page.forEach(c => {
        const tr = document.createElement("tr");
        const badgeClass = c.risk_label === "High" ? "risk-badge-high" : "risk-badge-low";
        const badgeIcon = c.risk_label === "High" ? "🔴" : "🟢";
        const riskColor = c.risk_score >= 70 ? "#ff4d6a" : c.risk_score >= 40 ? "#fb923c" : "#4dff88";

        tr.innerHTML = `
            <td><strong>${c.contract_id}</strong></td>
            <td title="${c.vendor_name}">${truncate(c.vendor_name, 28)}</td>
            <td>${truncate(c.dept, 22)}</td>
            <td class="amount-cell">₹${formatAmount(c.amount)}</td>
            <td>${c.award_date}</td>
            <td class="risk-score-cell" style="color:${riskColor}">${c.risk_score.toFixed(1)}</td>
            <td><span class="risk-badge ${badgeClass}">${badgeIcon} ${c.risk_label}</span></td>
        `;
        tbody.appendChild(tr);
    });

    // Update count
    document.getElementById("tableCount").textContent =
        `Showing ${start + 1}–${Math.min(start + ROWS_PER_PAGE, sorted.length)} of ${sorted.length} contracts`;

    renderPagination(sorted.length);
}

function renderPagination(total) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";
    const pages = Math.ceil(total / ROWS_PER_PAGE);
    if (pages <= 1) return;

    const maxShow = 7;
    let startP = Math.max(1, currentPage - 3);
    let endP = Math.min(pages, startP + maxShow - 1);
    if (endP - startP < maxShow - 1) startP = Math.max(1, endP - maxShow + 1);

    if (currentPage > 1) {
        const prev = createPageBtn("‹", currentPage - 1);
        pagination.appendChild(prev);
    }

    for (let i = startP; i <= endP; i++) {
        const btn = createPageBtn(i, i);
        if (i === currentPage) btn.classList.add("active");
        pagination.appendChild(btn);
    }

    if (currentPage < pages) {
        const next = createPageBtn("›", currentPage + 1);
        pagination.appendChild(next);
    }
}

function createPageBtn(label, page) {
    const btn = document.createElement("button");
    btn.className = "page-btn";
    btn.textContent = label;
    btn.addEventListener("click", () => {
        currentPage = page;
        renderTable();
    });
    return btn;
}

// --- Filters ---
function applyFilters() {
    const search = document.getElementById("searchInput").value.toLowerCase();
    const risk = document.getElementById("riskFilter").value;
    const dept = document.getElementById("deptFilter").value;

    filteredContracts = allContracts.filter(c => {
        if (risk !== "all" && c.risk_label !== risk) return false;
        if (dept !== "all" && c.dept !== dept) return false;
        if (search) {
            const searchable = `${c.contract_id} ${c.vendor_name} ${c.dept} ${c.description}`.toLowerCase();
            if (!searchable.includes(search)) return false;
        }
        return true;
    });

    currentPage = 1;
    renderTable();
}

function populateDeptFilter(deptStats) {
    const select = document.getElementById("deptFilter");
    deptStats.forEach(d => {
        const opt = document.createElement("option");
        opt.value = d.dept;
        opt.textContent = d.dept;
        select.appendChild(opt);
    });
}

// --- Column Sorting ---
document.querySelectorAll(".data-table th").forEach(th => {
    th.addEventListener("click", () => {
        const colMap = {
            "th-id": "contract_id",
            "th-vendor": "vendor_name",
            "th-dept": "dept",
            "th-amount": "amount",
            "th-date": "award_date",
            "th-risk": "risk_score",
            "th-status": "risk_label"
        };
        const col = colMap[th.id];
        if (!col) return;
        if (sortColumn === col) {
            sortAsc = !sortAsc;
        } else {
            sortColumn = col;
            sortAsc = false;
        }
        currentPage = 1;
        renderTable();
    });
});

// --- Helpers ---
function formatAmount(amount) {
    if (amount >= 10000000) return (amount / 10000000).toFixed(2) + " Cr";
    if (amount >= 100000) return (amount / 100000).toFixed(2) + " L";
    return amount.toLocaleString("en-IN");
}

function truncate(str, max) {
    if (!str) return "";
    return str.length > max ? str.substring(0, max) + "…" : str;
}
