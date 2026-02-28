/**
 * Budget Tracker – Frontend Application
 * ======================================
 * Vanilla JS client that communicates with the FastAPI backend.
 */

const API_BASE = window.location.origin;

// ── DOM References ────────────────────────────────────────────────────────

const form             = document.getElementById("transaction-form");
const tableBody        = document.getElementById("transactions-body");
const emptyState       = document.getElementById("empty-state");
const totalIncomeEl    = document.getElementById("total-income");
const totalExpensesEl  = document.getElementById("total-expenses");
const balanceEl        = document.getElementById("balance");
const filterMonth      = document.getElementById("filter-month");
const filterYear       = document.getElementById("filter-year");
const btnFilter        = document.getElementById("btn-filter");

// ── Helpers ───────────────────────────────────────────────────────────────

/**
 * Format a number as Euro currency string.
 */
function formatEuro(value) {
    return new Intl.NumberFormat("de-DE", {
        style: "currency",
        currency: "EUR",
    }).format(value);
}

/**
 * Format an ISO date string to a locale-friendly format.
 */
function formatDate(isoDate) {
    return new Date(isoDate).toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
    });
}

/**
 * Build URL query string from an object (skips empty values).
 */
function buildQuery(params) {
    const filtered = Object.entries(params).filter(([, v]) => v !== "" && v != null);
    if (filtered.length === 0) return "";
    return "?" + new URLSearchParams(filtered).toString();
}

// ── API Calls ─────────────────────────────────────────────────────────────

async function fetchTransactions(params = {}) {
    const res = await fetch(`${API_BASE}/transactions${buildQuery(params)}`);
    if (!res.ok) throw new Error("Failed to fetch transactions");
    return res.json();
}

async function fetchSummary(params = {}) {
    const res = await fetch(`${API_BASE}/summary${buildQuery(params)}`);
    if (!res.ok) throw new Error("Failed to fetch summary");
    return res.json();
}

async function createTransaction(data) {
    const res = await fetch(`${API_BASE}/transactions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Failed to create transaction");
    }
    return res.json();
}

async function deleteTransaction(id) {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete transaction");
}

// ── Rendering ─────────────────────────────────────────────────────────────

function renderSummary(summary) {
    totalIncomeEl.textContent   = formatEuro(summary.total_income);
    totalExpensesEl.textContent = formatEuro(summary.total_expenses);
    balanceEl.textContent       = formatEuro(summary.balance);
}

function renderTransactions(transactions) {
    tableBody.innerHTML = "";

    if (transactions.length === 0) {
        emptyState.style.display = "block";
        return;
    }

    emptyState.style.display = "none";

    transactions.forEach((t) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${formatDate(t.date)}</td>
            <td><span class="badge badge--${t.type}">${t.type === "income" ? "Einnahme" : "Ausgabe"}</span></td>
            <td>${t.category}</td>
            <td class="amount--${t.type}">${t.type === "income" ? "+" : "−"} ${formatEuro(t.amount)}</td>
            <td>${t.note || "–"}</td>
            <td><button class="btn btn--danger" data-id="${t.id}" title="Löschen">✕</button></td>
        `;
        tableBody.appendChild(tr);
    });
}

function populateYearFilter(transactions) {
    const years = [...new Set(transactions.map((t) => new Date(t.date).getFullYear()))].sort((a, b) => b - a);
    const current = filterYear.value;
    filterYear.innerHTML = '<option value="">Alle Jahre</option>';
    years.forEach((y) => {
        const opt = document.createElement("option");
        opt.value = y;
        opt.textContent = y;
        if (String(y) === current) opt.selected = true;
        filterYear.appendChild(opt);
    });
}

// ── Data Loading ──────────────────────────────────────────────────────────

async function loadData() {
    const params = {};
    if (filterMonth.value) params.month = filterMonth.value;
    if (filterYear.value)  params.year  = filterYear.value;

    try {
        const [transactions, summary] = await Promise.all([
            fetchTransactions(params),
            fetchSummary(params),
        ]);
        renderSummary(summary);
        renderTransactions(transactions);

        // Populate year filter from ALL transactions (unfiltered)
        const all = await fetchTransactions();
        populateYearFilter(all);
    } catch (err) {
        console.error("Error loading data:", err);
    }
}

// ── Event Handlers ────────────────────────────────────────────────────────

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        type:     document.getElementById("type").value,
        amount:   parseFloat(document.getElementById("amount").value),
        category: document.getElementById("category").value,
        date:     document.getElementById("date").value || undefined,
        note:     document.getElementById("note").value || "",
    };

    try {
        await createTransaction(data);
        form.reset();
        document.getElementById("date").valueAsDate = new Date();
        await loadData();
    } catch (err) {
        alert("Fehler: " + err.message);
    }
});

tableBody.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-id]");
    if (!btn) return;

    if (!confirm("Buchung wirklich löschen?")) return;

    try {
        await deleteTransaction(btn.dataset.id);
        await loadData();
    } catch (err) {
        alert("Fehler beim Löschen: " + err.message);
    }
});

btnFilter.addEventListener("click", loadData);

// ── Init ──────────────────────────────────────────────────────────────────

document.getElementById("date").valueAsDate = new Date();
loadData();
