/* Study Quarter tracker. Plain JS, no build step.
 * Shared plan: plan.js (window.PLAN). Each person gets their own copy of the
 * plan plus their own checkmarks, notes and research cases, saved in this
 * browser's localStorage under STORAGE_KEY. Use Settings > Export to back up
 * or move to another device.
 */
(() => {
  "use strict";
  const PLAN = window.PLAN;
  const STORAGE_KEY = "studyQuarter.v1";
  const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const TYPE_LABEL = { kalamna: "Kalamna", study: "Study", project: "Project", book: "Book", video: "Video", leetcode: "LeetCode", research: "Research", review: "Review" };
  const CASE_FIELDS = [
    ["what", "What is it?", "Exact meaning in your own words"],
    ["why", "Why do we care?", "Business or technical impact"],
    ["measure", "How do we measure it?", "Formula, experiment or benchmark"],
    ["good", "What does good look like?", "Target, threshold, SLA"],
    ["bad", "What does bad look like?", "Failure condition"],
    ["detect", "How do we detect it in production?", "Monitoring, alerting"],
    ["improve", "What can improve it?", "Interventions and trade-offs"],
    ["example", "Concrete example", "One realistic scenario"],
    ["answer", "My answer to the final question", "Recommendation and why"],
    ["questions", "Open questions", "At least 3 questions without an obvious answer"],
  ];

  // ---------- storage ----------
  const clone = (o) => JSON.parse(JSON.stringify(o));
  let store = load();
  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch { return {}; }
  }
  function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(store)); }
    catch { toast("Not saved: this browser blocked storage. Export a backup from Settings."); }
  }
  function freshProfile() {
    return { planVersion: PLAN.version, days: clone(PLAN.days), done: {}, notes: {}, dayNotes: {}, cases: {}, topics: {}, materials: [], hideKalamna: false };
  }
  store.profiles = store.profiles || {};
  PLAN.profiles.forEach((p) => { if (!store.profiles[p.id]) store.profiles[p.id] = freshProfile(); });
  if (!store.active || !store.profiles[store.active]) store.active = PLAN.profiles[0].id;
  save();

  const me = () => store.profiles[store.active];
  const ui = { view: "today", week: null, openNote: null, scrollTo: null };

  // ---------- dates ----------
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const parse = (s) => { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); };
  const todayIso = () => iso(new Date());
  const pretty = (s) => { const d = parse(s); return `${DAY_NAMES[d.getDay()]}, ${MONTHS[d.getMonth()]} ${d.getDate()}`; };
  const isWeekend = (s) => PLAN.weekend.map((w) => (w + 1) % 7).includes(parse(s).getDay()); // python Mon=0 -> js Sun=0
  const clampDate = (s) => (s < PLAN.start ? PLAN.start : s > PLAN.end ? PLAN.end : s);

  // ---------- helpers ----------
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const safeUrl = (u) => (/^https?:\/\//i.test(u || "") ? u : "");
  const fmtH = (h) => { const n = Math.round(h * 100) / 100; return n < 1 ? `${Math.round(n * 60)} min` : `${n}h`; };
  const visible = (t) => !(me().hideKalamna && t.type === "kalamna");
  const dayByDate = (date) => me().days.find((d) => d.date === date);
  function findTask(id) {
    for (const day of me().days) {
      const i = day.tasks.findIndex((t) => t.id === id);
      if (i >= 0) return { day, i, task: day.tasks[i] };
    }
    return null;
  }
  function dayProgress(day) {
    const ts = day.tasks.filter(visible);
    const done = ts.filter((t) => me().done[t.id]).length;
    return { done, total: ts.length, ratio: ts.length ? done / ts.length : 0 };
  }
  function weekProgress(n) {
    let done = 0, total = 0;
    me().days.filter((d) => d.week === n).forEach((d) => { const p = dayProgress(d); done += p.done; total += p.total; });
    return total ? done / total : 0;
  }
  const weekOf = (date) => (dayByDate(clampDate(date)) || me().days[0]).week;

  let toastTimer;
  function toast(msg) {
    const el = document.getElementById("toast");
    el.textContent = msg; el.classList.add("show");
    clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  }

  // ---------- header ----------
  function renderPeople() {
    document.getElementById("people").innerHTML = PLAN.profiles.map((p) =>
      `<button role="tab" data-person="${p.id}" aria-selected="${p.id === store.active}">${esc(p.name)}</button>`).join("");
  }

  function renderGrid() {
    const days = me().days, today = todayIso();
    const first = parse(PLAN.start), lead = first.getDay();
    const cells = [];
    for (let k = 0; k < 7; k++) cells.push(`<span class="rowlabel" style="grid-row:${k + 2};grid-column:1">${k % 2 ? DAY_NAMES[k] : ""}</span>`);
    let col = 2;
    const monthSeen = new Set();
    for (let k = 0; k < lead; k++) cells.push(`<span class="cell pad" style="grid-row:${k + 2};grid-column:${col}"></span>`);
    days.forEach((d, idx) => {
      const dow = (lead + idx) % 7;
      col = 2 + Math.floor((lead + idx) / 7);
      const dt = parse(d.date), m = dt.getMonth();
      if (!monthSeen.has(m)) { monthSeen.add(m); cells.push(`<span class="month" style="grid-row:1;grid-column:${col}">${MONTHS[m]}</span>`); }
      const p = dayProgress(d);
      const lvl = p.ratio === 0 ? 0 : p.ratio < 0.34 ? 1 : p.ratio < 0.67 ? 2 : p.ratio < 1 ? 3 : 4;
      const cls = ["cell", d.date > today && p.done === 0 ? "future" : "", d.date === today ? "today" : "", ""].join(" ");
      cells.push(`<button class="${cls}" data-lvl="${lvl}" data-goto="${d.date}" style="grid-row:${dow + 2};grid-column:${col}"
        title="${pretty(d.date)} · Week ${d.week} · ${p.done}/${p.total} done" aria-label="${pretty(d.date)}, week ${d.week}, ${p.done} of ${p.total} done"></button>`);
    });
    document.getElementById("grid").innerHTML = cells.join("");

    let done = 0, total = 0, kDone = 0, kTotal = 0;
    days.forEach((d) => d.tasks.forEach((t) => {
      if (t.type === "kalamna") { kTotal++; if (me().done[t.id]) kDone++; return; }
      total++; if (me().done[t.id]) done++;
    }));
    const t = todayIso();
    const dayNum = t < PLAN.start ? 0 : Math.min(days.length, days.findIndex((d) => d.date === t) + 1 || days.length);
    document.getElementById("stats").innerHTML = `
      <div class="stat"><b>${total ? Math.round((done / total) * 100) : 0}%</b><span>${done} of ${total} tasks done</span></div>
      <div class="stat"><b>${dayNum}<small style="font-size:1rem"> / ${days.length}</small></b><span>${t < PLAN.start ? "days until start: " + Math.round((parse(PLAN.start) - parse(t)) / 864e5) : "day of the quarter"}</span></div>
      ${me().hideKalamna ? "" : `<div class="stat"><b>${kDone}</b><span>Kalamna blocks done</span></div>`}`;
  }

  function renderNav() {
    document.querySelectorAll("#views button").forEach((b) => b.setAttribute("aria-current", b.dataset.view === ui.view ? "page" : "false"));
  }

  function renderBanner() {
    const el = document.getElementById("banner");
    el.innerHTML = me().planVersion !== PLAN.version ? `<div class="banner"><p>The shared plan was updated. Load it to get the new tasks. Your checkmarks and notes stay; tasks you added or edited yourself will be replaced.</p>
      <button class="btn primary" data-action="load-new-plan">Load updated plan</button></div>` : "";
  }

  // ---------- tasks & days ----------
  function taskHtml(t, { showDate = false, date = "" } = {}) {
    const done = !!me().done[t.id], note = me().notes[t.id] || "", open = ui.openNote === t.id;
    const link = safeUrl(t.link);
    const mats = (me().materials || []).filter((m) => m.taskId === t.id);
    return `<li class="task ${done ? "done" : ""}" data-id="${t.id}">
      <input type="checkbox" id="c-${t.id}" data-action="toggle" ${done ? "checked" : ""}>
      <label class="task-title" for="c-${t.id}">${esc(t.title)}</label>
      <div class="task-meta"><span class="type type-${esc(t.type)}">${esc(TYPE_LABEL[t.type] || t.type)}</span>${t.hours ? `<span>${fmtH(t.hours)}</span>` : ""}
        ${showDate ? `<span>${pretty(date)}</span>` : ""}${link ? `<a href="${esc(link)}" target="_blank" rel="noopener">Open link</a>` : ""}
        ${mats.map((m) => safeUrl(m.url) ? `<a href="${esc(m.url)}" target="_blank" rel="noopener">Material: ${esc(m.title)}</a>` : `<span>Material: ${esc(m.title)}</span>`).join("")}</div>
      ${t.details ? `<p class="task-details">${esc(t.details)}</p>` : ""}
      ${open ? `<div class="task-note"><textarea rows="3" data-note="${t.id}" aria-label="Note for ${esc(t.title)}" placeholder="What you learned, links, what's left…">${esc(note)}</textarea></div>`
             : note ? `<p class="note-preview">${esc(note)}</p>` : ""}
      <div class="task-actions">
        <button class="icon-btn" data-action="note" aria-expanded="${open}">${note ? "Note ✎" : "Note"}</button>
        <button class="icon-btn" data-action="next-day" title="Move to the next day">Move</button>
        <button class="icon-btn" data-action="edit">Edit</button>
      </div>
    </li>`;
  }

  function dayHtml(day) {
    const today = todayIso();
    const tasks = day.tasks.filter(visible);
    const study = Math.round(tasks.filter((t) => t.type !== "kalamna" && !/^(Beyond the Basics|System Design playlist), video/.test(t.title)).reduce((s, t) => s + (+t.hours || 0), 0) * 4) / 4;
    const p = dayProgress(day);
    return `<article class="day ${day.date === today ? "is-today" : ""}" id="day-${day.date}">
      <div class="day-head"><h3>${pretty(day.date)}${isWeekend(day.date) ? '<span class="tag">Weekend</span>' : ""}${day.date === today ? '<span class="tag">Today</span>' : ""}</h3>
        <span class="day-meta">Week ${day.week} · ${fmtH(study)} study · ${p.done}/${p.total} done</span></div>
      <ul class="tasks">${tasks.map((t) => taskHtml(t)).join("") || '<li class="muted" style="padding:8px 0">No tasks. Add one, or enjoy the rest.</li>'}</ul>
      <div class="day-foot">
        <button class="btn" data-action="add" data-date="${day.date}">Add task</button>
        <details class="day-note" ${me().dayNotes[day.date] ? "open" : ""}><summary>Day notes</summary>
          <textarea rows="2" data-daynote="${day.date}" aria-label="Notes for ${pretty(day.date)}">${esc(me().dayNotes[day.date] || "")}</textarea></details>
      </div>
    </article>`;
  }

  // ---------- views ----------
  function viewToday() {
    const t = todayIso(), date = clampDate(t), day = dayByDate(date);
    let intro = "";
    if (t < PLAN.start) intro = `<p class="sub">The plan starts on ${pretty(PLAN.start)}. Here is day one.</p>`;
    else if (t > PLAN.end) intro = `<p class="sub">The quarter is over. Here is the last day; the grid above shows everything.</p>`;
    const overdue = [];
    if (t >= PLAN.start) me().days.forEach((d) => { if (d.date < date) d.tasks.forEach((x) => { if (!me().done[x.id] && x.type !== "kalamna" && visible(x)) overdue.push([d.date, x]); }); });
    const w = PLAN.weeks.find((x) => x.n === day.week);
    return `<div class="col"><h2>${t < PLAN.start || t > PLAN.end ? pretty(date) : "Today"}</h2>
      <p class="sub">Week ${w.n}: ${esc(w.title)}</p>${intro}
      ${dayHtml(day)}
      ${overdue.length ? `<section class="day overdue"><div class="day-head"><h3>Unfinished from earlier days</h3>
        <button class="btn" data-action="move-overdue" data-date="${date}">Move all ${overdue.length} to today</button></div>
        <ul class="tasks overdue-list">${overdue.slice(0, 40).map(([d, x]) => taskHtml(x, { showDate: true, date: d })).join("")}</ul>
        ${overdue.length > 40 ? `<p class="muted">Showing 40 of ${overdue.length}.</p>` : ""}</section>` : ""}</div>`;
  }

  function viewWeek() {
    if (ui.week == null) ui.week = weekOf(todayIso());
    const w = PLAN.weeks.find((x) => x.n === ui.week);
    const chips = PLAN.weeks.map((x) => `<button data-week="${x.n}" aria-pressed="${x.n === ui.week}" title="${esc(x.title)}">W${x.n}<span class="pct">${Math.round(weekProgress(x.n) * 100)}%</span></button>`).join("");
    const days = me().days.filter((d) => d.week === ui.week);
    const pct = Math.round(weekProgress(ui.week) * 100);
    return `<div class="weeks" aria-label="Choose a week">${chips}</div>
      <h2>Week ${w.n}: ${esc(w.title)}</h2>
      <p class="sub">${pretty(w.start)} to ${pretty(w.end)} · ${pct}% done</p>
      <div class="bar" aria-hidden="true"><i style="width:${pct}%"></i></div>
      ${weekMaterialsHtml(ui.week)}
      ${days.map(dayHtml).join("")}`;
  }

  function viewCases() {
    const groups = [["In this plan", PLAN.cases.filter((c) => c.week)], ["Next plan (multi-agent, memory, production)", PLAN.cases.filter((c) => !c.week)]];
    return `<div class="col"><h2>Research cases</h2>
      <p class="sub">One page per case from the BARQ guides. Answer the chain: problem, solutions, trade-offs, measurement, recommendation. "Copy for Notion" copies it as Markdown.</p>
      ${groups.map(([name, cs]) => `<h3 style="margin:22px 0 10px">${name}</h3>` + cs.map((c) => {
        const data = me().cases[c.id] || {};
        const filled = CASE_FIELDS.filter(([k]) => (data[k] || "").trim()).length;
        return `<details class="case" data-case="${c.id}"><summary><h3>${esc(c.title)}</h3>
          <span class="day-meta">${esc(c.source)}${c.week ? ` · Week ${c.week}` : ""} · ${filled}/${CASE_FIELDS.length} answered</span></summary>
          <p class="case-q"><b>Final question:</b> ${esc(c.question)}</p>
          ${CASE_FIELDS.map(([k, label, hint]) => `<label for="cf-${c.id}-${k}">${label} <span>${hint}</span></label>
            <textarea id="cf-${c.id}-${k}" rows="3" data-casefield="${c.id}.${k}">${esc(data[k] || "")}</textarea>`).join("")}
          <div class="case-foot"><button class="btn" data-action="copy-case" data-case-id="${c.id}">Copy for Notion</button><span class="muted">Saves as you type.</span></div>
        </details>`;
      }).join("")).join("")}</div>`;
  }

  function viewData() {
    const name = PLAN.profiles.find((p) => p.id === store.active).name;
    return `<div class="col"><h2>Settings &amp; backup</h2><p class="sub">These apply to ${esc(name)}'s plan only.</p>
      <section class="setting"><h3>Kalamna blocks</h3><p>Hide the daily 2h Kalamna block if it isn't part of this person's plan.</p>
        <label class="row"><input type="checkbox" data-action="toggle-kalamna" ${me().hideKalamna ? "checked" : ""}> Hide Kalamna blocks</label></section>
      <section class="setting"><h3>Backup and other devices</h3>
        <p>Progress is saved in this browser only. Export a backup regularly, and import it to continue on another phone or laptop.</p>
        <div class="row"><button class="btn primary" data-action="export">Export my progress</button>
        <label class="btn" style="cursor:pointer">Import a backup<input type="file" accept="application/json" data-action="import" hidden></label></div></section>
      <section class="setting"><h3>Reset</h3><p>Reload the shared plan keeps checkmarks and notes but drops your own edits. Erase starts ${esc(name)} from zero.</p>
        <div class="row"><button class="btn" data-action="reload-plan">Reload shared plan</button><button class="btn danger" data-action="erase">Erase ${esc(name)}'s progress</button></div></section>
      <p class="muted">Shared plan version ${esc(PLAN.version)}.</p></div>`;
  }

  function viewGuide() {
    const topics = (me().topics ||= {});
    const jump = PLAN.guide.map((g) => `<button data-guide-jump="${g.week}">W${g.week}</button>`).join("");
    const weeks = PLAN.guide.map((g) => {
      const w = PLAN.weeks.find((x) => x.n === g.week);
      let n = 0, got = 0;
      const secs = g.sections.map(([name, items], si) => `<h4 class="guide-sec">${esc(name)}</h4><ul class="topics">` + items.map((it, ii) => {
        const key = `${g.week}.${si}.${ii}`; n++; if (topics[key]) got++;
        return `<li><label><input type="checkbox" data-topic="${key}" ${topics[key] ? "checked" : ""}> <span>${esc(it)}</span></label></li>`;
      }).join("") + "</ul>").join("");
      return `<section class="guide-week" id="guide-${g.week}">
        <div class="guide-head"><div><p class="guide-num">Week ${g.week}</p><h3>${esc(w.title)}</h3>
          <p class="day-meta">${pretty(w.start)} to ${pretty(w.end)} · ${got} of ${n} topics you can explain</p></div>
          <button class="btn" data-open-week="${g.week}">Open week tasks</button></div>
        <p class="guide-goal">${esc(g.goal)}</p>${secs}</section>`;
    }).join("");
    const nx = PLAN.next_plan;
    return `<div class="col"><h2>Topics guide</h2>
      <p class="sub">Every topic in the plan, week by week. Tick a topic when you can explain it without notes.</p>
      <div class="weeks">${jump}<button data-guide-jump="next">Next</button></div>
      ${weeks}
      <section class="guide-week guide-next" id="guide-next"><h3>${esc(nx.title)}</h3><p class="guide-goal">${esc(nx.intro)}</p>
        <p class="flow" aria-label="Learning flow">${["Fundamentals", "LLMs", "RAG", "Agents", "Multi-agent + memory", "Production AI systems"].map((x, i) => `<span class="${i >= 4 ? "flow-next" : ""}">${x}</span>`).join('<span aria-hidden="true" class="flow-arrow">→</span>')}</p>
        ${nx.sections.map(([name, items]) => `<h4 class="guide-sec">${esc(name)}</h4><ul class="topics plain">${items.map((it) => `<li>${esc(it)}</li>`).join("")}</ul>`).join("")}
      </section></div>`;
  }

  function allMaterials() {
    return [...PLAN.materials.map((m) => ({ ...m, shared: true })), ...(me().materials || []).map((m) => ({ ...m, weeks: m.week ? [m.week] : [], source: "mine" }))];
  }
  function matLink(m) {
    const u = safeUrl(m.url);
    return u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(m.title)}</a>` : `<span>${esc(m.title)}</span>`;
  }
  function weekMaterialsHtml(n) {
    const ms = allMaterials().filter((m) => m.weeks.includes(n));
    if (!ms.length) return "";
    return `<details class="week-mats" open><summary>Materials for this week (${ms.length})</summary><ul>
      ${ms.map((m) => `<li><span class="kind">${esc(m.kind)}</span> ${matLink(m)}${m.source === "suggested" ? ' <span class="muted">(suggested)</span>' : m.source === "mine" ? ' <span class="muted">(yours)</span>' : ""}</li>`).join("")}
      </ul><button class="btn" data-action="add-material" data-week="${n}">Add material to this week</button></details>`;
  }
  function viewMaterials() {
    const f = ui.matWeek ?? "all";
    const chips = [["all", "All"], ...PLAN.weeks.map((w) => [String(w.n), "W" + w.n])].map(([v, l]) => `<button data-matweek="${v}" aria-pressed="${f === v}">${l}</button>`).join("");
    const pick = (m) => f === "all" || m.weeks.includes(+f);
    const mine = allMaterials().filter((m) => m.source === "mine" && (f === "all" || pick(m)));
    const plan = allMaterials().filter((m) => m.source === "plan" && pick(m));
    const sugg = allMaterials().filter((m) => m.source === "suggested" && pick(m));
    const item = (m) => {
      const linked = m.taskId ? findTask(m.taskId) : null;
      const wk = m.weeks.length ? (m.weeks.length > 3 ? `Weeks ${m.weeks[0]}–${m.weeks[m.weeks.length - 1]}` : "Week " + m.weeks.join(", ")) : "Any week";
      return `<li class="mat" data-mat="${esc(m.id)}">
        <div class="mat-main"><span class="kind">${esc(m.kind)}</span><h4>${matLink(m)}</h4>
          <p class="day-meta">${wk}${linked ? ` · linked to "${esc(linked.task.title)}" on ${pretty(linked.day.date)}` : m.taskId ? " · linked task was deleted" : ""}</p>
          ${m.note ? `<p class="mat-note">${esc(m.note)}</p>` : ""}</div>
        <div class="mat-actions">
          ${linked ? `<button class="icon-btn" data-goto-day="${linked.day.date}">Go to day</button>` : ""}
          <button class="icon-btn" data-action="mat-as-task" data-mat-id="${esc(m.id)}">Add as task</button>
          ${m.source === "mine" ? `<button class="icon-btn" data-action="mat-edit" data-mat-id="${esc(m.id)}">Edit</button>` : ""}
        </div></li>`;
    };
    const group = (title, list, empty) => `<h3 class="mat-group">${title} <span class="muted">(${list.length})</span></h3>` +
      (list.length ? `<ul class="mats">${list.map(item).join("")}</ul>` : `<p class="muted">${empty}</p>`);
    return `<div class="col"><h2>Materials</h2>
      <p class="sub">Playlists, books and references for each week. Add your own, pin them to a week, or link them to a task on any day.</p>
      <div class="row" style="margin-bottom:14px"><button class="btn primary" data-action="add-material" data-week="${f === "all" ? "" : f}">Add material</button></div>
      <div class="weeks">${chips}</div>
      ${group("Your materials", mine, "Nothing yet. Add a playlist, article or course you're using; only you see it.")}
      ${group("Plan materials", plan, "No plan materials for this week.")}
      ${group("Suggested references", sugg, "No suggestions for this week.")}</div>`;
  }

  function render() {
    renderPeople(); renderGrid(); renderNav(); renderBanner();
    const main = document.getElementById("main");
    main.innerHTML = ui.view === "week" ? viewWeek() : ui.view === "guide" ? viewGuide() : ui.view === "materials" ? viewMaterials() : ui.view === "cases" ? viewCases() : ui.view === "data" ? viewData() : viewToday();
    if (ui.scrollTo) { document.getElementById("day-" + ui.scrollTo)?.scrollIntoView({ block: "start" }); ui.scrollTo = null; }
    if (ui.openNote) main.querySelector(`[data-note="${ui.openNote}"]`)?.focus();
  }

  // ---------- mutations ----------
  function moveTask(id, toDate) {
    const f = findTask(id), target = dayByDate(toDate);
    if (!f || !target) return false;
    f.day.tasks.splice(f.i, 1);
    target.tasks.push(f.task);
    return true;
  }

  const editor = document.getElementById("editor"), form = document.getElementById("editor-form");
  let editing = null; // {id} or {newOn: date}
  function openEditor(opts) {
    editing = opts;
    const t = opts.id ? findTask(opts.id).task : { title: "", type: "study", hours: 1, link: "", details: "", ...(opts.prefill || {}) };
    const date = opts.id ? findTask(opts.id).day.date : opts.newOn;
    form.title.value = t.title; form.type.value = t.type; form.hours.value = t.hours ?? "";
    form.date.value = date; form.link.value = t.link || ""; form.details.value = t.details || "";
    document.getElementById("editor-title").textContent = opts.id ? "Edit task" : "Add task";
    document.getElementById("editor-delete").hidden = !opts.id;
    document.getElementById("editor-save").textContent = opts.id ? "Save task" : "Add task";
    editor.showModal();
  }
  editor.addEventListener("close", () => {
    if (editor.returnValue !== "save" || !editing) return;
    const data = { title: form.title.value.trim(), type: form.type.value, hours: parseFloat(form.hours.value) || 0, link: form.link.value.trim(), details: form.details.value.trim() };
    const date = clampDate(form.date.value || PLAN.start);
    if (!data.title) return;
    if (editing.id) {
      const f = findTask(editing.id);
      Object.assign(f.task, data);
      if (f.day.date !== date) moveTask(editing.id, date);
      toast(f.day.date !== date ? `Moved to ${pretty(date)}` : "Task saved");
    } else {
      dayByDate(date).tasks.push({ id: "u" + Date.now().toString(36), ...data });
      toast(`Added to ${pretty(date)}`);
    }
    editing = null; save(); render();
  });
  document.getElementById("editor-delete").addEventListener("click", () => {
    if (!editing?.id || !confirm("Delete this task?")) return;
    const f = findTask(editing.id);
    f.day.tasks.splice(f.i, 1);
    delete me().done[editing.id]; delete me().notes[editing.id];
    editing = null; editor.close("cancel"); save(); render(); toast("Task deleted");
  });

  function caseMarkdown(id) {
    const c = PLAN.cases.find((x) => x.id === id), d = me().cases[id] || {};
    return `# ${c.title}\n\n*${c.source}*\n\n> **Final question:** ${c.question}\n\n` +
      CASE_FIELDS.map(([k, label]) => `## ${label}\n\n${(d[k] || "").trim() || "_(empty)_"}\n`).join("\n");
  }

  // ---------- materials editor ----------
  const matDlg = document.getElementById("mat-editor"), mform = document.getElementById("mat-form");
  mform.week.innerHTML = '<option value="">No specific week</option>' + PLAN.weeks.map((w) => `<option value="${w.n}">Week ${w.n}: ${esc(w.title)}</option>`).join("");
  let matEditing = null;
  function fillTaskSelect(date, selected) {
    const day = date && dayByDate(date);
    mform.taskId.innerHTML = day ? '<option value="">No task</option>' + day.tasks.map((t) => `<option value="${t.id}" ${t.id === selected ? "selected" : ""}>${esc(t.title)}</option>`).join("")
                                 : '<option value="">Pick a day first</option>';
  }
  mform.date.addEventListener("change", () => fillTaskSelect(mform.date.value, ""));
  function openMatEditor(opts) {
    matEditing = opts;
    const m = opts.id ? me().materials.find((x) => x.id === opts.id) : { title: "", kind: "Playlist", url: "", note: "", week: opts.week ? +opts.week : "", taskId: "" };
    const linked = m.taskId ? findTask(m.taskId) : null;
    mform.title.value = m.title; mform.kind.value = m.kind; mform.url.value = m.url; mform.note.value = m.note || "";
    mform.week.value = m.week || ""; mform.date.value = linked ? linked.day.date : ""; mform.asTask.checked = false;
    fillTaskSelect(mform.date.value, m.taskId);
    document.getElementById("mat-title").textContent = opts.id ? "Edit material" : "Add material";
    document.getElementById("mat-save").textContent = opts.id ? "Save material" : "Add material";
    document.getElementById("mat-delete").hidden = !opts.id;
    matDlg.showModal();
  }
  matDlg.addEventListener("close", () => {
    if (matDlg.returnValue !== "save" || !matEditing) return;
    const list = (me().materials ||= []);
    const data = { title: mform.title.value.trim(), kind: mform.kind.value, url: mform.url.value.trim(), note: mform.note.value.trim(),
      week: mform.week.value ? +mform.week.value : "", taskId: mform.taskId.value || "" };
    if (!data.title) return;
    const date = mform.date.value ? clampDate(mform.date.value) : "";
    if (mform.asTask.checked && date) {
      const id = "u" + Date.now().toString(36);
      dayByDate(date).tasks.push({ id, title: data.title, type: data.kind === "Book" ? "book" : data.kind === "Playlist" || data.kind === "Video" ? "video" : "study", hours: 1, link: data.url, details: data.note });
      if (!data.taskId) data.taskId = id;
      if (!data.week) data.week = dayByDate(date).week;
    }
    if (matEditing.id) Object.assign(list.find((x) => x.id === matEditing.id), data);
    else list.push({ id: "mat-" + Date.now().toString(36), ...data });
    matEditing = null; save(); render(); toast("Material saved");
  });
  document.getElementById("mat-delete").addEventListener("click", () => {
    if (!matEditing?.id || !confirm("Delete this material?")) return;
    me().materials = me().materials.filter((x) => x.id !== matEditing.id);
    matEditing = null; matDlg.close("cancel"); save(); render(); toast("Material deleted");
  });

  // ---------- events ----------
  document.getElementById("people").addEventListener("click", (e) => {
    const b = e.target.closest("[data-person]"); if (!b) return;
    store.active = b.dataset.person; ui.openNote = null; save(); render();
  });
  document.getElementById("views").addEventListener("click", (e) => {
    const b = e.target.closest("[data-view]"); if (!b) return;
    ui.view = b.dataset.view; ui.openNote = null; render();
    document.getElementById("main").focus({ preventScroll: true });
  });
  document.getElementById("grid").addEventListener("click", (e) => {
    const b = e.target.closest("[data-goto]"); if (!b) return;
    ui.view = "week"; ui.week = dayByDate(b.dataset.goto).week; ui.scrollTo = b.dataset.goto; render();
  });
  document.getElementById("banner").addEventListener("click", (e) => {
    if (e.target.closest('[data-action="load-new-plan"]')) { me().days = clone(PLAN.days); me().planVersion = PLAN.version; save(); render(); toast("Updated plan loaded"); }
  });

  const main = document.getElementById("main");
  main.addEventListener("click", (e) => {
    const mw = e.target.closest("[data-matweek]");
    if (mw) { ui.matWeek = mw.dataset.matweek; render(); return; }
    const gd = e.target.closest("[data-goto-day]");
    if (gd) { ui.view = "week"; ui.week = dayByDate(gd.dataset.gotoDay).week; ui.scrollTo = gd.dataset.gotoDay; render(); return; }
    const gj = e.target.closest("[data-guide-jump]");
    if (gj) { document.getElementById("guide-" + gj.dataset.guideJump)?.scrollIntoView({ block: "start" }); return; }
    const ow = e.target.closest("[data-open-week]");
    if (ow) { ui.view = "week"; ui.week = +ow.dataset.openWeek; render(); window.scrollTo(0, 0); return; }
    const wk = e.target.closest("[data-week]:not([data-action])");
    if (wk) { ui.week = +wk.dataset.week; render(); return; }
    const el = e.target.closest("[data-action]"); if (!el) return;
    const id = el.closest("[data-id]")?.dataset.id;
    switch (el.dataset.action) {
      case "add-material": openMatEditor({ week: el.dataset.week }); break;
      case "mat-edit": openMatEditor({ id: el.dataset.matId }); break;
      case "mat-as-task": {
        const m = allMaterials().find((x) => x.id === el.dataset.matId);
        const date = clampDate(todayIso());
        openEditor({ newOn: m.weeks.length && dayByDate(date).week !== m.weeks[0] && !m.weeks.includes(dayByDate(date).week) ? PLAN.weeks.find((w) => w.n === m.weeks[0]).start : date,
          prefill: { title: m.title, link: m.url, details: m.note, type: m.kind === "Book" ? "book" : m.kind === "Playlist" || m.kind === "Video" ? "video" : "study" } });
        break;
      }
      case "note": ui.openNote = ui.openNote === id ? null : id; render(); break;
      case "edit": openEditor({ id }); break;
      case "add": openEditor({ newOn: el.dataset.date }); break;
      case "next-day": {
        const f = findTask(id), idx = me().days.indexOf(f.day);
        if (idx >= me().days.length - 1) { toast("This is the last day of the plan"); break; }
        const to = me().days[idx + 1].date; moveTask(id, to); save(); render(); toast(`Moved to ${pretty(to)}`); break;
      }
      case "move-overdue": {
        const to = el.dataset.date; let n = 0;
        me().days.forEach((d) => { if (d.date < to) [...d.tasks].forEach((x) => { if (!me().done[x.id] && x.type !== "kalamna" && visible(x)) { moveTask(x.id, to); n++; } }); });
        save(); render(); toast(`Moved ${n} tasks to ${pretty(to)}`); break;
      }
      case "copy-case": {
        const md = caseMarkdown(el.dataset.caseId);
        (navigator.clipboard?.writeText(md) || Promise.reject()).then(() => toast("Copied. Paste it into Notion."), () => { prompt("Copy this Markdown:", md); });
        break;
      }
      case "export": {
        const blob = new Blob([JSON.stringify({ app: "study-quarter", exportedAt: new Date().toISOString(), profile: store.active, data: me() }, null, 1)], { type: "application/json" });
        const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: `study-quarter-${store.active}-${todayIso()}.json` });
        document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
        toast("Backup downloaded"); break;
      }
      case "reload-plan":
        if (confirm("Reload the shared plan? Checkmarks and notes stay; your own task edits are replaced.")) { me().days = clone(PLAN.days); me().planVersion = PLAN.version; save(); render(); toast("Shared plan reloaded"); }
        break;
      case "erase":
        if (confirm("Erase all progress, notes and cases for this person? Export a backup first if unsure.")) { store.profiles[store.active] = freshProfile(); save(); render(); toast("Progress erased"); }
        break;
    }
  });
  main.addEventListener("change", (e) => {
    const el = e.target;
    if (el.dataset.topic) {
      if (el.checked) me().topics[el.dataset.topic] = Date.now(); else delete me().topics[el.dataset.topic];
      save(); const sec = el.closest(".guide-week"); const all = sec.querySelectorAll("[data-topic]"), on = sec.querySelectorAll("[data-topic]:checked");
      const meta = sec.querySelector(".day-meta"); meta.textContent = meta.textContent.replace(/\d+ of \d+ topics/, `${on.length} of ${all.length} topics`);
      return;
    }
    if (el.dataset.action === "toggle") {
      const id = el.closest("[data-id]").dataset.id;
      if (el.checked) me().done[id] = Date.now(); else delete me().done[id];
      save(); render();
    } else if (el.dataset.action === "toggle-kalamna") {
      me().hideKalamna = el.checked; save(); render();
    } else if (el.dataset.action === "import" && el.files[0]) {
      el.files[0].text().then((txt) => {
        const obj = JSON.parse(txt);
        if (obj.app !== "study-quarter" || !obj.data?.days) throw new Error();
        const who = PLAN.profiles.find((p) => p.id === store.active).name;
        if (!confirm(`Replace ${who}'s current progress with this backup from ${obj.exportedAt?.slice(0, 10) || "unknown date"}?`)) return;
        store.profiles[store.active] = obj.data; save(); render(); toast("Backup imported");
      }).catch(() => toast("That file isn't a Study Quarter backup."));
    }
  });
  let typingTimer;
  main.addEventListener("input", (e) => {
    const el = e.target;
    if (el.dataset.note) me().notes[el.dataset.note] = el.value;
    else if (el.dataset.daynote) me().dayNotes[el.dataset.daynote] = el.value;
    else if (el.dataset.casefield) { const [c, k] = el.dataset.casefield.split("."); (me().cases[c] ||= {})[k] = el.value; }
    else return;
    clearTimeout(typingTimer); typingTimer = setTimeout(save, 400);
  });
  main.addEventListener("focusout", (e) => { if (e.target.dataset.note !== undefined) { save(); } });

  render();
})();
