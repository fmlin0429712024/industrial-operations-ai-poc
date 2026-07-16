---
name: field-execution
description: Convert an approved industrial asset recommendation into a field-ready work package and outcome record. Use after a qualified human approves an inspection, maintenance, or operational response.
---

# Field Execution

Prepare a synthetic ticket; do not dispatch people, purchase equipment, or create a production work order.

## POC boundary

For the ESP workflow, create and close a **synthetic diagnostic ticket** only. The ticket identifies a Field Engineer role, scope, safety prerequisites, and a simulated outcome. Do not select a real technician, reserve a time slot, dispatch personnel, purchase an ESP, or create a production work order.

## Inputs

- Approved recommendation and supporting evidence.
- Asset location, criticality, safety requirements, and work history.
- Available technician skills, parts, and operating window.

## Procedure

1. Confirm explicit human approval and work boundary.
2. Assemble the asset context, inspection steps, safety notes, and evidence.
3. Identify prerequisites: parts, isolation, permits, and production coordination.
4. Create a synthetic ticket after explicit approval.
5. On a simulated field update, record either `esp_replaced` or `no_fault_found`, then close the ticket.

## Output contract

Return `ticket_id`, `ticket_status`, `work_scope`, `safety_prerequisites`, `evidence`, `approval_reference`, and `field_outcome`.
