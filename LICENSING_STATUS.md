# Licensing and rights status

<!-- vcp-document-control
status: Unresolved, authorized review required
normative-authority: Rights decision gate X016
protocol-version: All repository protocol versions and artifacts
last-reviewed: 2026-08-14 active authority and evidence boundary
owner: Authorized rights authority
evidence-boundary: Conflict inventory and required decision, not legal advice or authorization
-->

**Status:** unresolved, authorized review required
**Decision gate:** X016 in the coordinated release ledger
**Last reviewed:** 2026-08-14

This repository contains conflicting licence signals. Source maintenance can
classify and expose that conflict, but cannot decide ownership, contributor
authority, IETF submission rights, patent terms, or trademark rights. No release
or submission should treat this page as legal advice or an authorization.

## Current evidence matrix

| File class | Repository evidence | Unresolved question | Release treatment |
|:---|:---|:---|:---|
| Root repository | `LICENSE` contains MIT text | Which files and historical contributions it validly covers | Retain; do not generalize beyond reviewed scope |
| Normative specifications | Several files carry CC BY 4.0 notices while README and former governance claimed MIT | Which notice controls each file and whether every contributor authorized it | Rights review required per file class |
| Schemas and examples | Often lack individual notices | Whether root MIT applies and whether copied material has separate terms | Include only after matrix approval |
| IETF Internet-Draft source | IETF Trust and BCP 78 boilerplate coexist with a final CC BY 4.0 footer | Whether that footer is permissible and whether all authors authorized submission | Withdrawn working copy; no submission authority |
| Rendered DOCX candidates | Generated from several sources and templates | Embedded text, template, font, image, and contributor rights | Candidate only; canonical selection and rights review pending |
| Contributions | DCO language exists, but historical sign-offs and applicable file licences require review | Whether every contribution was properly certified for its destination licence | Audit before publication; DCO does not cure missing rights |
| Name, logo, and certification terms | Former governance asserted ownership and permissions without an attached legal record | Actual owner, registrations, permitted descriptive use, certification authority, and enforcement | No certification or trademark permission claimed here |
| Foundation transfer | Former charter described a contingent grant | Current rights holder, accepting entity, executed terms, and effective date | No transfer claimed |

## Required authorized decision

The X016 evidence should approve an exact matrix that identifies:

1. each governed path or file class;
2. copyright holder or authorized licensor;
3. applicable licence and notice text;
4. treatment of prior contributions and DCO evidence;
5. third-party text, templates, fonts, images, and generated artifacts;
6. IETF submission and redistribution terms;
7. patent disclosure and contribution terms;
8. trademark ownership and permitted use;
9. changes required in README, package metadata, headers, rendered documents,
   contribution guidance, and release bundles;
10. reviewer name, authority, date, scope, conditions, and approved hashes.

Working signal: an authorized matrix covers every shipped file, automated checks
match that matrix, and public copy no longer relies on one repository-wide badge
to hide file-specific terms.

## Present public wording

Use: "Licensing and submission rights are under review; see
`LICENSING_STATUS.md`."

Do not claim that all repository content is MIT, that all specification text is
CC BY 4.0, that an IETF submission is authorized, that a foundation transfer is
effective, or that a certification or trademark licence exists until the
authorized decision says so.
