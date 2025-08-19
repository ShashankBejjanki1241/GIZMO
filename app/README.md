# UI (Next.js) — To Scaffold

Planned pages:
- `/` — create task (instruction + template)
- `/t/[taskId]` — live timeline (WebSocket to `/ws/{taskId}`), diff viewer, logs
- `/replay/[runId]` — deterministic replay from stored events

Tech:
- Next.js (app router), websocket client, Monaco diff
- Tailwind for quick theming
