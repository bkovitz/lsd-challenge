import re
from typing import Dict, List, Tuple, Union, Optional, Set, Any
import copy

class Term:
    """Base class for all terms in the rewriting system."""
    def __init__(self, name: str, args: List["Term"] = None):
        self.name = name
        self.args = args or []

    def __str__(self) -> str:
        if not self.args:
            return self.name
        args_str = " ".join(str(arg) for arg in self.args)
        return f"{self.name}[{args_str}]"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Term):
            return False
        return self.name == other.name and self.args == other.args

    def copy(self) -> "Term":
        """Create a deep copy of this term."""
        return Term(self.name, [arg.copy() for arg in self.args])
        
    def is_constant(self) -> bool:
        """Check if this term is a constant (has no variables)."""
        return not self.args


class Variable(Term):
    """A variable that can match any term."""
    def __init__(self, name: str, is_sequence: bool = False):
        super().__init__(name)
        self.is_sequence = is_sequence  # True for sequence variables like ...α
    
    def __str__(self) -> str:
        if self.is_sequence:
            return f"...{self.name}"
        return self.name
    
    def copy(self) -> "Variable":
        """Create a deep copy of this variable."""
        return Variable(self.name, self.is_sequence)


class EvalTerm(Term):
    """A term that should be evaluated during pattern matching."""
    def __init__(self, term: Term):
        super().__init__("$" + term.name, term.args)
        self.inner_term = term
    
    def __str__(self) -> str:
        inner_str = str(self.inner_term)
        return f"${inner_str}"
    
    def copy(self) -> "EvalTerm":
        """Create a deep copy of this eval term."""
        return EvalTerm(self.inner_term.copy())


class Rule:
    """A rewriting rule that transforms a left-hand side pattern to a right-hand side."""
    def __init__(self, lhs: Term, rhs: Term):
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self) -> str:
        return f"{self.lhs} -> {self.rhs}"


