# PRD — Multi-Agent AI Developer

## Problem
Great coding assistants exist, but end-to-end planning→coding→testing is opaque and unsafe. We want a transparent, safe, demo-able system.

## Users
- Recruiters/engineers (primary)
- Curious developers (secondary)

## Use Cases
- UC1: Run a curated showcase task end-to-end with no setup.
- UC2: Enter a custom task for a chosen template repo.
- UC3: Watch agent timeline, inspect diffs, view test logs.
- UC4: Replay a past successful run (no new LLM calls).

## In Scope (MVP)
- Agents: Planner, Coder, Tester.
- Secure sandbox: network-isolated Docker, time/mem caps.
- Templates: React+Jest, Express+Supertest, Flask+pytest.
- Real-time dashboard: timeline, diff viewer, logs.
- Artifacts: downloadable diffs and logs.

## Out of Scope (MVP)
- Reviewer agent, PRs to GitHub, auth roles, payments.

## User Stories & AC
1. Start Task → live updates within 5s.  
2. View code changes as side-by-side diffs.  
3. See tests run with pass/fail counts and stack traces.  
4. Replay a run deterministically (no LLM).  
5. Safety: only allowlisted commands; kill on timeout.

## Constraints
- Budget: free tiers.  
- Security: no outbound network from sandbox.  
- Determinism: low temperature; strict output parsing.

## Non-Functional
- P95 end-to-end showcase < 90s.
- Availability (demo week) 99%.
- Structured logging and run IDs.

## Milestones
M1 infra, M2 protocol/orchestrator, M3 sandbox, M4 UI, M5 reliability/memory, M6 deploy+docs.

## Metrics
- Success rate on 10 curated tasks ≥ 80%.
- Time-to-first event < 5s.  
- Zero sandbox escapes in testing.
