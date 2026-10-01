# Validation

## Level A — Implementation
Check:
- payment fractions remain in [0,1]
- exposures are nonnegative
- no self-loops unless explicitly allowed
- zero exposure means no network-mediated contagion
- convergence is correctly detected
- non-convergence is visible to the caller

## Level B — Simulation sanity
Sanity checks include:
- no-shock solvent systems should remain solvent
- increasing exposure should permit more contagion pathways
- removing network edges should remove network-mediated contagion
- stronger adverse shocks should not systematically create an artificial improvement under otherwise identical conditions

These are model sanity checks, not universal mathematical theorems.

## Level C — Statistical validation
Use sufficient Monte Carlo runs, multiple seeds, uncertainty intervals, and sensitivity analysis.

## Reproducibility
Record configuration, Git commit, package versions where possible, parameters, and seed.

## Important distinction
Monte Carlo confidence/uncertainty quantifies randomness *inside the chosen simulator*. It does not quantify uncertainty about whether the simulator itself is a good representation of real financial systems.

## No cherry-picking
All primary results must follow the predeclared baseline and experiment definitions.
