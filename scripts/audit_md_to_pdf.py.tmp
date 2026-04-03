#!/usr/bin/env python3
"""Render the senior counsel audit memo Markdown into a formatted color PDF.

- Pipe-tables become real ReportLab tables (no raw | markdown).
- Inline **bold**, *italic*, and `code` become proper paragraph markup (no raw **).
- Nested bullet lists get indentation.
- Status column uses colored text plus light row tint (visible even in grayscale print preview).
- Emoji traffic lights become small colored bullets (PDF standard fonts rarely render emoji).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DEFAULT_MD = Path("audit_reports/senior_counsel_audit_2022_2026.md")
DEFAULT_PDF = Path("audit_reports/senior_counsel_audit_2022_2026.pdf")

COLOR_GREEN = colors.HexColor("#0d6e3d")
COLOR_YELLOW = colors.HexColor("#b8860b")
COLOR_HEADER_BG = colors.HexColor("#2c3e50")
COLOR_H2 = colors.HexColor("#1a5276")
COLOR_H3 = colors.HexColor("#2471a3")
COLOR_RULE = colors.HexColor("#3498db")
ROW_GREEN = colors.HexColor("#e8f6ef")
ROW_YELLOW = colors.HexColor("#fff8e6")


def _replace_emoji_status_markers(s: str) -> str:
    """Map emoji to colored Unicode bullets (standard fonts usually include U+25CF)."""
    return (
        s.replace("🟢", '<font color="#0d6e3d">●</font>')
        .replace("🟡", '<font color="#b8860b">●</font>')
        .replace("🔴", '<font color="#b22222">●</font>')
    )


def _inline_md_to_paragraph_xml(text: str) -> str:
    """Convert common Markdown inline to ReportLab paragraph XML."""
    s = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = _replace_emoji_status_markers(s)
    # Bold must be applied before italic (*...*) parsing.
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", s)
    # Italic: single asterisks, not adjacent to another asterisk (avoids **).
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = s.replace("§", "Sec. ")
    return s


def _status_color(cell: str) -> object | None:
    t = cell.strip()
    if "🟡" in t or "yellow" in t.lower():
        return COLOR_YELLOW
    if "🟢" in t or t.lower().startswith("green") or "green" in t.lower():
        return COLOR_GREEN
    if "🔴" in t or "red" in t.lower():
        return colors.HexColor("#b22222")
    return None


def _row_status_tint(status_cell: str) -> object | None:
    """Background tint for full table row based on Status column text."""
    t = status_cell.lower()
    if "yellow" in t or "🟡" in status_cell:
        return ROW_YELLOW
    if "green" in t or "🟢" in status_cell:
        return ROW_GREEN
    return None


def _normalize_status_cell_for_pdf(cell: str) -> str:
    t = cell.strip()
    t = re.sub(r"[🟢🟡🔴]", "", t).strip()
    t = re.sub(r"^\*\*(.+?)\*\*$", r"\1", t)
    if not t and any(e in cell for e in ("🟢", "🟡", "🔴")):
        for ch, label in (("🟢", "Green"), ("🟡", "Yellow"), ("🔴", "Red")):
            if ch in cell:
                return label
    return t if t else cell


def _build_table(
    header: list[str],
    rows: list[list[str]],
    styles: object,
    col_widths: list[float] | None = None,
) -> Table:
    try:
        status_idx = next(i for i, h in enumerate(header) if h.strip().lower() == "status")
    except StopIteration:
        status_idx = -1

    body_style = ParagraphStyle(
        name="TblBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    hdr_style = ParagraphStyle(
        name="TblHdr",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_LEFT,
    )

    def p_cell(text: str, style: ParagraphStyle, fg: object | None = None) -> Paragraph:
        st: ParagraphStyle = style
        if fg is not None:
            st = ParagraphStyle(name=style.name + "_c", parent=style, textColor=fg)
        return Paragraph(_inline_md_to_paragraph_xml(text), st)

    data: list[list[object]] = []
    data.append([p_cell(c, hdr_style, colors.white) for c in header])

    row_tints: list[object | None] = [None]
    for row in rows:
        out_row: list[object] = []
        tint = _row_status_tint(row[status_idx]) if 0 <= status_idx < len(row) else None
        row_tints.append(tint)
        for j, cell in enumerate(row):
            if j == status_idx and status_idx >= 0:
                fg = _status_color(cell)
                disp = _normalize_status_cell_for_pdf(cell)
                out_row.append(p_cell(disp, body_style, fg or colors.black))
            else:
                out_row.append(p_cell(cell.strip(), body_style))
        data.append(out_row)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    base_ts: list[tuple] = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#bdc3c7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        tint = row_tints[i]
        if tint is not None:
            base_ts.append(("BACKGROUND", (0, i), (-1, i), tint))
        elif i % 2 == 0:
            base_ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f4f6f8")))
    t.setStyle(TableStyle(base_ts))
    return t


def _heading_indent(line: str) -> int:
    """Return number of leading spaces before list marker (- or *)."""
    return len(line) - len(line.lstrip(" "))


def _is_list_line(line: str) -> bool:
    s = line.lstrip(" ")
    return s.startswith("- ") or s.startswith("* ")


def _list_content(line: str) -> str:
    s = line.lstrip(" ")
    return s[2:].strip()


def markdown_audit_to_pdf(md_path: Path, pdf_path: Path) -> None:
    raw = md_path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleDoc",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        spaceAfter=12,
        textColor=COLOR_H2,
    )
    h2_style = ParagraphStyle(
        name="H2Doc",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
        textColor=COLOR_H2,
    )
    h3_style = ParagraphStyle(
        name="H3Doc",
        parent=styles["Heading3"],
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=6,
        textColor=COLOR_H3,
    )
    body_style = ParagraphStyle(
        name="AuditBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
    )

    story: list = []
    page_w = letter[0] - 1.5 * inch
    col3 = [page_w * 0.26, page_w * 0.12, page_w * 0.62]

    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            story.append(Spacer(1, 6))
            i += 1
            continue

        if line.startswith("|"):
            block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            if len(block) < 2:
                story.append(Paragraph(_inline_md_to_paragraph_xml(block[0]), body_style))
                continue

            def split_row(s: str) -> list[str]:
                return [p.strip() for p in s.strip().strip("|").split("|")]

            parsed = [split_row(r) for r in block]
            header = parsed[0]

            def _is_separator_row(cells: list[str]) -> bool:
                if not cells:
                    return False
                return all(
                    bool(re.fullmatch(r":?-{3,}:?", c.strip().replace(" ", ""))) for c in cells
                )

            rest_start = 1
            if len(parsed) > 1 and _is_separator_row(parsed[1]):
                rest_start = 2
            rows = parsed[rest_start:]
            twidths = None
            ncols = len(header)
            if ncols == 3:
                twidths = col3
            elif ncols == 6:
                twidths = [page_w / 6.0] * 6
            elif ncols == 2:
                twidths = [page_w * 0.22, page_w * 0.78]
            else:
                twidths = [page_w / float(ncols)] * ncols

            story.append(_build_table(header, rows, styles, col_widths=twidths))
            story.append(Spacer(1, 10))
            continue

        if line.startswith("### "):
            story.append(Paragraph(_inline_md_to_paragraph_xml(line[4:]), h3_style))
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(_inline_md_to_paragraph_xml(line[3:]), h2_style))
            i += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(_inline_md_to_paragraph_xml(line[2:]), title_style))
            i += 1
            continue

        if line.strip().startswith("---"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width=page_w, thickness=1.5, color=COLOR_RULE, spaceBefore=6, spaceAfter=10))
            i += 1
            continue

        if _is_list_line(line):
            while i < len(lines) and lines[i].strip() and _is_list_line(lines[i]):
                ind = _heading_indent(lines[i])
                nest = max(ind // 2, 0)
                content = _list_content(lines[i])
                bullet_style = ParagraphStyle(
                    name=f"Bullet_{nest}_{len(story)}",
                    parent=body_style,
                    leftIndent=18 + nest * 16,
                    firstLineIndent=-10,
                    bulletIndent=8 + nest * 16,
                )
                story.append(
                    Paragraph(
                        _inline_md_to_paragraph_xml(content),
                        bullet_style,
                        bulletText="•",
                    )
                )
                i += 1
            story.append(Spacer(1, 6))
            continue

        story.append(Paragraph(_inline_md_to_paragraph_xml(line.strip()), body_style))
        i += 1

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=md_path.stem,
    )
    doc.build(story)


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert audit markdown memo to formatted color PDF.")
    ap.add_argument("markdown", nargs="?", type=Path, default=DEFAULT_MD)
    ap.add_argument("--out", type=Path, default=DEFAULT_PDF)
    args = ap.parse_args()
    markdown_audit_to_pdf(args.markdown.expanduser().resolve(), args.out.expanduser().resolve())
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
