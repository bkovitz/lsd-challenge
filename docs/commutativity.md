# A Commutative Strategy
This rendition of the diagram may be beneficial:
```
A----f1--->B
|          |
g1         g2
|          |
V          V
C----f2--->D
```
- A, B, C, D are the four strings of an LSD problem.
- f1 is "delta" or more accurately the "precedent."
- f1, g1, f2, g2 are functions that are presumed to exist if the problem has a solution.
- A, B, C are known; D is undefined.
- While the functions probably won't have inverses, approximating their "inverses" may still be useful.
- Right now we only use `f1` and have given little consideration of `g1`; but `g1` also maps one known string to another, so it should be relatively easy to approximate (possibly the easiest).
- For example, there are many ways to represent D:
  (Here, `f^` and `g^` represent the inverses of f and g)
  + `f2(C)`
  + `g2(B)`
  + `f2.g1(A)`
  + `g2.f1(A)`
  + `f2.g1.f1^(B)`
  + `g2.f1.g1^(C)`
- For a solution to exist, these expressions must be *similar* (~). Here similar is different from the conventional definition.
- While the following notation is actually improper, but I believe it is an easy way to think about the goal:
```
f2(C) ~ g2(B) ~ f2.g1(A) ~ g2.f1(A) ~ f2.g1.f1^(B) ~ g2.f1.g1^(C)
```
- Essentially, the similarity serves as a "weight" that measures the strength of a function(s).
- The more similary, the more confidence we can have that the functions are accurate.
- In theory, this would provide more paths for finding D.
- Keep in mind, that previous expression just for "D" and represents the last step of the process.
- Also, this doesn't include corresponding "inverses" which may also be useful.
- This is how the algorithm decides when and where to generate chunks.
## Steps
1. Search for `f1` and `g1` by maximizing `f1(A) ~ B` and `g1(A) ~ C`.
2. Search for `f^1` and `g^1`, by maximizing `g^1(C) ~ A` and `f^1(B) ~ A`.
3. Maximize `f1.g^1(C) ~ B` and `g1.f^1(B) ~ C`.
4. (And so on, until finally:)
5. Maximize `f2(C) ~ g2(B) ~ f2.g1(A) ~ g2.f1(A) ~ f2.g1.f1^(B) ~ g2.f1.g1^(C)`

