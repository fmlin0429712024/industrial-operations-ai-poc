---
name: field-execution
description: Convert an approved industrial asset recommendation into a field-ready work package and outcome record. Use after a qualified human approves an inspection, maintenance, or operational response.
---

# Field Execution

Prepare work; do not dispatch people or create a production work order without approval.

## Inputs

- Approved recommendation and supporting evidence.
- Asset location, criticality, safety requirements, and work history.
- Available technician skills, parts, and operating window.

## Procedure

1. Confirm explicit human approval and work boundary.
2. Assemble the asset context, inspection steps, safety notes, and evidence.
3. Identify prerequisites: parts, isolation, permits, and production coordination.
4. Produce a draft work package and a structured outcome template.

## Output contract

Return `work_scope`, `priority`, `safety_prerequisites`, `required_parts`, `evidence`, `approval_reference`, and `outcome_fields`.
