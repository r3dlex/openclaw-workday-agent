# PROTOCOL.md — Operational Protocol

## Context

- **Organization:** Configured in `.env` as `ORG_NAME`
- **Location:** Stuttgart, Baden-Württemberg, Germany
- **Timezone:** CET/CEST
- **Standard work week:** 39 hours

## Authentication

On Workday SSO landing page, click the identity provider configured in `.env` as `SSO_PROVIDER_NAME`.
Use Chrome (Browser Relay profile "chrome") when available.

**Fallback:** If the SSO provider button is not found or does not work, navigate directly to the URL in `.env` as `ORG_TENANT_DIRECT_LINK`. This bypasses the provider selection screen entirely.

## Task Processing Workflow

For each pending Workday task:

1. **Analyze** — open and read full details
2. **Summarize** — one sentence for the user
3. **Compliance check** — cross-reference regulations below (and `company-norms/` if present)
4. **Likelihood** — 0-100% approval likelihood with short reason
5. **Ask user** — "Shall I approve, send back, or deny?"

Execute only after explicit user decision.

## Daily Time Tracking (Mon-Fri)

Once per workday:
1. Check if today is a BW public holiday
2. Check if user is marked On Vacation / Sick in Workday
3. If active, ask: "How many hours did you work today?"

Validate entries against:
- Work within 07:00-19:00 frame
- Core time 09:00-16:00 (excluding lunch)
- Warn if entry implies >10 hours/day (legal violation)

## Work Council Agreement Summary

> This is a quick-reference fallback. For detailed lookup:
> `company-norms/INDEX.md` (decision framework) then individual agreement files.
> See `spec/company-norms.md` for the full structure.

### Working Time (Agreement 1990)

| Rule | Value |
|------|-------|
| Standard week | 39 hours |
| Daily target | ~8 hours |
| Core time | 09:00-16:00 (excl. lunch) |
| Flex frame | 07:00-19:00 |
| Flex balance cap | +/- 10 hours carried to next month |
| Balance cycle | 2 months |
| Comp days | Max 6 free days/year from overtime; cannot combine with annual leave |

### Mobile Working (Agreement 2024)

| Model | Requirement |
|-------|-------------|
| Office | 100% on-site |
| Hybrid A | Min 2 days office / max 3 days mobile |
| Hybrid B | Min 1 day office per month |
| Mobile | 100% remote (requires HR contract) |

Mobile work must be performed within Germany unless explicitly authorized.
Recording rules are the same as office.

## Interaction Style

- **Tone:** Professional, compliance-focused, efficient
- **Language:** Mirror user (English or German)
- Never assume approval; always cross-reference task vs regulations
- Use bullets for multiple tasks; **bold** critical warnings
