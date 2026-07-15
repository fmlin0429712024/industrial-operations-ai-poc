---
name: process-energy-optimization
description: Evaluate industrial operating conditions and propose safe, evidence-backed process or energy actions. Use when operators need to assess yield, throughput, energy, emissions, or constraint trade-offs.
---

# Process & Energy Optimization

Evaluate decisions; never autonomously modify a process setpoint.

## POC boundary

For the ESP workflow, this skill does not solve a full production-optimization problem. It compares only two choices: continue monitoring, or plan an approved inspection during a feasible operating window. It records production, safety, and intervention trade-offs for an operator.

## Inputs

- Current process conditions and trends.
- Engineering, safety, and operating constraints.
- Production, energy, emissions, and quality objectives.

## Procedure

1. Identify the decision objective and non-negotiable constraints.
2. Separate evidence from assumptions and flag missing measurements.
3. Compare feasible actions and state expected trade-offs.
4. Produce a recommendation for operator review.

## Output contract

Return `objective`, `constraints`, `options`, `recommended_action`, `expected_tradeoffs`, `evidence`, and `operator_approval_required`.
