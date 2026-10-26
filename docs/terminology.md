# Evolving Spider — Terminology

*Protocol concepts mapped to spider behavior*

---

## Structure

| Term | Meaning | Spider Behavior |
|------|---------|-----------------|
| **Hub** | `project.md` — single source of truth | Center of the web where spider sits |
| **Radials** | Task docs branching from hub | Spokes extending from web center |
| **Dragline** | Git history — safety thread | Silk line spider trails for safety |
| **Egg Sac** | Backlog — future tasks | Protected bundle of potential |

---

## Actions

| Term | Meaning | Spider Behavior |
|------|---------|-----------------|
| **Weave** | Create new doc | Building web structure |
| **Spin** | Implement, write code | Producing silk, active creation |
| **Wrap** | Complete task, commit | Securing caught prey |
| **Sense** | Read NOW section, check status | Detecting vibrations on web |
| **Repair** | Fix docs or code | Mending damaged web sections |
| **Molt** | Major revision as understanding evolves | Shedding old shell to grow |
| **Anchor** | Establish foundation (first task, initial setup) | First threads that hold the web |
| **Retreat** | Revert to safe state | Moving to safe position |

---

## States

| Term | Icon | Meaning | Spider Behavior |
|------|------|---------|-----------------|
| **Waiting** | 🚫 | Blocked | Patient observation |
| **Spinning** | 🔄 | Active | Producing silk |
| **Wrapped** | ✅ | Done | Prey secured |
| **Dormant** | ⏳ | Pending | Resting, not yet active |

---

## Session Flow

| Phase | Term | Action |
|-------|------|--------|
| Start | **Sense** | Read hub and active radial, understand state |
| Work | **Spin** | Implement based on NOW.Next |
| Problem | **Repair** | Fix what's broken |
| Checkpoint | **Wrap** | Commit progress |
| End | **Anchor** | Update NOW for next session |
| Failure | **Retreat** | Revert via dragline |

---

## Structures

| Term | What |
|------|------|
| **Web** | The entire project documentation structure |
| **Hub** | `project.md` |
| **Radial** | Individual task doc (`tasks/t[#]-[name].md`) |
| **Spiral** | Iterations within a task (LOG entries) |
| **Dragline** | Git commit history |
| **Egg Sac** | Future tasks (⏳ Pending in task table) |
| **Anchor Point** | Initial project setup, T1 |

---

## Quick Reference

```text
Web
├── Hub (project.md)
│   ├── Radial (t1-auth.md) ——— Spirals (iterations)
│   ├── Radial (t2-dashboard.md)
│   └── Egg Sac (pending tasks)
└── Dragline (git history)

Session: Sense → Spin → Wrap → Anchor
Recovery: Retreat via Dragline
Growth: Molt when understanding evolves
```
