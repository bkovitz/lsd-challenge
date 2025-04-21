# Term Rewriting System Notes Summary

## March 31, 2025: Sequence Variables Syntax
- **New Syntax**: Inspired by Scheme's `syntax-rules` macros (see [Scheme TSPL4](https://scheme.com/tspl4/syntax.html#./syntax:h2)):
  - Uses `Seq[ARG ...]` to denote sequence variables with ellipsis.
  - Example Rule: `Succ[Seq[ARG ...]] -> Seq[Succ[ARG] ...]`
    - Reduces `Succ[Seq[a b c]]` to `Seq[Succ[a] Succ[b] Succ[c]]` in one step.
  - Another Rule: `Seq[Succ[ARG] ...] -> Seq[Undo[ARG] ...]`
    - Reduces `Seq[Succ[a] Succ[b] Succ[c]]` to `Seq[Undo[a] Undo[b] Undo[c]]`.
- **Advantage**: Ellipsis separated from variable name allows matching complex repeating structures on the left-hand side (LHS).
- **Limitation**: LHS like `Seq[Succ[ARG] ...]` won’t match unrelated structures (e.g., `Seq[Pred[a] Pred[b] Pred[c]]`).

## March 19, 2025: New World Pons Asinorum
- **Objective**: A minimal system to complete the "New World" in the pons asinorum:
  - Reduces `NewWorld[Seq[i j k] Blank]` to `NewWorld[Seq[i j k] Seq[i j l]]`.
  - Works for any successor run (e.g., starting from any letter, any length).
  - Fails to reduce unrelated inputs.
- **Rules**:
  - `NewWorld[Run[...α] Blank] -> NewWorld[Run[...α] AdvanceLast[...α]]`: Initiates advancement of the last element.
  - `Seq[A $Succ[A] ...α] -> Seq[Run[A Succ[A]] ...α]`: Starts a run from a successor pair.
  - `Seq[Run[...α A] $Succ[A] ...β] -> Seq[Run[...α A Succ[A]] ...β]`: Extends a run with a successor.
  - `Seq[Run[...α]] -> Run[...α]`: Flattens a single-run sequence.
  - `AdvanceLast[...α A] -> Seq[...α Succ[A]]`: Advances the last element to its successor.
- **Note**: `$Succ[A]` suggests forcing a reduction to `Succ[A]`, ensuring correct successor matching.

## March 18, 2025: Painting a Canvas
- **Objective**: Paint a canvas from a chunk specification:
  - Example: `Paint[Chunk[Seq[Run[L -> Succ]] Length[5] FirstItem[a]] Blank]` reduces to `Painted[Seq[a b c d e]]`.
- **Proposed Rules**:
  - `Paint[Chunk[FirstItem[X] ...α] Seq[_ ...β]] -> Paint[Chunk[...α] Seq[X ...β]]`: Adds the first item to the sequence, removing `FirstItem`.
  - `Paint[Chunk[Length[N] ...α] Blank] -> Paint[Chunk[...α] Seq(repeat _ N)]`: Creates a sequence of `N` placeholders.
  - `Paint[Chunk[Seq[Run[RULE]] ...α] Seq[...β _ L ...γ]] -> Paint[Chunk[...α] Seq[...β FillPairFromRun[RULE 'L L] ...γ]]`: Applies a run rule (e.g., `L -> Succ`) to fill a pair.
  - `FillPairFromRun[L -> R[L] X Y] -> Seq[X Y] substitute SubstFromRule[R[X] -> Y]`: Fills a pair using a rule substitution.
  - `SubstFromRule[RULE] -> pmatch(R compatibleRule(R))`: Generates a substitution from a rule (requires under-the-hood functions).
- **Notes**:
  - `'L` suggests a fresh variable (e.g., `(fresh 'L)`).
  - `substitute` and `pmatch` imply built-in system functions for substitution and pattern matching.

## General Observations
- **Sequence Variables**: Central to all systems, using ellipsis (`...`) for flexible matching and transformation.
- **Modularity**: Each note focuses on a specific domain (sequence ops, New World, painting), suggesting a modular rule set.
- **Complexity**: Rules range from simple transformations to requiring advanced features (e.g., fresh variables, substitutions).

