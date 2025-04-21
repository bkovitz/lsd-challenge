from term import *


# undo_seq_rule = Rule(
#     Seq([Node(Atom("Succ"), (Var("ARG"),))], True),
#     Seq([Node(Atom("Undo"), (Var("ARG"),))], True),
# )

# Rules from March 19, 2025 notes (New World Pons Asinorum)

succ_run_rule = Rule(
    Seq([Atom("A"), Node(Atom("Succ"), (Atom("A"),)), Var("α")], True),
    Seq(
        [
            Node(
                Atom("Run"),
                (Atom("A"), Node(Atom("Succ"), (Atom("A"),))),
            ),
            Var("α"),
        ],
        True,
    ),
)

flatten_run_rule = Rule(
    Seq([Node(Atom("Run"), (Seq([Var("α")], True),))]),
    Node(Atom("Run"), (Seq([Var("α")], True),)),
)

advance_last_rule = Rule(
    Node(Atom("AdvanceLast"), (Seq([Var("α")], True), Atom("A"))),
    Seq([Seq([Var("α")], True), Node(Atom("Succ"), (Atom("A"),))]),
)

# Rules from March 18, 2025 notes (Painting Canvas) - Simplified
paint_first_rule = Rule(
    Node(
        Atom("Paint"),
        (
            Node(Atom("Chunk"), (Node(Atom("FirstItem"), (Var("X"),)), Var("α"))),
            Seq([Var("β")], True),
        ),
    ),
    Node(
        Atom("Paint"),
        (Node(Atom("Chunk"), (Var("α"),)), Seq([Var("X"), Var("β")], True)),
    ),
)

# paint_length_rule = Rule(
#     Node(Atom("Paint"), (Node(Atom("Chunk"), (Atom(f"Length[{N}]"), Var("α"))), Atom("Blank"))),
#     Node(Atom("Paint"), (Node(Atom("Chunk"), (Var("α"),)), Seq([Atom("_")] * N)))
# )

if __name__ == "__main__":
    # Test Sequence Variable Rules (March 31)
    term1 = Node(Atom("Succ"), (Seq([Atom("a"), Atom("b"), Atom("c")]),))
    print("Seq Rule Test:", rewrite(term1, [succ_seq_rule]))

    term2 = Seq(
        [
            Node(Atom("Succ"), (Atom("a"),)),
            Node(Atom("Succ"), (Atom("b"),)),
            Node(Atom("Succ"), (Atom("c"),)),
        ]
    )
    print("Undo Rule Test:", rewrite(term2, [undo_seq_rule]))

    # Test New World Rules (March 19)
    new_world_term = Node(
        Atom("NewWorld"), (Seq([Atom("i"), Atom("j"), Atom("k")]), Atom("Blank"))
    )
    new_world_rules = [
        new_world_rule,
        succ_run_rule,
        # extend_run_rule,
        flatten_run_rule,
        advance_last_rule,
    ]
    print("New World Test:", rewrite(new_world_term, new_world_rules))

    # Test Painting Rules (March 18)
    paint_term = Node(
        Atom("Paint"),
        (
            Node(
                Atom("Chunk"),
                (Node(Atom("FirstItem"), (Atom("a"),)), Atom("Length[5]")),
            ),
            Atom("Blank"),
        ),
    )
    paint_rules = [
        paint_first_rule,
        # paint_length_rule,
    ]
    print("Paint Test:", rewrite(paint_term, paint_rules))
