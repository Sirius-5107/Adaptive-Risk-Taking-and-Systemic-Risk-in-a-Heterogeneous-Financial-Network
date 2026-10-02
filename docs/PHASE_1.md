# Phase 1 — Deterministic Clearing

This phase deliberately ignores random networks, Monte Carlo, ML, and adaptation.

## The hand-checkable system

Four institutions form a chain:

A → B → C → D

Each arrow represents an interbank obligation of 100.

External assets after the shock:

| Bank | External assets | Interbank obligation |
|---|---:|---:|
| A | 40 | 100 to B |
| B | 20 | 100 to C |
| C | 20 | 100 to D |
| D | 0 | 0 |

External liabilities are zero in this toy example.

### Step 1 — A
A has 40 available and owes 100.

Payment fraction:
r_A = 40 / 100 = 0.40

So A pays B 40.

### Step 2 — B
B started with 20 and receives 40 from A.

Available funds:
20 + 40 = 60

Therefore:
r_B = 60 / 100 = 0.60

B pays C 60.

### Step 3 — C
C started with 20 and receives 60 from B.

Available funds:
20 + 60 = 80

Therefore:
r_C = 80 / 100 = 0.80

C pays D 80.

### Step 4 — D
D has no interbank obligation, so there is no payment fraction to solve for. We represent it as 1.

### Result

A shock to A produces:

0.40 → 0.60 → 0.80 → 1.00

The important idea is that A's loss propagates through the payment network.

## Why this is a fixed-point problem

In this particular chain, we can calculate left-to-right because there are no cycles.

Real networks can contain cycles such as:

A → B
B → A

Then A's payment affects B, while B's payment affects A. Neither can be solved independently.

That is why the general solver repeatedly:
1. starts with a payment guess,
2. calculates incoming payments,
3. recalculates payment fractions,
4. repeats until the numbers stop changing.

The tests in tests/test_clearing.py turn the hand calculations above into executable checks.

## What this phase proves

It does not prove anything about real banks.

It proves that our implementation correctly captures the first mechanism we care about:

asset shock → reduced payment → counterparty receives less → counterparty's payment may fall.

Only after these deterministic checks pass should we introduce randomness.