class RewritingSystem:
    """A term rewriting system with pattern matching and rule application."""
    def __init__(self):
        self.rules = []
        self.evaluation_cache = {}  # Cache for term evaluations
        self.debug = False  # Set to True to enable debug prints
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rewriting rule to the system."""
        self.rules.append(rule)
    
    def parse_rules(self, rules_text: str) -> None:
        """Parse multiple rules from a string."""
        rules_lines = [line.strip() for line in rules_text.split('\n') if line.strip()]
        
        for line in rules_lines:
            if '->' not in line:
                continue
                
            lhs_str, rhs_str = line.split('->', 1)
            lhs = self.parse_term(lhs_str.strip())
            rhs = self.parse_term(rhs_str.strip())
            self.add_rule(Rule(lhs, rhs))
    
    def parse_term(self, term_str: str) -> Term:
        """Parse a term from a string representation."""
        term_str = term_str.strip()
        
        # Check for sequence variable
        if term_str.startswith('...'):
            return Variable(term_str[3:], is_sequence=True)
        
        # Check for regular variable (uppercase letters are variables)
        if re.match(r'^[A-Z]$', term_str):
            return Variable(term_str)
        
        # Check for term with arguments
        if '[' in term_str and term_str.endswith(']'):
            name, args_str = term_str.split('[', 1)
            args_str = args_str[:-1]  # Remove closing bracket
            
            # Check for eval term
            if name.startswith('$'):
                inner_name = name[1:]
                args = self.parse_arguments(args_str)
                inner_term = Term(inner_name, args)
                return EvalTerm(inner_term)
            
            args = self.parse_arguments(args_str)
            return Term(name, args)
        
        # Simple term without arguments
        return Term(term_str)
    
    def parse_arguments(self, args_str: str) -> List[Term]:
        """Parse a list of arguments from a string."""
        args = []
        current_arg = ""
        bracket_depth = 0
        
        for char in args_str:
            if char == '[':
                bracket_depth += 1
                current_arg += char
            elif char == ']':
                bracket_depth -= 1
                current_arg += char
            elif char == ' ' and bracket_depth == 0:
                if current_arg:
                    args.append(self.parse_term(current_arg))
                    current_arg = ""
            else:
                current_arg += char
        
        if current_arg:
            args.append(self.parse_term(current_arg))
        
        return args
    
    def log(self, *args, **kwargs):
        """Debug logging."""
        if self.debug:
            print(*args, **kwargs)
            
    def match(self, pattern: Term, term: Term, bindings: Dict[str, Union[Term, List[Term]]] = None) -> Optional[Dict[str, Union[Term, List[Term]]]]:
        """Match a pattern against a term, returning variable bindings if successful."""
        if bindings is None:
            bindings = {}
        else:
            bindings = copy.deepcopy(bindings)
        
        self.log(f"Matching pattern {pattern} against term {term}")
        
        # Handle EvalTerm in the pattern
        if isinstance(pattern, EvalTerm):
            # Replace variables in the inner term with their bindings
            eval_term = self.substitute(pattern.inner_term, bindings)
            self.log(f"Evaluating {pattern} -> {eval_term}")
            
            # Evaluate the term
            evaluated = self.evaluate(eval_term)
            if evaluated is None:
                # Try direct evaluation rules for Succ[X]
                if eval_term.name == "Succ" and len(eval_term.args) == 1:
                    arg = eval_term.args[0]
                    # Find direct Succ rule
                    for rule in self.rules:
                        if (rule.lhs.name == "Succ" and len(rule.lhs.args) == 1 and 
                            rule.lhs.args[0].name == arg.name):
                            evaluated = rule.rhs
                            self.log(f"Direct Succ rule found: {rule.lhs} -> {rule.rhs}")
                            break
                
                if evaluated is None:
                    self.log(f"Evaluation failed for {eval_term}")
                    return None
                
            self.log(f"Evaluated {eval_term} -> {evaluated}")
            
            # For $Succ[A] comparison with a term like 'j'
            if str(evaluated) == str(term):
                self.log(f"Direct match: {evaluated} == {term}")
                return bindings
                
            # If direct comparison fails, try matching
            new_bindings = self.match(evaluated, term, bindings)
            if new_bindings is not None:
                self.log(f"Eval term matches after evaluation")
                return new_bindings
                
            self.log(f"Eval term doesn't match: {evaluated} ≠ {term}")
            return None
        
        # Handle Variable
        if isinstance(pattern, Variable):
            if pattern.is_sequence:
                # Sequence variables are handled in match_args
                if isinstance(term, list):
                    if pattern.name in bindings:
                        if bindings[pattern.name] == term:
                            return bindings
                        return None
                    bindings[pattern.name] = term
                    return bindings
                return None
            else:
                # Regular variables match a single term
                if pattern.name in bindings:
                    # If already bound, it must match the same term
                    if bindings[pattern.name] == term:
                        return bindings
                    return None
                else:
                    # Bind the variable to the term
                    bindings[pattern.name] = term
                    return bindings
        
        # Match Term structures
        if not isinstance(term, Term):
            return None
        
        if pattern.name != term.name:
            return None
        
        # Both pattern and term are non-variable Terms with the same name
        if len(pattern.args) == 0 and len(term.args) == 0:
            return bindings
        
        # Match the arguments
        return self.match_args(pattern.args, term.args, bindings)
    
    def match_args(self, pattern_args: List[Term], term_args: List[Term], bindings: Dict[str, Union[Term, List[Term]]]) -> Optional[Dict[str, Union[Term, List[Term]]]]:
        """Match arguments of a term, handling sequence variables."""
        # Find sequence variables
        seq_vars = [(i, arg) for i, arg in enumerate(pattern_args) 
                   if isinstance(arg, Variable) and arg.is_sequence]
        
        if not seq_vars:
            # No sequence variables, just match arguments one-to-one
            if len(pattern_args) != len(term_args):
                return None
            
            current_bindings = copy.deepcopy(bindings)
            
            for i in range(len(pattern_args)):
                new_bindings = self.match(pattern_args[i], term_args[i], current_bindings)
                if new_bindings is None:
                    return None
                current_bindings = new_bindings
            
            return current_bindings
        
        # Handle case with exactly one sequence variable
        if len(seq_vars) == 1:
            seq_var_idx, seq_var = seq_vars[0]
            
            # Number of fixed arguments before and after the sequence variable
            pre_count = seq_var_idx
            post_count = len(pattern_args) - seq_var_idx - 1
            
            # Make sure we have at least enough arguments
            if len(term_args) < pre_count + post_count:
                return None
            
            # Match prefix
            current_bindings = copy.deepcopy(bindings)
            for i in range(pre_count):
                new_bindings = self.match(pattern_args[i], term_args[i], current_bindings)
                if new_bindings is None:
                    return None
                current_bindings = new_bindings
            
            # Match suffix (from the end)
            for i in range(post_count):
                pattern_idx = len(pattern_args) - 1 - i
                term_idx = len(term_args) - 1 - i
                
                new_bindings = self.match(pattern_args[pattern_idx], term_args[term_idx], current_bindings)
                if new_bindings is None:
                    return None
                current_bindings = new_bindings
            
            # The sequence variable matches everything in the middle
            seq_start = pre_count
            seq_end = len(term_args) - post_count
            seq_value = term_args[seq_start:seq_end]
            
            # Check if the sequence variable is already bound
            if seq_var.name in current_bindings:
                if current_bindings[seq_var.name] != seq_value:
                    return None
            else:
                current_bindings[seq_var.name] = seq_value
            
            return current_bindings
        
        # Multiple sequence variables not supported in this implementation
        self.log("Warning: Multiple sequence variables not supported")
        return None
    
    def substitute(self, term: Term, bindings: Dict[str, Union[Term, List[Term]]]) -> Term:
        """Substitute variables in a term with their bindings."""
        if isinstance(term, Variable):
            if term.name in bindings:
                if term.is_sequence:
                    # Sequence variables expand to multiple terms
                    # But we should return a Term, not a list
                    self.log(f"Expanding sequence variable {term.name} to {bindings[term.name]}")
                    return bindings[term.name]
                else:
                    # Regular variables substitute to a single term
                    self.log(f"Substituting variable {term.name} with {bindings[term.name]}")
                    return copy.deepcopy(bindings[term.name])
            return term.copy()
        
        if isinstance(term, EvalTerm):
            # Recursively substitute in the inner term
            inner_subst = self.substitute(term.inner_term, bindings)
            return EvalTerm(inner_subst)
        
        # Recursively substitute in arguments
        new_args = []
        for arg in term.args:
            if isinstance(arg, Variable) and arg.is_sequence and arg.name in bindings:
                # Expand sequence variables
                self.log(f"Expanding sequence variable {arg.name} in args to {bindings[arg.name]}")
                new_args.extend([copy.deepcopy(t) for t in bindings[arg.name]])
            else:
                new_args.append(self.substitute(arg, bindings))
        
        return Term(term.name, new_args)
    
    def evaluate(self, term: Term) -> Optional[Term]:
        """Evaluate a term by applying rules until no more rules apply."""
        # Use cached result if available
        term_str = str(term)
        if term_str in self.evaluation_cache:
            self.log(f"Using cached evaluation for {term_str}")
            return self.evaluation_cache[term_str]
        
        self.log(f"Evaluating term: {term}")
        
        # Special case for Succ[X] terms
        if term.name == "Succ" and len(term.args) == 1:
            arg = term.args[0]
            # Find direct Succ rule
            for rule in self.rules:
                if (rule.lhs.name == "Succ" and len(rule.lhs.args) == 1 and 
                    rule.lhs.args[0].name == arg.name):
                    result = rule.rhs
                    self.log(f"Direct Succ rule found: {rule.lhs} -> {rule.rhs}")
                    self.evaluation_cache[term_str] = result
                    return result
        
        # Find a rule that applies at the top level
        for i, rule in enumerate(self.rules):
            bindings = self.match(rule.lhs, term, {})
            if bindings is not None:
                self.log(f"Rule {i}: {rule} applies with bindings {bindings}")
                result = self.substitute(rule.rhs, bindings)
                self.log(f"Result after substitution: {result}")
                
                # Also try to further evaluate the result
                final_result = self.evaluate(result)
                if final_result is not None:
                    self.log(f"Final result after further evaluation: {final_result}")
                    self.evaluation_cache[term_str] = final_result
                    return final_result
                
                self.evaluation_cache[term_str] = result
                return result
        
        # If no rule applies at the top level, try to evaluate arguments
        if term.args:
            new_args = []
            changed = False
            
            for arg in term.args:
                evaluated_arg = self.evaluate(arg)
                if evaluated_arg is not None:
                    new_args.append(evaluated_arg)
                    changed = True
                else:
                    new_args.append(arg.copy())
            
            if changed:
                result = Term(term.name, new_args)
                self.log(f"Arguments evaluated: {term} -> {result}")
                
                # Try evaluating again with the new arguments
                final_result = self.evaluate(result)
                if final_result is not None:
                    self.evaluation_cache[term_str] = final_result
                    return final_result
                
                self.evaluation_cache[term_str] = result
                return result
        
        # If nothing changed, return None to indicate no evaluation
        return None
    
    def rewrite(self, term: Term) -> Term:
        """Apply rewriting rules until no more rules apply."""
        current = term
        steps = 0
        max_steps = 50  # Prevent potential infinite loops
        
        self.log(f"Starting rewrite of: {term}")
        
        while steps < max_steps:
            new_term = self.rewrite_once(current)
            if new_term is None:
                self.log(f"No more rules apply. Final result: {current}")
                return current
                
            self.log(f"Step {steps+1}: {current} -> {new_term}")
            
            if str(new_term) == str(current):
                self.log(f"No changes in this step. Final result: {current}")
                return current
                
            current = new_term
            steps += 1
        
        self.log(f"Reached maximum rewrite steps ({max_steps}). Final result: {current}")
        return current
    
    def rewrite_once(self, term: Term) -> Optional[Term]:
        """Apply a single rewriting step."""
        # Try to apply a rule at the top level
        for i, rule in enumerate(self.rules):
            bindings = self.match(rule.lhs, term, {})
            if bindings is not None:
                self.log(f"Rule {i}: {rule} applies to {term} with bindings {bindings}")
                result = self.substitute(rule.rhs, bindings)
                self.log(f"Result after substitution: {result}")
                return result
        
        # If no rule applies at the top level, try to rewrite arguments
        if term.args:
            for i, arg in enumerate(term.args):
                new_arg = self.rewrite_once(arg)
                if new_arg is not None:
                    new_args = [a.copy() for a in term.args]
                    new_args[i] = new_arg
                    result = Term(term.name, new_args)
                    self.log(f"Rewrote argument {i} of {term} -> {result}")
                    return result
        
        # If nothing changed, return None to indicate no rewriting
        return None


# Example usage
def main():
    # Create a rewriting system
    system = RewritingSystem()
    system.debug = True  # Enable debug output
    
    # Add rules
    rules_text = """
    NewWorld[Run[...α] Blank] -> NewWorld[Run[...α] AdvanceLast[...α]]
    Seq[A $Succ[A] ...α] -> Seq[Run[A Succ[A]] ...α]
    Seq[Run[...α A] $Succ[A] ...β] -> Seq[Run[...α A Succ[A]] ...β]
    Seq[Run[...α]] -> Run[...α]
    AdvanceLast[...α A] -> Seq[...α Succ[A]]
    Succ[a] -> b
    Succ[b] -> c
    Succ[c] -> d
    Succ[d] -> e
    Succ[e] -> f
    Succ[f] -> g
    Succ[g] -> h
    Succ[h] -> i
    Succ[i] -> j
    Succ[j] -> k
    Succ[k] -> l
    Succ[l] -> m
    Succ[m] -> n
    Succ[n] -> o
    Succ[o] -> p
    Succ[p] -> q
    Succ[q] -> r
    Succ[r] -> s
    Succ[s] -> t
    Succ[t] -> u
    Succ[u] -> v
    Succ[v] -> w
    Succ[w] -> x
    Succ[x] -> y
    Succ[y] -> z
    """
    
    system.parse_rules(rules_text)
    
    # Parse the input term
    input_term = system.parse_term("NewWorld[Seq[i j k] Blank]")
    print("Input:", input_term)
    
    # Let's trace through the intermediate steps manually
    print("\n=== Manual Tracing ===")
    
    # Step 1: Apply Seq[A $Succ[A] ...α] -> Seq[Run[A Succ[A]] ...α]
    # This should convert Seq[i j k] to Seq[Run[i j] k]
    seq_i_j_k = system.parse_term("Seq[i j k]")
    step1_rule = system.rules[1]  # The second rule in our list
    bindings1 = system.match(step1_rule.lhs, seq_i_j_k, {})
    if bindings1:
        step1_result = system.substitute(step1_rule.rhs, bindings1)
        print("Step 1: Seq[i j k] ->", step1_result)
        
        # Step 2: Apply Seq[Run[...α A] $Succ[A] ...β] -> Seq[Run[...α A Succ[A]] ...β]
        # This should convert Seq[Run[i j] k] to Seq[Run[i j k]]
        step2_rule = system.rules[2]  # The third rule in our list
        bindings2 = system.match(step2_rule.lhs, step1_result, {})
        if bindings2:
            step2_result = system.substitute(step2_rule.rhs, bindings2)
            print("Step 2:", step1_result, "->", step2_result)
            
            # Step 3: Apply Seq[Run[...α]] -> Run[...α]
            # This should convert Seq[Run[i j k]] to Run[i j k]
            step3_rule = system.rules[3]  # The fourth rule in our list
            bindings3 = system.match(step3_rule.lhs, step2_result, {})
            if bindings3:
                step3_result = system.substitute(step3_rule.rhs, bindings3)
                print("Step 3:", step2_result, "->", step3_result)
                
                # Now we should have Run[i j k]
                print("Final manual result:", step3_result)
            else:
                print("Step 3 failed to match")
        else:
            print("Step 2 failed to match")
    else:
        print("Step 1 failed to match")
    
    print("\n=== Automatic Rewriting ===")
    # Apply the rewriting rules
    output_term = system.rewrite(input_term)
    print("Output:", output_term)
    
    # Expected: NewWorld[Seq[i j k] Seq[i j l]]
    expected = system.parse_term("NewWorld[Seq[i j k] Seq[i j l]]")
    print("Expected:", expected)
    print("Matches expected:", output_term == expected)
    
    # Test if we can convert Seq[i j k] to Run[i j k]
    print("\n=== Testing Seq to Run conversion ===")
    seq_term = system.parse_term("Seq[i j k]")
    run_result = system.rewrite(seq_term)
    print("Seq[i j k] rewrites to:", run_result)
    expected_run = system.parse_term("Run[i j k]")
    print("Should be:", expected_run)
    print("Matches expected:", run_result == expected_run)


if __name__ == "__main__":
    main()
