# Study Quarter tracker (Oct 1 – Dec 31, 2026)

A static study tracker for Ahmed and Bassant. Plain HTML, CSS and JavaScript, no build step.

## Files

| File | What it is |
|---|---|
| `index.html` | Page shell and the edit-task dialog |
| `styles.css` | All styling (light and dark mode follow the device) |
| `app.js` | The app: views, checkmarks, notes, editing, moving tasks, backups |
| `plan.js` | The shared plan data (`window.PLAN`): 11 weeks, 92 days, topics guide, next-plan preview, research cases |
| `tools/generate_plan.py` | Builds `plan.js` from a weekly spec. Edit this to change the shared plan |

## Deploy on Cloudflare Pages

1. Put this folder in a GitHub repo (or keep it as a folder).
2. Cloudflare dashboard → Workers & Pages → Create → Pages.
3. Either connect the GitHub repo, or choose **Upload assets** and drag the folder in.
4. Build settings: framework preset **None**, build command **empty**, output directory **`/`** (the repo root).
5. Deploy. Every push to the repo redeploys automatically if you connected GitHub.

You can also just open `index.html` locally; it works without a server.

## How progress is saved

- Each person (Ahmed, Bassant) has their own copy of the plan, checkmarks, notes and research-case answers.
- Everything is saved in the browser's `localStorage` under the key `studyQuarter.v1`. It stays on that device and browser only.
- To move to another device or keep a backup: **Settings & backup → Export my progress**, then **Import a backup** on the other device.
- Possible upgrade later: sync across devices with Cloudflare Pages Functions + D1 or KV.

## What each person can do on the page

- Check tasks off, add notes to any task or day.
- **Move** a task to the next day, or **Edit** it to change the title, type, hours, link, details or day.
- **Add task** to any day, delete tasks.
- **Today** shows unfinished tasks from earlier days with a "Move all to today" button.
- **Topics guide**: every week's title, goal and all its topics, with a checkbox per topic ("I can explain this"), plus the next 3 months' continuation at the end.
- **Materials**: all playlists, books and videos from the plan plus suggested references, filterable by week. Each person can add their own materials, pin them to a week, and link them to a task on any day (or add them as a new task). Linked materials show on the task, and each week shows its materials above its days.
- **Research cases**: a page per BARQ guide case with the research template; "Copy for Notion" copies it as Markdown.
- Hide the daily Kalamna block per person (Settings).

## Changing the shared plan (for both people)

1. Edit `BLOCKS` (daily tasks), `GUIDE` (topics guide), `NEXT` (next-plan preview), `MATERIALS` (shared materials) or `CASES` in `tools/generate_plan.py`.
2. Bump `PLAN_VERSION` (for example `2026-10-15.1`).
3. Run `python tools/generate_plan.py` (it prints study hours vs. capacity per week).
4. Deploy. Each person sees a banner offering the updated plan. Accepting keeps checkmarks and notes for tasks whose id didn't change, and replaces their own task edits.

Task ids are assigned in order (`t0001`, `t0002`…), so adding a task early in the spec shifts later ids. If someone has lots of progress, prefer adding new tasks near the end of a week, or add them in the page itself.

## Notes for editing with Claude Code

- Keep it framework-free: no bundler, no npm dependencies.
- Plan data shape: `PLAN.days[] = { date: "YYYY-MM-DD", week: n, tasks: [{ id, title, type, hours, details, link }] }`.
  Task `type` is one of `kalamna, study, project, book, video, leetcode, research, review`.
- Per-person state shape in localStorage: `{ active, profiles: { ahmed: { planVersion, days, done: {id: timestamp}, notes: {id: text}, dayNotes: {date: text}, cases: {caseId: {field: text}}, topics: {"week.section.item": timestamp}, materials: [{ id, title, kind, url, note, week, taskId }], hideKalamna } } }`.
- Adding a person: add them to `profiles` in `generate_plan.py` and regenerate.
- Weekend days are Friday and Saturday (`WEEKEND` in the generator); weekends get 3h of study, weekdays 2.5h, plus Kalamna 2h and one ~20 min video every day.

Topics-guide ticks are keyed by position (`week.section.item`), so reordering topics inside a section moves the ticks with the position, not the text. Add new topics at the end of a section to keep existing ticks correct.
