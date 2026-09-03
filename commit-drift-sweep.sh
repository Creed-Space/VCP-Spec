#!/usr/bin/env bash
# Commits + pushes this session's drift-sweep edits in VCP-Spec.
# Stages ONLY the 10 files this session touched. Other modifications
# you may have locally (specs/VCP_ADAPTATION_v2.0.md, specs/VCP_PAPER_OUTLINE.md,
# specs/value_context_protocols_paper_v1.md, veps/VEP-0004-...md, etc.)
# are left untouched — review and commit those separately.
#
# Run from repo root: bash commit-drift-sweep.sh
set -euo pipefail

cd "$(dirname "$0")"

# Clear any sandbox-leftover lock files.
rm -f .git/index.lock
find .git/objects -name 'tmp_obj_*' -delete 2>/dev/null || true

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "On branch: ${BRANCH}"

# Files this session edited.
FILES=(
  docs/VCP_OVERVIEW.md
  docs/VCP_NEWCOMER_GUIDE.md
  docs/VCP_CONTEXT_DATA_FLOW.md
  docs/VCP_INTEGRATION_GUIDE.md
  docs/context/VCP_CONTEXT_SPECIFICATION.md
  docs/adaptation/VCP_ADAPTATION.md
  specs/VCP_PAPER_SPEC_CONTENT.md
  specs/VCP_SPECIFICATION_v2.0.md
  specs/extensions/VCP-X-Personal/spec.md
  schemas/vcp-adaptation-context.schema.json
)

git add "${FILES[@]}"

echo
echo "Staged for commit:"
git diff --cached --stat
echo
echo "If anything unexpected is staged, run 'git restore --staged <file>'"
echo "and re-run, or Ctrl-C now."
echo "Press Enter to commit + push..."
read -r

git commit -m "docs: VCP v3.2 drift sweep — CULTURE communication-styles, 18-dim model, schema sync

- Replace nationality-based CULTURE values (american/european/japanese/global)
  with spec-aligned communication styles (high_context/low_context/formal/
  casual/mixed) across user-facing docs and the 12-row CULTURE table in
  VCP_CONTEXT_SPECIFICATION.md.
- Modernise the v3.0 emoji showcase block in VCP_CONTEXT_SPECIFICATION.md
  and VCP_ADAPTATION.md (Appendix A): drop deprecated STATE-as-situational,
  add SYSTEM_CONTEXT at position 9, add the four VEP-0004 dimensions
  (EMBODIMENT, PROXIMITY, RELATIONSHIP, FORMALITY) as positions 10-13, and
  list the 5 personal-state R-line dimensions.
- Update stale 14-dimension / 9-situational claims in specs/ to the
  current 18-dim model (13 situational + 5 personal):
    * specs/VCP_PAPER_SPEC_CONTENT.md
    * specs/VCP_SPECIFICATION_v2.0.md (conformance table + bullet)
    * specs/extensions/VCP-X-Personal/spec.md
- Sync schemas/vcp-adaptation-context.schema.json from v1 (Enneagram, 9
  dims) to v3.2 (13 situational + 5 personal, VEP-0004) so the canonical
  schema location matches what the SDKs validate against."

git push origin "${BRANCH}"

echo
echo "Done."
git log --oneline -n 1
