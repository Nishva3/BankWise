(() => {
  const API_KEY = "bankwise_api_base";
  const TOKEN_KEY = "bankwise_access_token";
  const USER_KEY = "bankwise_user";
  const THEME_KEY = "bankwise_theme";
  const DENSITY_KEY = "bankwise_density";
  const LANDING_KEY = "bankwise_default_page";
  const API = () => (localStorage.getItem(API_KEY) || "https://bankwise-api.onrender.com").replace(/\/$/, "");
  const screen = document.body.dataset.screen || "";
  const routes = {
    overview: "bankwise_overview_dashboard", "upload-statement": "bankwise_upload_statement",
    transactions: "bankwise_transactions", "financial-insights": "bankwise_financial_insights",
    "anomaly-detection": "bankwise_anomaly_detection", "classification-review": "bankwise_classification_review",
    "reports-&-exports": "bankwise_reports_exports", settings: "bankwise_settings",
    "help-&-support": "bankwise_settings"
  };
  const categories = ["Food & Dining", "Groceries", "Shopping", "Transportation", "Entertainment", "Healthcare", "Education", "Utilities", "Housing & Rent", "Travel", "Insurance", "Salary & Income", "Investments", "ATM & Cash Withdrawal", "Bank Charges", "Loan & EMI", "Transfers", "Other / Uncategorized"];
  const token = () => localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
  const preferenceStyle = document.createElement("style");
  preferenceStyle.textContent = `
    html[data-bw-theme="dark"] body { background:#111a16!important;color:#e6f2ec!important; }
    html[data-bw-theme="dark"] main { background:#111a16!important;color:#e6f2ec!important; }
    html[data-bw-theme="dark"] aside,html[data-bw-theme="dark"] header,html[data-bw-theme="dark"] .bg-white { background:#1e2b25!important;color:#e6f2ec!important;border-color:#34463c!important; }
    html[data-bw-theme="dark"] .bg-\\[\\#eaf7f0\\],html[data-bw-theme="dark"] .bg-\\[\\#f0fcf6\\] { background:#26372f!important;color:#e6f2ec!important; }
    html[data-bw-theme="dark"] .text-\\[\\#131e1a\\],html[data-bw-theme="dark"] .text-\\[\\#53615b\\],html[data-bw-theme="dark"] .text-gray-500 { color:#c4d4cb!important; }
    html[data-bw-theme="dark"] .text-on-surface,html[data-bw-theme="dark"] .text-on-surface-variant { color:#d6e5dc!important; }
    html[data-bw-theme="dark"] input,html[data-bw-theme="dark"] select,html[data-bw-theme="dark"] textarea { background:#17231d!important;color:#e6f2ec!important;border-color:#52685b!important; }
    html[data-bw-density="compact"] main .space-y-5 { row-gap:.75rem!important; }
    html[data-bw-density="compact"] main .p-5 { padding:1rem!important; }
  `;
  document.head.append(preferenceStyle);
  function applyPreferences() {
    const preference = localStorage.getItem(THEME_KEY) || "light";
    const dark = preference === "dark" || (preference === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.bwTheme = dark ? "dark" : "light";
    document.documentElement.dataset.bwDensity = localStorage.getItem(DENSITY_KEY) || "comfortable";
  }
  applyPreferences();
  if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", () => { if ((localStorage.getItem(THEME_KEY) || "light") === "system") applyPreferences(); });
  const apiStatus = connected => {
    const badge = [...document.querySelectorAll("header span")].find(el => /REST API Connected|API Unavailable|API Connected/.test(el.textContent));
    if (badge) badge.textContent = connected ? "REST API Connected" : "API Unavailable";
  };
  if (screen === "settings") {
    const badge = [...document.querySelectorAll("header span")].find(el => /REST API Connected|API Unavailable|API Connected/.test(el.textContent));
    badge?.parentElement?.remove();
  }
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[c]));
  const displayDate = value => {
    if (!value) return "N/A";
    const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (match) return `${match[3]}/${match[2]}/${match[1]}`;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat(undefined, {day:"2-digit",month:"short",year:"numeric"}).format(date);
  };
  const money = value => value == null || value === "" ? "N/A" : new Intl.NumberFormat(undefined, { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(Number(value));
  const toast = (message, bad = false) => {
    let box = document.getElementById("bankwise-toast");
    if (!box) { box = document.createElement("div"); box.id = "bankwise-toast"; box.setAttribute("role", "status"); box.style.cssText = "position:fixed;right:24px;bottom:24px;z-index:9999;max-width:420px;padding:14px 18px;border-radius:12px;color:white;box-shadow:0 8px 28px #0003;font:500 14px Inter, sans-serif"; document.body.append(box); }
    box.style.background = bad ? "#a32626" : "#00513f"; box.textContent = message; box.hidden = false;
    clearTimeout(box._timer); box._timer = setTimeout(() => { box.hidden = true; }, 5000);
  };
  async function api(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (token()) headers.set("Authorization", `Bearer ${token()}`);
    if (options.body && !(options.body instanceof FormData) && typeof options.body !== "string") {
      headers.set("Content-Type", "application/json"); options.body = JSON.stringify(options.body);
    }
    const response = await fetch(`${API()}${path}`, { ...options, headers });
    if (options.raw) { if (!response.ok) throw new Error(`Export failed (${response.status})`); return response.blob(); }
    const type = response.headers.get("content-type") || "";
    const data = type.includes("json") ? await response.json() : null;
    if (!response.ok) { apiStatus(false); const error = new Error(data?.message || data?.error || `Request failed (${response.status})`); error.status = response.status; throw error; }
    apiStatus(true);
    return data;
  }
  const go = page => { location.href = `../${routes[page] || routes.overview}/code.html`; };
  const goLanding = () => go(localStorage.getItem(LANDING_KEY) || "overview");
  const displayError = error => toast(error.message || "The request could not be completed.", true);
  const valueAt = (root, selector, fallback = "") => root.querySelector(selector)?.value ?? fallback;
  const addLivePanel = (title, content) => {
    const main = document.querySelector("main"); if (!main) return null;
    const panel = document.createElement("section"); panel.id = "bankwise-live-panel";
    panel.className = "mx-6 my-5 rounded-xl bg-white p-5 shadow-sm";
    panel.innerHTML = `<div class="mb-2 flex items-center justify-between gap-3"><h2 class="text-lg font-semibold">${esc(title)}</h2><span class="rounded-full bg-[#bfedd4] px-3 py-1 text-xs font-semibold text-[#00513f]">Live account data</span></div><p class="mb-4 text-xs text-gray-500">Values shown in this panel come from your account. The original Stitch page below contains sample preview content.</p>${content}`;
    main.prepend(panel); return panel;
  };
  const setUser = user => {
    const saved = user || JSON.parse(localStorage.getItem(USER_KEY) || "null");
    if (!saved) return;
    localStorage.setItem(USER_KEY, JSON.stringify(saved));
    document.querySelectorAll("aside .font-label-md.truncate").forEach(el => { el.textContent = saved.name || saved.email?.split("@")[0] || "Account"; });
    document.querySelectorAll("aside .font-label-sm.truncate").forEach(el => { el.textContent = saved.email || ""; });
  };
  async function openProfile() {
    let user;
    try { user = (await api("/api/auth/me")).user; setUser(user); }
    catch (error) { displayError(error); return; }
    document.getElementById("profile-overlay")?.remove();
    const overlay = document.createElement("div"); overlay.id = "profile-overlay";
    overlay.className = "fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4";
    overlay.setAttribute("role", "presentation");
    overlay.innerHTML = `<section role="dialog" aria-modal="true" aria-labelledby="profile-title" class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl"><div class="mb-4 flex items-center justify-between"><h2 id="profile-title" class="text-xl font-semibold">Your profile</h2><button type="button" data-profile-close aria-label="Close profile" class="rounded-lg px-3 py-2 hover:bg-gray-100">Close</button></div><form id="profile-form" class="space-y-4"><label class="block text-sm">Full name<input class="${inputClass}" name="name" required maxlength="120" value="${esc(user.name)}"></label><label class="block text-sm">Email<input class="${inputClass} mt-1" value="${esc(user.email)}" readonly></label><label class="block text-sm">Phone (optional)<input class="${inputClass} mt-1" name="phone" maxlength="40" value="${esc(user.phone)}"></label><label class="block text-sm">Institution or employer (optional)<input class="${inputClass} mt-1" name="institution" maxlength="120" value="${esc(user.institution)}"></label><label class="block text-sm">City (optional)<input class="${inputClass} mt-1" name="city" maxlength="100" value="${esc(user.city)}"></label><div class="flex justify-end gap-2"><button type="button" data-profile-close class="${secondaryClass}">Cancel</button><button type="submit" class="${buttonClass}">Save profile</button></div></form></section>`;
    document.body.append(overlay);
    overlay.querySelectorAll("[data-profile-close]").forEach(button => button.onclick = () => overlay.remove());
    overlay.addEventListener("click", event => { if (event.target === overlay) overlay.remove(); });
    overlay.querySelector("#profile-form").onsubmit = async event => {
      event.preventDefault(); const button = event.currentTarget.querySelector('[type="submit"]'); button.disabled = true;
      const form = new FormData(event.currentTarget);
      try {
        const result = await api("/api/auth/me", {method:"PATCH", body:{name:form.get("name"),phone:form.get("phone"),institution:form.get("institution"),city:form.get("city")}});
        setUser(result.user); overlay.remove(); toast("Profile saved.");
      } catch(error) { displayError(error); button.disabled = false; }
    };
  }
  function openTransactionEditor(transaction, onSaved) {
    document.getElementById("transaction-edit-overlay")?.remove();
    const overlay=document.createElement("div");overlay.id="transaction-edit-overlay";overlay.className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4";
    overlay.innerHTML=`<section role="dialog" aria-modal="true" aria-labelledby="transaction-edit-title" class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl"><div class="mb-4 flex items-center justify-between"><h2 id="transaction-edit-title" class="text-xl font-semibold">Edit transaction</h2><button type="button" data-close class="${secondaryClass}">Close</button></div><form id="transaction-edit-form" class="grid gap-4 sm:grid-cols-2"><label class="text-sm sm:col-span-2">Description<input class="${inputClass} mt-1" name="description" required maxlength="500" value="${esc(transaction.description)}"></label><label class="text-sm">Date<input class="${inputClass} mt-1" type="date" name="date" value="${esc(transaction.date||"")}"></label><label class="text-sm">Category<select class="${inputClass} mt-1" name="category">${categories.map(c=>`<option ${c===transaction.final_category?"selected":""}>${esc(c)}</option>`).join("")}</select></label><label class="text-sm">Debit<input class="${inputClass} mt-1" type="number" min="0" step="0.01" name="debit" value="${transaction.debit??""}"></label><label class="text-sm">Credit<input class="${inputClass} mt-1" type="number" min="0" step="0.01" name="credit" value="${transaction.credit??""}"></label><label class="text-sm">Balance<input class="${inputClass} mt-1" type="number" step="0.01" name="balance" value="${transaction.balance??""}"></label><label class="text-sm">Reference (optional)<input class="${inputClass} mt-1" name="reference" maxlength="100" value="${esc(transaction.reference||"")}"></label><div class="flex justify-end gap-2 sm:col-span-2"><button type="button" data-close class="${secondaryClass}">Cancel</button><button type="submit" class="${buttonClass}">Save transaction</button></div></form></section>`;
    document.body.append(overlay);overlay.querySelectorAll("[data-close]").forEach(b=>b.onclick=()=>overlay.remove());overlay.addEventListener("click",e=>{if(e.target===overlay)overlay.remove();});
    overlay.querySelector("#transaction-edit-form").onsubmit=async e=>{e.preventDefault();const b=e.currentTarget.querySelector('[type="submit"]');b.disabled=true;const form=new FormData(e.currentTarget);const body={description:form.get("description"),date:form.get("date")||null,category:form.get("category"),reference:form.get("reference")||null};for(const field of ["debit","credit","balance"])body[field]=form.get(field)===""?null:Number(form.get(field));try{await api(`/api/transactions/${transaction._id}`,{method:"PUT",body});overlay.remove();toast("Transaction saved.");onSaved?.();}catch(error){displayError(error);b.disabled=false;}};
  }
  const logout = () => { localStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); location.href = "../bankwise_authentication/code.html"; };

  // Generated navigation links all point to '#'; map them to the matching Stitch screen.
  document.querySelectorAll("a[data-path]").forEach(link => {
    const path = link.dataset.path;
    if (routes[path]) link.href = `../${routes[path]}/code.html`;
    else if (path === "help-&-support") { link.href = "#help"; link.addEventListener("click", e => { e.preventDefault(); toast("For help, review the project README or contact your administrator."); }); }
  });
  const dateLabel = document.querySelector("header .font-data-mono.text-data-mono");
  if (dateLabel) dateLabel.textContent = "All account activity";
  document.querySelectorAll('button[title="Logout"]').forEach(button => button.addEventListener("click", logout));
  document.querySelectorAll("[data-profile-trigger]").forEach(button => button.addEventListener("click", openProfile));

  async function requireSession() {
    if (!token()) { location.href = "../bankwise_authentication/code.html"; return false; }
    try {
      const result = await api("/api/auth/me"); setUser(result.user);
      const cleanupKey = `bankwise-dedupe-v2:${result.user.id}`;
      if (!sessionStorage.getItem(cleanupKey)) {
        try {
          const cleanup = await api("/api/transactions/deduplicate", {method:"POST", body:{}});
          sessionStorage.setItem(cleanupKey, "done");
          if (cleanup.removed_count) sessionStorage.setItem("bankwise-flash", `${cleanup.removed_count} exact duplicate transaction rows were removed from your ledger.`);
        } catch(error) {
          if (error.status === 404 && !sessionStorage.getItem("bankwise-dedupe-route-notice")) {
            sessionStorage.setItem("bankwise-dedupe-route-notice", "shown");
            toast("Restart the backend to load the latest duplicate-cleanup API.", true);
          } else if (error.status !== 404) displayError(error);
        }
      }
      return true;
    }
    catch (error) {
      if (error.status === 401 || error.status === 422) logout();
      else displayError(error);
      return false;
    }
  }
  async function download(path, filename) {
    const blob = await api(path, { raw: true }); const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
  }

  // Authentication screen
  window.handleAuthSubmit = async (event, mode) => {
    event.preventDefault(); const form = event.target; const button = form.querySelector('[type="submit"]');
    const original = button?.innerHTML; if (button) { button.disabled = true; button.textContent = "Connecting"; }
    try {
      const register = mode === "register";
      const email = valueAt(form, register ? "#reg-email" : "#signin-email").trim().toLowerCase();
      const password = valueAt(form, register ? "#reg-password" : "#signin-password");
      const name = register ? valueAt(form, "#reg-name").trim() : "";
      if (register && password !== valueAt(form, "#reg-confirm-password")) throw new Error("The passwords do not match.");
      if (register && password.length < 10) throw new Error("Use a password with at least 10 characters.");
      if (register && !name) throw new Error("Enter your name to create an account.");
      if (register) await api("/api/auth/register", { method: "POST", body: { name, email, password } });
      const result = await api("/api/auth/login", { method: "POST", body: { email, password } });
      localStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(TOKEN_KEY);
      const remember = !register && Boolean(form.querySelector('input[type="checkbox"]')?.checked);
      (remember ? localStorage : sessionStorage).setItem(TOKEN_KEY, result.access_token);
      const me = await api("/api/auth/me"); setUser(me.user); goLanding();
    } catch (error) { displayError(error); }
    finally { if (button) { button.disabled = false; button.innerHTML = original; } }
  };
  window.switchAuthTab = target => {
    const isSignIn=target==="signin";
    document.getElementById("panel-signin")?.classList.toggle("hidden",!isSignIn);
    document.getElementById("panel-register")?.classList.toggle("hidden",isSignIn);
    document.getElementById("tab-btn-signin")?.classList.toggle("bg-surface-container-lowest",isSignIn);
    document.getElementById("tab-btn-signin")?.classList.toggle("shadow-sm",isSignIn);
    document.getElementById("tab-btn-register")?.classList.toggle("bg-surface-container-lowest",!isSignIn);
    document.getElementById("tab-btn-register")?.classList.toggle("shadow-sm",!isSignIn);
  };
  window.togglePasswordVisibility = (inputId, button) => {
    const input=document.getElementById(inputId);if(!input)return;
    input.type=input.type==="password"?"text":"password";
    const icon=button?.querySelector(".material-symbols-outlined");if(icon)icon.textContent=input.type==="password"?"visibility":"visibility_off";
  };
  if (screen === "authentication") {
    document.querySelector("#panel-signin form")?.addEventListener("submit",event=>window.handleAuthSubmit(event,"login"));
    document.querySelector("#panel-register form")?.addEventListener("submit",event=>window.handleAuthSubmit(event,"register"));
    document.getElementById("tab-btn-signin")?.addEventListener("click",()=>window.switchAuthTab("signin"));
    document.getElementById("tab-btn-register")?.addEventListener("click",()=>window.switchAuthTab("register"));
    document.querySelectorAll("#panel-signin button,#panel-register button").forEach(button=>{
      if(button.type==="button"&&button.querySelector(".material-symbols-outlined")?.textContent.includes("visibility"))button.addEventListener("click",()=>{const input=button.parentElement.querySelector("input[type=password],input[type=text]");if(input)window.togglePasswordVisibility(input.id,button);});
      if(button.textContent.toLowerCase().includes("create an account"))button.addEventListener("click",()=>window.switchAuthTab("register"));
      if(button.textContent.trim().toLowerCase()==="sign in")button.addEventListener("click",()=>window.switchAuthTab("signin"));
    });
    if (token()) api("/api/auth/me").then(({ user }) => { setUser(user); goLanding(); }).catch(() => { localStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(TOKEN_KEY); });
  } else if (screen) {
    setLoading("BankWise", "Connecting to your account and loading live data");
    requireSession().then(ok => { if (ok) loadScreen(); });
  }

  async function loadScreen() {
    await renderWorkspace();
  }

  const buttonClass = "rounded-lg bg-[#00513f] px-4 py-2 text-sm font-semibold text-white hover:bg-[#176b55] disabled:cursor-not-allowed disabled:opacity-50";
  const secondaryClass = "rounded-lg border border-[#bec9c3] bg-white px-4 py-2 text-sm font-semibold text-[#00513f] hover:bg-[#f0fcf6] disabled:opacity-50";
  const inputClass = "w-full rounded-lg border border-[#bec9c3] bg-white px-3 py-2 text-sm text-[#131e1a] focus:border-[#00513f] focus:outline-none";
  const moneyRows = (items, valueKey) => items.map(x => `<div class="flex items-center justify-between border-b border-[#e4f1ea] py-2"><span>${esc(x.category || x.month || x.description)}</span><span class="font-semibold">${money(x[valueKey])}</span></div>`).join("");
  function beginPage(title, subtitle, content) {
    const main = document.querySelector("main");
    main.innerHTML = `<div class="mx-auto max-w-[1500px] space-y-5 px-5 py-6 md:px-8"><div><h1 class="text-2xl font-semibold text-[#131e1a]">${esc(title)}</h1><p class="mt-1 text-sm text-[#53615b]">${esc(subtitle)}</p></div><div id="page-error" class="hidden rounded-lg bg-[#ffdad6] p-3 text-sm text-[#93000a]"></div>${content}</div>`;
    const notice = sessionStorage.getItem("bankwise-flash");
    if (notice) { sessionStorage.removeItem("bankwise-flash"); toast(notice); }
    return main;
  }
  function showPageError(error) { const box = document.getElementById("page-error"); if (box) { box.textContent = error.message || "Request failed"; box.classList.remove("hidden"); } displayError(error); }
  function setLoading(title, subtitle) { beginPage(title, subtitle, `<div class="rounded-xl bg-white p-8 text-sm text-gray-600">Loading account data</div>`); }
  function card(label, value, hint = "") { return `<div class="rounded-xl bg-white p-5 shadow-sm"><div class="text-sm text-[#53615b]">${esc(label)}</div><div class="mt-2 text-2xl font-semibold text-[#131e1a]">${esc(value)}</div>${hint ? `<div class="mt-1 text-xs text-[#6f7974]">${esc(hint)}</div>` : ""}</div>`; }
  function table(headers, rows, empty, id = "") { return `<div class="overflow-x-auto rounded-xl bg-white shadow-sm"><table class="w-full min-w-[720px] text-left text-sm"><thead class="bg-[#eaf7f0] text-xs uppercase text-[#53615b]"><tr>${headers.map(h=>`<th class="px-4 py-3">${h}</th>`).join("")}</tr></thead><tbody ${id ? `id="${id}"` : ""} class="divide-y divide-[#e4f1ea]">${rows || `<tr><td class="px-4 py-8 text-center text-gray-500" colspan="${headers.length}">${esc(empty)}</td></tr>`}</tbody></table></div>`; }
  function bindPageNav() {
    document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.go)));
    const bell=[...document.querySelectorAll("header button")].find(b=>b.textContent.includes("notifications"));
    if (bell) bell.onclick=()=>go("anomaly-detection");
  }
  async function renderWorkspace() {
    const names = {overview:["Overview","Your account activity, balances, and recent transactions."],"upload-statement":["Upload statement","Upload a PDF statement to extract and classify transactions."],transactions:["Transactions","Search, filter, and correct transactions processed from your statements."],"financial-insights":["Financial insights","Explore cash flow, categories, and monthly trends calculated from your account."],"anomaly-detection":["Anomaly detection","Review transaction patterns flagged for your attention."],"classification-review":["Classification review","Correct categories and review uncertain classifications."],"reports-&-exports":["Reports and exports","Download reports from the transactions in your account."],settings:["Settings","Choose your BankWise appearance and account preferences."]};
    const [title, subtitle]=names[screen]||names.overview; setLoading(title,subtitle);
    try {
      if (screen==="overview") await renderOverview(title,subtitle);
      else if (screen==="upload-statement") await renderUpload(title,subtitle);
      else if (screen==="transactions") await renderLedger(title,subtitle);
      else if (screen==="financial-insights") await renderFinancialInsights(title,subtitle);
      else if (screen==="anomaly-detection") await renderAnomalyPage(title,subtitle);
      else if (screen==="classification-review") await renderClassificationPage(title,subtitle);
      else if (screen==="reports-&-exports") await renderReportsPage(title,subtitle);
      else await renderSettingsPage(title,subtitle);
      bindPageNav();
    } catch(error) { showPageError(error); }
  }
  async function renderOverview(title,subtitle) {
    const [insights, tx, categoriesData, statements, anomalies] = await Promise.all([api("/api/analytics/overview"),api("/api/transactions?page=1&limit=10"),api("/api/analytics/categories"),api("/api/statements"),api("/api/anomalies?limit=1")]);
    const rows=tx.items.map(x=>`<tr><td class="px-4 py-3">${esc(x.date||"N/A")}</td><td class="px-4 py-3 font-medium">${esc(x.description)}</td><td class="px-4 py-3">${esc(x.final_category)}</td><td class="px-4 py-3 text-right">${money(x.debit||x.credit)}</td><td class="px-4 py-3">${esc(x.review_status||"classified")}</td></tr>`).join("");
    beginPage(title,subtitle,`<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">${card("Credits in",money(insights.total_credits),"All incoming credits, including transfers and refunds")}${card("Debits out",money(insights.gross_expenditure),"All outgoing debit transactions")}${card("Net cash flow",money(insights.net_cash_flow),"Credits in minus debits out")}${card("Transactions",Number(tx.total).toLocaleString())}</div><div class="grid gap-5 xl:grid-cols-3"><section class="space-y-3 xl:col-span-2"><div class="flex items-center justify-between"><h2 class="font-semibold">Recent transactions</h2><button class="${secondaryClass}" data-go="transactions">View all transactions</button></div>${table(["Date","Description","Category","Amount"],rows,"No transactions yet. Upload a statement to begin.")}</section><section class="space-y-4"><div class="rounded-xl bg-white p-5 shadow-sm"><div class="mb-3 flex items-center justify-between"><h2 class="font-semibold">Uploaded statements</h2><button class="${secondaryClass}" data-go="upload-statement">Upload PDF</button></div>${statements.items.slice(0,5).map(s=>`<div class="flex justify-between gap-2 border-b py-2 text-sm"><span>${esc(s.filename)}</span><span>${esc(s.status)}  -  ${s.transaction_count||0}</span></div>`).join("")||`<p class="text-sm text-gray-500">No statements uploaded.</p>`}</div><div class="rounded-xl bg-white p-5 shadow-sm"><div class="mb-3 flex items-center justify-between"><h2 class="font-semibold">Top spending categories</h2><button class="${secondaryClass}" data-go="financial-insights">Insights</button></div>${moneyRows(categoriesData.items.slice(0,5),"total_debit")||`<p class="text-sm text-gray-500">No transactions yet.</p>`}</div><button class="${secondaryClass} w-full" data-go="anomaly-detection">Review ${anomalies.total} flagged anomalies</button></section></div>`);
  }
  async function renderUpload(title,subtitle) {
    const statements=await api("/api/statements");
    const statementRows=items=>items.map(s=>`<tr><td class="px-4 py-3">${esc(s.filename)}</td><td class="px-4 py-3">${esc(s.status)}</td><td class="px-4 py-3">${s.transaction_count||0}</td><td class="px-4 py-3">${s.duplicate_count||0}</td><td class="px-4 py-3">${esc(s.created_at||"N/A")}</td></tr>`).join("");
    const main=beginPage(title,subtitle,`<section class="rounded-xl bg-white p-6 shadow-sm"><form id="statement-form" class="space-y-4"><label class="block text-sm font-medium">Bank statement PDF<input id="statement-file" class="${inputClass} mt-2" type="file" accept=".pdf,application/pdf" required></label><p class="text-xs text-gray-500">Use an unlocked PDF. Scanned PDFs require Tesseract OCR on the backend.</p><button class="${buttonClass}" type="submit">Upload and process</button><span id="upload-progress" class="ml-3 text-sm text-gray-600" aria-live="polite"></span></form><div id="upload-result" class="mt-4 hidden" aria-live="polite"></div></section><section><h2 class="mb-3 font-semibold">Your uploaded statements</h2>${table(["File","Status","New transactions","Duplicates skipped","Uploaded"],statementRows(statements.items),"No statements uploaded.","statement-rows")}</section>`);
    main.querySelector("#statement-form").addEventListener("submit",async e=>{
      e.preventDefault();const form=e.currentTarget,f=main.querySelector("#statement-file").files[0];if(!f)return;
      const btn=form.querySelector("button[type=submit]"),status=main.querySelector("#upload-progress"),resultPanel=main.querySelector("#upload-result");btn.disabled=true;status.textContent="Uploading PDF";resultPanel.classList.add("hidden");resultPanel.innerHTML="";
      try{
        const fd=new FormData();fd.append("file",f);
        const uploaded=await api("/api/statements/upload",{method:"POST",body:fd});
        let result=uploaded,alreadyImported=false;
        if(uploaded.duplicate&&uploaded.status==="completed"){alreadyImported=true;}
        else{status.textContent="Processing statement";result=await api(`/api/statements/${uploaded.statement_id}/process`,{method:"POST",body:{}});}
        const count=Number(result.transaction_count||0),skipped=Number(result.duplicate_count||0);
        status.textContent=alreadyImported?"This statement was already uploaded.":"Uploaded successfully.";
        resultPanel.innerHTML=`<div class="rounded-lg border border-[#9bd5b7] bg-[#f0fcf6] p-4"><h2 class="font-semibold text-[#00513f]">${alreadyImported?"Statement already uploaded":"Uploaded successfully"}</h2><p class="mt-1 text-sm text-gray-700">${count.toLocaleString()} transactions are available in your account. ${alreadyImported?"No new rows were added.":`${skipped.toLocaleString()} exact duplicate rows were skipped.`}</p><div class="mt-3 flex flex-wrap gap-2"><button type="button" id="upload-view-transactions" class="${buttonClass}">View transactions</button><button type="button" id="upload-view-overview" class="${secondaryClass}">View overview</button></div></div>`;
        resultPanel.classList.remove("hidden");
        const history=await api("/api/statements");main.querySelector("#statement-rows").innerHTML=statementRows(history.items)||`<tr><td class="px-4 py-8 text-center text-gray-500" colspan="5">No statements uploaded.</td></tr>`;
        main.querySelector("#upload-view-transactions").onclick=()=>go("transactions");
        main.querySelector("#upload-view-overview").onclick=()=>go("overview");
        form.reset();
      }catch(err){status.textContent="";showPageError(err);}
      finally{btn.disabled=false;}
    });
  }
  async function renderLedger(title,subtitle) {
    const params=new URLSearchParams(location.search);const page=Math.max(1,Number(params.get("page")||1));const filters=new URLSearchParams({page:String(page),limit:"25"});for(const k of ["search","category","date_from","date_to"])if(params.get(k))filters.set(k,params.get(k));
    const [data,filteredTotals]=await Promise.all([api(`/api/transactions?${filters}`),api(`/api/transactions/summary?${filters}`)]);
    const txById=new Map(data.items.map(x=>[x._id,x]));
    const rows=data.items.map(x=>`<tr><td class="px-3 py-3 whitespace-nowrap">${esc(displayDate(x.date))}</td><td class="px-3 py-3">${esc(x.description)}</td><td class="px-3 py-3 text-right">${Number(x.debit||0)>0?money(x.debit):"N/A"}</td><td class="px-3 py-3 text-right">${Number(x.credit||0)>0?money(x.credit):"N/A"}</td><td class="px-3 py-3 text-right">${money(x.balance)}</td><td class="px-3 py-3">${esc(x.final_category||"Other / Uncategorized")}</td><td class="px-3 py-3"><button class="${secondaryClass}" data-edit="${esc(x._id)}">Edit</button></td></tr>`).join("");
    const main=beginPage(title,subtitle,`<form id="tx-filter" class="grid gap-3 rounded-xl bg-white p-4 shadow-sm sm:grid-cols-2 xl:grid-cols-5"><input class="${inputClass}" name="search" placeholder="Search description" value="${esc(params.get("search")||"")}"><select class="${inputClass}" name="category"><option value="">All categories</option>${categories.map(c=>`<option ${params.get("category")===c?"selected":""}>${esc(c)}</option>`).join("")}</select><input class="${inputClass}" type="date" name="date_from" value="${esc(params.get("date_from")||"")}"><input class="${inputClass}" type="date" name="date_to" value="${esc(params.get("date_to")||"")}"><div class="flex gap-2"><button class="${buttonClass}" type="submit">Apply filters</button><button class="${secondaryClass}" id="clear-filters" type="button">Reset</button></div></form><div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">${card("Matching transactions",data.total)}${card("Debits out in selected results",money(filteredTotals.debit_total),"All filtered debit rows")}${card("Credits in selected results",money(filteredTotals.credit_total),"Includes income, refunds, and transfers")}${card("Net cash flow in selected results",money(filteredTotals.net_cash_flow),"Credits in minus debits out")}</div><div class="flex flex-wrap items-center justify-between gap-3"><p class="text-sm text-gray-600">Showing ${data.items.length} of ${data.total} transactions  -  page ${data.page}</p><div class="flex flex-wrap gap-2"><button id="deduplicate" class="${secondaryClass}">Remove exact duplicates</button><button id="reclassify" class="${secondaryClass}">Re-run categorizer</button><button id="export-tx" class="${buttonClass}">Export filtered CSV</button></div></div>${table(["Date","Description","Debit","Credit","Balance","Category","Edit"],rows,"No transactions match your filters.","ledger-rows")}<div class="flex justify-end gap-2"><button id="prev-page" class="${secondaryClass}" ${page<=1?"disabled":""}>Previous</button><button id="next-page" class="${secondaryClass}" ${page*25>=data.total?"disabled":""}>Next</button></div>`);
    main.querySelector("#tx-filter").onsubmit=e=>{e.preventDefault();const p=new URLSearchParams(new FormData(e.currentTarget));p.set("page","1");location.search=p.toString();};
    main.querySelector("#clear-filters").onclick=()=>location.href=location.pathname;
    main.querySelector("#prev-page").onclick=()=>{const p=new URLSearchParams(location.search);p.set("page",String(Math.max(1,page-1)));location.search=p.toString();};
    main.querySelector("#next-page").onclick=()=>{const p=new URLSearchParams(location.search);p.set("page",String(page+1));location.search=p.toString();};
    main.querySelector("#export-tx").onclick=()=>{const q=new URLSearchParams(location.search);download(`/api/export/csv${q.size?`?${q}`:""}`,"bankwise-transactions.csv").catch(showPageError);};
    main.querySelector("#deduplicate").onclick=async e=>{e.currentTarget.disabled=true;try{const r=await api("/api/transactions/deduplicate",{method:"POST",body:{}});toast(`${r.removed_count} exact duplicate transaction rows removed.`);await renderWorkspace();}catch(err){showPageError(err);}finally{e.currentTarget.disabled=false;}};
    main.querySelector("#reclassify").onclick=async e=>{e.currentTarget.disabled=true;try{const r=await api("/api/transactions/reclassify",{method:"POST",body:{}});toast(`${r.processed_count} transactions reprocessed; ${r.changed_count} categories changed.`);await renderWorkspace();}catch(err){showPageError(err);}finally{e.currentTarget.disabled=false;}};
    main.querySelectorAll("[data-edit]").forEach(b=>b.onclick=()=>openTransactionEditor(txById.get(b.dataset.edit),()=>renderWorkspace()));
  }
  async function renderFinancialInsights(title,subtitle) {
    const i=await api("/api/analytics/overview");
    const categoryRows=i.category_breakdown||[];
    const monthlyRows=i.monthly_spending||[];
    const monthlyCategoryRows=i.monthly_category_spending||[];
    const categoryHtml=categoryRows.map(x=>`<tr><td class="px-4 py-3 font-medium">${esc(x.category)}</td><td class="px-4 py-3 text-right">${x.transaction_count}</td><td class="px-4 py-3 text-right">${money(x.total_debit)}</td><td class="px-4 py-3 text-right">${money(x.total_refunds)}</td><td class="px-4 py-3 text-right">${money(x.net_expense)}</td><td class="px-4 py-3 text-right">${money(x.total_income)}</td><td class="px-4 py-3 text-right">${money(x.other_credits)}</td><td class="px-4 py-3 text-right">${Number(x.expense_share_percent).toFixed(1)}%</td><td class="px-4 py-3 text-right">${money(x.average_debit)}</td><td class="px-4 py-3 text-right">${money(x.illustrative_10_percent_reduction)}</td></tr>`).join("");
    const monthHtml=monthlyRows.map(x=>`<tr><td class="px-4 py-3">${esc(x.month)}</td><td class="px-4 py-3 text-right">${x.transaction_count}</td><td class="px-4 py-3 text-right">${money(x.income)}</td><td class="px-4 py-3 text-right">${money(x.other_credits)}</td><td class="px-4 py-3 text-right">${money(x.gross_expenses)}</td><td class="px-4 py-3 text-right">${money(x.refunds)}</td><td class="px-4 py-3 text-right">${money(x.amount)}</td><td class="px-4 py-3 text-right">${money(x.net_cash_flow)}</td><td class="px-4 py-3 text-right">${money(x.net_savings)}</td></tr>`).join("");
    const detailHtml=monthlyCategoryRows.map(x=>`<tr><td class="px-4 py-3">${esc(x.month)}</td><td class="px-4 py-3">${esc(x.category)}</td><td class="px-4 py-3 text-right">${x.transaction_count}</td><td class="px-4 py-3 text-right">${money(x.total_debit)}</td><td class="px-4 py-3 text-right">${money(x.total_refunds)}</td><td class="px-4 py-3 text-right">${money(x.net_expense)}</td><td class="px-4 py-3 text-right">${money(x.total_income)}</td><td class="px-4 py-3 text-right">${money(x.other_credits)}</td></tr>`).join("");
    const main=beginPage(title,subtitle,`<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">${card("Recognized income",money(i.total_income),"Salary and explicitly identified income")}${card("Identified refunds",money(i.total_refunds),"Credits matched as refunds or reversals")}${card("Other credits",money(i.total_other_credits),"Credits not identified as income or refunds")}${card("Net expenses",money(i.total_expenditure),"Gross debits less identified refunds")}${card("Estimated net savings",money(i.net_savings),"Recognized income less net expenses")}${card("Savings rate",i.savings_rate_percent==null?"N/A":`${i.savings_rate_percent}%`,"Estimated net savings divided by recognized income")}${card("Net cash flow",money(i.net_cash_flow),"All credits less all debits, including transfers")}</div><section class="rounded-xl bg-white p-5 shadow-sm"><div class="mb-3 flex flex-wrap items-center justify-between gap-3"><div><h2 class="font-semibold">Every spending category</h2><p class="mt-1 text-xs text-gray-500">Credits are separated by meaning. Refunds and other credits are not counted as earnings. 10% reduction figures are illustrative scenarios.</p><details class="mt-2 text-xs text-gray-600"><summary class="cursor-pointer font-medium">What these credit columns mean</summary><p class="mt-2"><strong>Recognized income</strong> includes credits categorized as Salary &amp; Income or descriptions that clearly identify salary, payroll, pension, dividends, interest, rental, or business income. <strong>Refunds</strong> are credits whose descriptions identify a refund, reversal, chargeback, cashback, or merchant credit; they reduce net expenses. <strong>Other credits</strong> are incoming transfers or credits without a clear income/refund label. A zero means no uploaded transaction matched that definition; BankWise does not invent values.</p></details></div><button id="export-insights" class="${secondaryClass}">Export full insights CSV</button></div>${table(["Category","Transactions","Gross expenses","Refunds","Net expense","Recognized income","Other credits","Expense share","Average debit","10% reduction scenario"],categoryHtml,"No category data yet.")}</section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Monthly totals</h2>${table(["Month","Transactions","Recognized income","Other credits","Gross expenses","Refunds","Net expenses","Net cash flow","Estimated savings"],monthHtml,"Monthly trends appear once dated transactions are available.")}</section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Category expenses by month</h2>${table(["Month","Category","Transactions","Gross expenses","Refunds","Net expense","Recognized income","Other credits"],detailHtml,"No monthly category data yet.")}</section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Recurring payments</h2>${(i.insights.find(x=>x.type==="recurring_payments")?.items||[]).map(x=>`<div class="flex flex-wrap justify-between gap-2 border-b py-3"><span>${esc(x.description)} <span class="text-xs text-gray-500">${x.occurrences} payments across ${x.months.length} months</span></span><span>${money(x.average_amount)} average</span></div>`).join("")||`<p class="text-sm text-gray-500">Recurring payments will appear when the same merchant has debits in multiple months.</p>`}</section>`);
    main.querySelector("#export-insights").onclick=()=>{
      const quote=value=>`"${String(value??"").replaceAll('"','""')}"`;
      const lines=["section,period,category,transaction_count,gross_expenses,refunds,net_expense,recognized_income,other_credits,net_cash_flow,expense_share_percent,average_debit,illustrative_10_percent_reduction"];
      for(const x of categoryRows) lines.push(["category","",x.category,x.transaction_count,x.total_debit,x.total_refunds,x.net_expense,x.total_income,x.other_credits,x.net_cash_flow,x.expense_share_percent,x.average_debit,x.illustrative_10_percent_reduction].map(quote).join(","));
      for(const x of monthlyRows) lines.push(["month",x.month,"",x.transaction_count,x.gross_expenses,x.refunds,x.amount,x.income,x.other_credits,x.net_cash_flow,"","",""].map(quote).join(","));
      for(const x of monthlyCategoryRows) lines.push(["monthly_category",x.month,x.category,x.transaction_count,x.total_debit,x.total_refunds,x.net_expense,x.total_income,x.other_credits,x.total_credit-x.total_debit,"","",""].map(quote).join(","));
      const url=URL.createObjectURL(new Blob([lines.join("\r\n")],{type:"text/csv"}));const a=document.createElement("a");a.href=url;a.download="bankwise-financial-insights.csv";a.click();URL.revokeObjectURL(url);
    };
  }
  async function renderAnomalyPage(title,subtitle) {
    const data=await api("/api/anomalies?limit=100");
    const rows=data.items.map(a=>{const x=a.transaction||{};return `<tr><td class="px-4 py-3">${esc(displayDate(x.date))}</td><td class="px-4 py-3">${esc(x.description||"Transaction")}</td><td class="px-4 py-3 text-right">${Number(x.debit||0)>0?money(x.debit):money(x.credit)}</td><td class="px-4 py-3">${esc(x.final_category||"N/A")}</td><td class="px-4 py-3">${esc(a.reason)}</td><td class="px-4 py-3">${esc(a.method)}</td><td class="px-4 py-3">${esc(a.severity)}</td><td class="px-4 py-3"><span class="rounded-full px-2 py-1 text-xs ${a.review_status==="reviewed"?"bg-[#bfedd4] text-[#00513f]":"bg-[#fff0cf] text-[#6d4d00]"}">${esc(a.review_status)}</span></td><td class="px-4 py-3">${a.review_status==="reviewed"?"<span class=\"text-sm text-gray-500\">Reviewed</span>":`<button class="${secondaryClass}" data-review="${esc(a._id)}">Mark reviewed</button>`} <button class="${secondaryClass}" data-dismiss="${esc(a._id)}">Dismiss</button></td></tr>`;}).join("");
    const main=beginPage(title,subtitle,`<div class="flex flex-wrap items-center justify-between gap-3"><p>${data.total} flagged records  -  reviewed items stay visible for audit.</p><button id="rescan-anomalies" class="${buttonClass}">Re-scan ledger</button></div>${table(["Date","Transaction","Amount","Category","Reason","Detection","Severity","Status","Actions"],rows,"No matching anomalies. Re-scan evaluates transaction size, duplicates, and unusual frequency against the current ledger.")}`);
    main.querySelector("#rescan-anomalies").onclick=async e=>{e.currentTarget.disabled=true;try{const result=await api("/api/anomalies/scan",{method:"POST",body:{}});toast(`Scanned ${result.scanned_transactions} transactions: ${result.flagged_count} supported flags, ${result.created_count} new, ${result.stale_count} outdated flags cleared.`);await renderWorkspace();}catch(err){showPageError(err);}finally{e.currentTarget.disabled=false;}};
    main.querySelectorAll("[data-review]").forEach(b=>b.onclick=async()=>{b.disabled=true;try{await api(`/api/anomalies/${b.dataset.review}/review`,{method:"PUT",body:{status:"reviewed"}});toast("Anomaly marked reviewed and retained in the audit list.");await renderWorkspace();}catch(err){showPageError(err);}});
    main.querySelectorAll("[data-dismiss]").forEach(b=>b.onclick=async()=>{b.disabled=true;try{await api(`/api/anomalies/${b.dataset.dismiss}`,{method:"DELETE"});toast("Anomaly dismissed and removed from the active list.");await renderWorkspace();}catch(err){showPageError(err);}});
  }
  async function renderClassificationPage(title,subtitle) {
    const params=new URLSearchParams(location.search);const page=Math.max(1,Number(params.get("page")||1));
    const [queueResult,summaryResult,metricsResult]=await Promise.allSettled([api(`/api/classification/review-queue?page=${page}&limit=25`),api("/api/classification/summary"),api("/api/classification/metrics")]);
    if(queueResult.status==="rejected")throw queueResult.reason;
    if(summaryResult.status==="rejected")throw summaryResult.reason;
    const queue=queueResult.value,summary=summaryResult.value,metrics=metricsResult.status==="fulfilled"?metricsResult.value:{metrics:null};const items=Array.isArray(queue.items)?queue.items:[];
    const report=metrics.metrics?.logistic_regression||metrics.metrics||{};const accuracy=report.accuracy!=null&&Number.isFinite(Number(report.accuracy))?`${(Number(report.accuracy)*100).toFixed(1)}%`:"Not available";const weightedF1=report.weighted_f1!=null&&Number.isFinite(Number(report.weighted_f1))?`${(Number(report.weighted_f1)*100).toFixed(1)}%`:"Not available";
    const rows=items.map(x=>{
      const warnings=Array.isArray(x.validation_warnings)?x.validation_warnings:(typeof x.validation_warnings==="string"&&x.validation_warnings.trim()?[x.validation_warnings.trim()]:[]);
      const transactionLabel=`${x.description||"Transaction"} on ${displayDate(x.date)}`;
      const side=Number(x.debit||0)>0?"debit":"credit",amount=money(Number(x.debit||x.credit||0));
      const reason=warnings.some(w=>/amount order assumed|without dr\/cr marker|direction is uncertain/i.test(String(w)))
        ?`The statement did not clearly label the amount direction. BankWise read ${amount} as a ${side} for ${transactionLabel}; verify it against the original statement.`
        :warnings.length?`${warnings.join("; ")} Transaction: ${transactionLabel} (${amount}).`
        :x.method==="ml"?`The model assigned ${x.predicted_category||x.final_category} with a ${(Number(x.confidence||0)*100).toFixed(1)}% score; review this prediction.`
        :`This transaction was flagged for review. Check its category and statement details: ${transactionLabel} (${amount}).`;
      const signal=x.method==="rule"?`<span title="A deterministic keyword rule matched; this is not a probability score.">Rule match</span>`
        :x.method==="ml"&&x.confidence!=null?`${(Number(x.confidence)*100).toFixed(1)}% ML score`
        :x.method==="fallback"?"No trained model":"N/A";
      return `<tr><td class="px-4 py-3">${esc(displayDate(x.date))}</td><td class="px-4 py-3">${esc(x.description)}</td><td class="px-4 py-3 text-right">${money(x.debit||x.credit)}</td><td class="px-4 py-3">${esc(x.predicted_category||x.final_category)}</td><td class="px-4 py-3">${signal}</td><td class="px-4 py-3">${esc(reason)}</td><td class="px-4 py-3"><select class="${inputClass}" data-class-cat="${esc(x._id)}">${categories.map(c=>`<option ${c===x.final_category?"selected":""}>${esc(c)}</option>`).join("")}</select></td><td class="px-4 py-3"><div class="flex flex-col gap-2"><button class="${buttonClass}" data-class-save="${esc(x._id)}">Save category</button><button class="${secondaryClass}" data-class-edit="${esc(x._id)}">Edit transaction details</button></div></td></tr>`;
    }).join("");
    const categoryRows=(summary.category_counts||[]).map(x=>`<tr><td class="px-4 py-3">${esc(x.category)}</td><td class="px-4 py-3 text-right">${Number(x.count).toLocaleString()}</td><td class="px-4 py-3 text-right">${summary.total_transactions?`${(x.count/summary.total_transactions*100).toFixed(1)}%`:"0.0%"}</td></tr>`).join("");
    const main=beginPage(title,subtitle,`<div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">${card("Processed transactions",Number(summary.total_transactions).toLocaleString())}${card("Classified without review",Number(summary.auto_classified).toLocaleString())}${card("Need review",Number(summary.review_required).toLocaleString())}${card("Extraction warnings",Number(summary.extraction_warnings).toLocaleString())}${card("Average ML score",summary.average_confidence==null?"N/A":`${(summary.average_confidence*100).toFixed(1)}%`)}</div><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-2 font-semibold">Classifier validation</h2><div class="grid gap-4 sm:grid-cols-2">${card("Validation accuracy",accuracy)}${card("Weighted F1",weightedF1)}</div><p class="mt-3 text-sm text-gray-600"> ${Number(summary.corrected||0)} transaction categories have user corrections. </p></section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Processed records by category</h2>${table(["Category","Records","Share of processed records"],categoryRows,"No processed transactions yet.")}</section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Transactions requiring attention</h2><p class="mb-3 text-sm text-gray-600">Uploaded transactions flagged by classification confidence or extraction warnings. Rule-based categories appear as “Rule match”; the label is not a probability. Showing ${items.length} of ${queue.total} flagged transactions.</p>${table(["Date","Description","Amount","Predicted category","Classifier signal","Review reason","Correct category","Actions"],rows,"No uploaded transactions need review.")}<div class="mt-3 flex justify-end gap-2"><button id="review-prev" class="${secondaryClass}" ${page<=1?"disabled":""}>Previous</button><button id="review-next" class="${secondaryClass}" ${page*25>=queue.total?"disabled":""}>Next</button></div></section>`);
    main.querySelector("#review-prev").onclick=()=>{const q=new URLSearchParams(location.search);q.set("page",String(page-1));location.search=q.toString();};
    main.querySelector("#review-next").onclick=()=>{const q=new URLSearchParams(location.search);q.set("page",String(page+1));location.search=q.toString();};
    main.querySelectorAll("[data-class-save]").forEach(b=>b.onclick=async()=>{const id=b.dataset.classSave,value=main.querySelector(`[data-class-cat="${id}"]`).value;try{await api(`/api/transactions/${id}`,{method:"PUT",body:{category:value}});toast("Correction saved for feedback review.");await renderWorkspace();}catch(err){showPageError(err);}});
    main.querySelectorAll("[data-class-edit]").forEach(b=>b.onclick=()=>openTransactionEditor(items.find(x=>x._id===b.dataset.classEdit),()=>renderWorkspace()));
  }
  async function renderReportsPage(title,subtitle) {
    const [statements,tx]=await Promise.all([api("/api/statements"),api("/api/transactions?page=1&limit=1")]);
    const main=beginPage(title,subtitle,`<div class="grid gap-4 md:grid-cols-3">${card("Transactions in account",tx.total)}${card("Uploaded statements",statements.items.length)}${card("Exports","CSV and Excel")}</div><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Export transactions</h2><form id="report-filter" class="grid gap-3 md:grid-cols-4"><select name="category" class="${inputClass}"><option value="">All categories</option>${categories.map(c=>`<option>${esc(c)}</option>`).join("")}</select><input name="date_from" class="${inputClass}" type="date"><input name="date_to" class="${inputClass}" type="date"><div class="flex gap-2"><button class="${buttonClass}" data-format="csv" type="button">Download CSV</button><button class="${secondaryClass}" data-format="excel" type="button">Download Excel</button></div></form><p class="mt-2 text-xs text-gray-500">Downloads include all matching transactions, up to the backend export limit.</p></section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-3 font-semibold">Statement history</h2>${table(["Filename","Status","Transactions","Created"],statements.items.map(s=>`<tr><td class="px-4 py-3">${esc(s.filename)}</td><td class="px-4 py-3">${esc(s.status)}</td><td class="px-4 py-3">${s.transaction_count||0}</td><td class="px-4 py-3">${esc(s.created_at||"N/A")}</td></tr>`).join(""),"No statements uploaded.")}</section>`);
    main.querySelectorAll("[data-format]").forEach(b=>b.onclick=()=>{const q=new URLSearchParams(new FormData(main.querySelector("#report-filter")));download(`/api/export/${b.dataset.format}${q.size?`?${q}`:""}`,b.dataset.format==="csv"?"bankwise-transactions.csv":"bankwise-report.xlsx").catch(showPageError);});
    const resetSection=document.createElement("section");resetSection.className="rounded-xl border border-red-200 bg-white p-5 shadow-sm";resetSection.innerHTML=`<h2 class="font-semibold text-red-800">Clear imported data</h2><p class="mt-1 text-sm text-gray-600">Remove this account's uploaded statements, extracted transactions, anomaly history, and processing history. Your account and profile remain.</p><button id="show-data-reset" type="button" class="${secondaryClass} mt-3 border-red-300 text-red-800">Review reset</button><div id="data-reset-confirm" class="mt-4 hidden rounded-lg bg-red-50 p-4"><p class="text-sm text-red-900">This cannot be undone. Type <strong>CLEAR</strong> to confirm. Any statement still processing must finish first.</p><div class="mt-3 flex flex-wrap gap-2"><input id="data-reset-word" class="${inputClass} max-w-48" aria-label="Type CLEAR to confirm" autocomplete="off"><button id="confirm-data-reset" class="${buttonClass}" disabled>Clear account data</button><button id="cancel-data-reset" class="${secondaryClass}">Cancel</button></div><p id="data-reset-status" class="mt-2 text-sm" aria-live="polite"></p></div>`;main.appendChild(resetSection);
    const panel=resetSection.querySelector("#data-reset-confirm"),word=resetSection.querySelector("#data-reset-word"),confirm=resetSection.querySelector("#confirm-data-reset"),status=resetSection.querySelector("#data-reset-status");
    resetSection.querySelector("#show-data-reset").onclick=()=>{panel.classList.remove("hidden");word.focus();};
    word.oninput=()=>{confirm.disabled=word.value!=="CLEAR";};
    resetSection.querySelector("#cancel-data-reset").onclick=()=>{word.value="";confirm.disabled=true;status.textContent="";panel.classList.add("hidden");};
    confirm.onclick=async()=>{confirm.disabled=true;status.textContent="Clearing imported records";try{const result=await api("/api/data/clear",{method:"DELETE"});sessionStorage.removeItem("bankwise-flash");sessionStorage.removeItem("bankwise-dedupe-route-notice");const deleted=result.transactions_deleted+result.statements_deleted+result.anomalies_deleted+result.dismissals_deleted+result.feedback_deleted+result.processing_logs_deleted;toast(`Reset complete. Removed ${deleted.toLocaleString()} account records and ${result.files_deleted} uploaded files.`);await renderWorkspace();}catch(err){status.textContent=err.message||"Reset failed. Your data was not cleared.";confirm.disabled=word.value!=="CLEAR";}};
  }
  async function renderSettingsPage(title,subtitle) {
    const theme=localStorage.getItem(THEME_KEY)||"light", density=localStorage.getItem(DENSITY_KEY)||"comfortable", landing=localStorage.getItem(LANDING_KEY)||"overview";
    const main=beginPage(title,subtitle,`<section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-1 font-semibold">Appearance</h2><p class="mb-4 text-sm text-gray-500">Choose how BankWise looks on this device.</p><div class="grid gap-4 sm:grid-cols-2"><label class="text-sm">Theme<select id="theme-choice" class="${inputClass} mt-1"><option value="light" ${theme==="light"?"selected":""}>Light</option><option value="dark" ${theme==="dark"?"selected":""}>Dark</option><option value="system" ${theme==="system"?"selected":""}>Match device</option></select></label><label class="text-sm">Layout density<select id="density-choice" class="${inputClass} mt-1"><option value="comfortable" ${density==="comfortable"?"selected":""}>Comfortable</option><option value="compact" ${density==="compact"?"selected":""}>Compact</option></select></label><label class="text-sm">Open after sign in<select id="landing-choice" class="${inputClass} mt-1"><option value="overview" ${landing==="overview"?"selected":""}>Overview</option><option value="transactions" ${landing==="transactions"?"selected":""}>Transactions</option><option value="financial-insights" ${landing==="financial-insights"?"selected":""}>Financial insights</option></select></label></div></section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-1 font-semibold">Profile</h2><p class="mb-4 text-sm text-gray-500">Update your name and optional contact details.</p><button id="settings-profile" class="${buttonClass}">Open profile details</button></section><section class="rounded-xl bg-white p-5 shadow-sm"><h2 class="mb-1 font-semibold">Account</h2><p class="mb-4 text-sm text-gray-500">Sign out of this BankWise session.</p><button id="settings-logout" class="${secondaryClass}">Sign out</button></section><div class="flex justify-end"><button id="reset-settings" class="${secondaryClass}">Reset page preferences</button></div>`);
    main.querySelector("#theme-choice").onchange=e=>{localStorage.setItem(THEME_KEY,e.target.value);applyPreferences();toast("Theme preference saved.");};
    main.querySelector("#density-choice").onchange=e=>{localStorage.setItem(DENSITY_KEY,e.target.value);applyPreferences();toast("Layout density saved.");};
    main.querySelector("#landing-choice").onchange=e=>{localStorage.setItem(LANDING_KEY,e.target.value);toast("Sign-in page preference saved.");};
    main.querySelector("#settings-profile").onclick=openProfile;
    main.querySelector("#settings-logout").onclick=logout;
    main.querySelector("#reset-settings").onclick=()=>{localStorage.removeItem(THEME_KEY);localStorage.removeItem(DENSITY_KEY);localStorage.removeItem(LANDING_KEY);applyPreferences();toast("Page preferences reset.");renderWorkspace();};
  }

})();


