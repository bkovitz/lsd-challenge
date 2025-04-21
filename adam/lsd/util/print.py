def print_table(rows: list[list[str]], headers: list[str], align: str = "left") -> None:
    """Print a table with aligned columns."""
    cols = len(headers)
    valid_rows = [row for row in rows if len(row) == cols]
    if not valid_rows:
        return

    str_rows = [[str(cell) for cell in row] for row in valid_rows]
    str_headers = [str(h) for h in headers]
    widths = [
        max(len(str_headers[i]), max((len(row[i]) for row in str_rows), default=0))
        for i in range(cols)
    ]

    align_fn = str.rjust if align == "right" else str.center if align == "center" else str.ljust
    print(" | ".join(align_fn(str_headers[i], widths[i]) for i in range(cols)))
    print("-" * (sum(widths) + 3 * (cols - 1)))
    for row in str_rows:
        print(" | ".join(align_fn(cell, widths[i]) for i, cell in enumerate(row)))
