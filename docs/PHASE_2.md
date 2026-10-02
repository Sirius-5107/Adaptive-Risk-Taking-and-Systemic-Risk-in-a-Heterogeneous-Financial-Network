# Phase 2 — Heterogeneous Financial Network

Phase 2 adds the random network while keeping the clearing model deterministic once a network and shock are fixed.

## What is generated?

We create N institutions and assign each one to one of two groups:

- group 0: lower-risk/conservative
- group 1: higher-risk/risky

For every ordered pair of distinct institutions i and j:

- if i and j belong to the same group, an edge is created with probability p_within;
- if i and j belong to different groups, an edge is created with probability p_cross.

An edge i -> j means institution i owes institution j.

For this phase, every active edge has the same obligation amount exposure_scale.

This is intentional. We first want to isolate the effect of network structure. Randomizing both who is connected and how large every exposure is would make early debugging harder.

## Baseline

The documented baseline is:

- N = 100
- fraction lower-risk = 0.50
- p_within = 0.10
- p_cross = 0.05
- exposure_scale = 0.05
- seed = 20261001

The generator uses NumPy's local Generator, so the same seed produces the same groups and obligation matrix.

## Why p_within and p_cross matter

If p_within is larger than p_cross, institutions are more likely to connect to institutions from their own group.

This allows us to compare networks with similar overall connectivity but different placement of cross-group links.

That distinction matters because systemic contagion depends not only on how many links exist, but also on where those links sit in the network.

## What this phase does not claim

The random graph is a modelling assumption, not a measurement of the real financial system.

The two groups are also computational abstractions. They become financially meaningful only after we assign different risk exposures and run shocks through the clearing mechanism.

## Tests

The network tests verify:

1. expected group counts;
2. no self-obligations;
3. non-negative exposures;
4. exact reproducibility under a fixed seed;
5. zero probabilities produce no edges;
6. active edges use the configured exposure scale.

The next phase will connect this generated network to institution assets, liabilities, shocks, and the Phase 1 clearing solver.
