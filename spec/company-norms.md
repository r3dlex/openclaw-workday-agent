# Company Norms Reference

> Committed stub. The actual agreements live in `company-norms/` (gitignored).
> This file documents the structure and decision framework without sensitive content.

## Purpose

The OpenClaw agent cross-references work council agreements (Betriebsvereinbarungen)
when making compliance decisions about Workday task approvals and time tracking.

## Expected Files in `company-norms/`

```
company-norms/
├── INDEX.md                                    # Progressive disclosure entry point
├── betriebsvereinbarung-arbeitszeit-de.md      # Working time (German, 1990)
├── working-hours-agreement-en.md               # Working time (English, 1990)
├── betriebsvereinbarung-mobile-arbeit-de.md    # Mobile working (German, 2024)
├── mobile-working-agreement-en.md              # Mobile working (English, 2024)
└── README.md                                   # Setup instructions
```

## Agent Lookup Order

```
PROTOCOL.md (summary tables)
  └─► company-norms/INDEX.md (quick reference + decision framework)
       └─► company-norms/<specific-agreement>.md (full legal text)
```

The agent should:
1. Start with the summary in `PROTOCOL.md` for most decisions
2. Consult `company-norms/INDEX.md` when the summary is insufficient
3. Read the full agreement text only when quoting specific clauses

## Decision Framework

When evaluating a Workday task:

| Check | Rule | Source |
|-------|------|--------|
| Time entry within flex frame | 07:00-19:00 | Working Time IV.2 |
| Core hours respected | 09:00-16:00 excl. lunch | Working Time I.2 |
| Daily max not exceeded | 8h standard, warn >10h | Working Time I.4 + ArbZG |
| Weekly target | 39h | Working Time I |
| Plus/minus balance | Max +/-10h carry-over, 2-month cycle | Working Time I.6 |
| Comp days | Max 6/year, not adjacent to leave | Working Time I.7 |
| Overtime authorized | Must be management-ordered | Working Time II.1 |
| Mobile work model | Office / Hybrid A / Hybrid B / Full mobile | Mobile Working §3 |
| Work location | Germany unless pre-approved | Mobile Working §2 |

## Setup

To populate `company-norms/` for a new clone:

```bash
# Copy your organization's agreements into the directory
cp /path/to/agreements/*.md company-norms/

# Verify the index exists
cat company-norms/INDEX.md
```

If `company-norms/` is empty, the agent falls back to the summary tables in `PROTOCOL.md`.
