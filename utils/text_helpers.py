"""Text normalization helpers for project browser tree labels."""


def normalize_tree_label(text: str) -> str:
    """Normalize tree labels that may span multiple lines."""
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def search_query_for_name(name: str) -> str:
    """Build a single-line search query (search box does not accept newlines well)."""
    lines = [line.strip() for line in name.splitlines() if line.strip()]
    return lines[0] if lines else name.strip()
