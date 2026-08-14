# Governance records

This directory separates active interim authority, unratified proposals, public
decisions, meeting records, conflicts, appeals, security decisions, and
succession procedures.

| Path | Purpose | Authority |
|:---|:---|:---|
| `authority.json` | Machine-readable present governance state | Mirrors active `GOVERNANCE.md` |
| `PROPOSED_TSC_CHARTER.md` | Preserved permanent-charter proposal | None until ratified |
| `PROPOSED_IP_AND_MARKS_POLICY.md` | Questions and draft policy for legal review | None until adopted |
| `decisions/` | Public decision records | Each record states its own authority |
| `meetings/` | Meeting minutes | Evidence only, unless linked by a decision |
| `security/` | Public templates for embargoed decisions | Details remain in private advisories |
| `SUCCESSION_AND_INACTIVITY.md` | Interim continuity procedure | Active interim process |

Working signal: a current claim can be traced to `authority.json` and a decision
record, while proposed language is never mistaken for an operative grant.
