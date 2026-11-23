"""Static feature extraction for Python functions."""

from __future__ import annotations

import ast
import hashlib
import io
import textwrap
import tokenize
from dataclasses import dataclass


FEATURE_NAMES = ("nloc", "parameter_count", "branch_count")
FEATURE_LABELS = {
    "nloc": "Non-comment LOC",
    "parameter_count": "Jumlah parameter",
    "branch_count": "Jumlah percabangan",
}


class CodeFormatError(ValueError):
    """Raised when Python source cannot be parsed."""


@dataclass(frozen=True)
class ExtractedFunction:
    name: str
    code: str
    line_start: int
    line_end: int
    nloc: int
    parameter_count: int
    branch_count: int

    @property
    def features(self) -> dict[str, int]:
        return {
            "nloc": self.nloc,
            "parameter_count": self.parameter_count,
            "branch_count": self.branch_count,
        }

    @property
    def code_hash(self) -> str:
        normalized = textwrap.dedent(self.code).strip()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _significant_line_count(source: str) -> int:
    """Count physical lines that contain meaningful Python tokens."""
    meaningful_lines: set[int] = set()
    ignored = {
        tokenize.COMMENT,
        tokenize.ENCODING,
        tokenize.ENDMARKER,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.NEWLINE,
        tokenize.NL,
    }
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if token.type not in ignored and token.string.strip():
                meaningful_lines.add(token.start[0])
    except (IndentationError, tokenize.TokenError):
        return sum(
            1
            for line in source.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    return max(1, len(meaningful_lines))


def _parameter_count(arguments: ast.arguments) -> int:
    return (
        len(arguments.posonlyargs)
        + len(arguments.args)
        + len(arguments.kwonlyargs)
        + int(arguments.vararg is not None)
        + int(arguments.kwarg is not None)
    )


class _BranchCounter(ast.NodeVisitor):
    """Count control-flow decisions while excluding nested functions."""

    def __init__(self, root: ast.AST) -> None:
        self.root = root
        self.count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node is self.root:
            self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node is self.root:
            self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_MatchCase(self, node: ast.match_case) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.count += max(0, len(node.values) - 1)
        self.generic_visit(node)


def _branch_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    counter = _BranchCounter(node)
    counter.visit(node)
    return counter.count


def _collect_functions(
    module: ast.Module,
) -> list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, str]]:
    found: list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, str]] = []

    def visit_body(body: list[ast.stmt], class_prefix: str = "") -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{class_prefix}{node.name}" if class_prefix else node.name
                found.append((node, name))
            elif isinstance(node, ast.ClassDef):
                prefix = f"{class_prefix}{node.name}." if class_prefix else f"{node.name}."
                visit_body(node.body, prefix)

    visit_body(module.body)
    return found


def _build_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    name: str,
    code: str,
) -> ExtractedFunction:
    clean_code = textwrap.dedent(code).strip()
    return ExtractedFunction(
        name=name,
        code=clean_code,
        line_start=node.lineno,
        line_end=getattr(node, "end_lineno", node.lineno),
        nloc=_significant_line_count(clean_code),
        parameter_count=_parameter_count(node.args),
        branch_count=_branch_count(node),
    )


def extract_functions(source: str) -> list[ExtractedFunction]:
    """Extract top-level functions and class methods from Python source.

    Plain statements without a function declaration are treated as one synthetic
    function so that short snippets can still be analyzed in the web interface.
    """
    normalized = textwrap.dedent(source.replace("\r\n", "\n")).strip("\n")
    if not normalized.strip():
        raise CodeFormatError("Kode Python masih kosong.")

    try:
        module = ast.parse(normalized)
    except SyntaxError as exc:
        location = f"baris {exc.lineno}" if exc.lineno else "lokasi tidak diketahui"
        raise CodeFormatError(f"SyntaxError pada {location}: {exc.msg}") from exc

    functions = _collect_functions(module)
    if functions:
        extracted = []
        for node, name in functions:
            segment = ast.get_source_segment(normalized, node)
            if not segment:
                lines = normalized.splitlines()
                segment = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            extracted.append(_build_function(node, name, segment))
        return extracted

    indented = "\n".join(f"    {line}" if line.strip() else "" for line in normalized.splitlines())
    wrapper = f"def __input_snippet__():\n{indented}\n"
    try:
        wrapped_module = ast.parse(wrapper)
    except SyntaxError as exc:
        raise CodeFormatError(f"Cuplikan Python tidak valid: {exc.msg}") from exc

    wrapper_node = wrapped_module.body[0]
    return [
        ExtractedFunction(
            name="__input_snippet__",
            code=normalized,
            line_start=1,
            line_end=max(1, len(normalized.splitlines())),
            nloc=_significant_line_count(normalized),
            parameter_count=0,
            branch_count=_branch_count(wrapper_node),
        )
    ]

