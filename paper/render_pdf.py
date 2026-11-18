"""Render the accompanying, deliberately simple methods-paper Markdown.

Optional document-build dependency: ReportLab. This is not needed to run the
auditor. Fonts are resolved locally; no fonts or resources are downloaded.
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted,
)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "A_Citation_Is_Not_a_Check_v0.1.0.md"
OUTPUT = ROOT / "A_Citation_Is_Not_a_Check_v0.1.0.pdf"
INK, SECONDARY = colors.HexColor("#2C2C2B"), colors.HexColor("#525860")
BLUE, SURFACE, BORDER = colors.HexColor("#25634C"), colors.HexColor("#F0F7F2"), colors.HexColor("#D9DFE5")
WIDTH = 480


def fonts():
    options = [
        (Path("/usr/share/fonts/msttcore/arial.ttf"), Path("/usr/share/fonts/msttcore/arialbd.ttf")),
        (Path("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"), Path("/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf")),
        (Path("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"), Path("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in options:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("PaperSans", str(regular)))
            pdfmetrics.registerFont(TTFont("PaperSansBold", str(bold)))
            pdfmetrics.registerFontFamily("PaperSans", normal="PaperSans", bold="PaperSansBold",
                                         italic="PaperSans", boldItalic="PaperSansBold")
            return "PaperSans"
    raise SystemExit("A local Arial or DejaVu Sans font pair is required; no font is downloaded.")


FONT = fonts()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("PaperTitle", fontName="PaperSansBold", fontSize=24, leading=27,
                         textColor=INK, spaceAfter=14))
styles.add(ParagraphStyle("PaperH2", fontName="PaperSansBold", fontSize=16.5, leading=21,
                         textColor=INK, spaceBefore=6, spaceAfter=10, keepWithNext=True))
styles.add(ParagraphStyle("PaperH3", fontName="PaperSansBold", fontSize=12, leading=15.5,
                         textColor=BLUE, spaceBefore=8, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle("PaperBody", fontName=FONT, fontSize=10.2, leading=13.2,
                         textColor=INK, spaceAfter=5, alignment=TA_LEFT))
styles.add(ParagraphStyle("PaperReference", parent=styles["PaperBody"],
                         fontSize=9.3, leading=11.6, spaceAfter=4))
styles.add(ParagraphStyle("PaperBullet", parent=styles["PaperBody"], leftIndent=13,
                         firstLineIndent=0, bulletIndent=0, spaceAfter=5))
styles.add(ParagraphStyle("PaperCell", fontName=FONT, fontSize=9.5, leading=12.2, textColor=INK))
styles.add(ParagraphStyle("PaperCellHead", parent=styles["PaperCell"], fontName="PaperSansBold"))
styles.add(ParagraphStyle("PaperCallout", parent=styles["PaperBody"], fontSize=10.5, leading=14, spaceAfter=0))
styles.add(ParagraphStyle("PaperCode", fontName="Courier", fontSize=10, leading=14,
                         textColor=INK, backColor=colors.HexColor("#F7F8F9"),
                         borderPadding=10, spaceBefore=5, spaceAfter=13))


CITATIONS = {
    "https://aclanthology.org/2025.acl-industry.23.pdf": 1,
    "https://aclanthology.org/2026.evaleval-1.35.pdf": 2,
    "https://arxiv.org/html/2605.08583v3": 3,
}


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\[\^(https?://[^\]]+)\]", lambda m:
                  '<super><link href="' + m.group(1) + '">['
                  + str(CITATIONS[m.group(1)]) + ']</link></super>', text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#25634C">\1</link>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="10">\1</font>', text)
    return text


def page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SECONDARY)
    canvas.setFont(FONT, 9)
    canvas.drawString(66, 759, "QUOTELEDGER")
    canvas.drawRightString(546, 759, "WORKING METHODS DRAFT  /  v0.1.0")
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(66, 748, 546, 748)
    canvas.drawString(66, 29, "Aaron Michael Weis (ΩNeiron™)  ·  Research draft")
    canvas.drawRightString(546, 29, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Output already exists; select a new PDF path.")
    lines = args.source.read_text(encoding="utf-8").splitlines()
    story = []
    index = 0
    references = False
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line == "<!-- PAGE -->":
            story.append(PageBreak())
            index += 1
            continue
        if line.startswith("```"):
            index += 1
            code = []
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            story.append(Preformatted("\n".join(code), styles["PaperCode"]))
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            widths = ([145, 335] if len(rows[0]) == 2 else
                      [150, 75, 255] if len(rows[0]) == 3 else
                      [WIDTH / len(rows[0])] * len(rows[0]))
            cells = [[Paragraph(inline(cell), styles["PaperCellHead" if row_number == 0 else "PaperCell"])
                      for cell in row] for row_number, row in enumerate(rows)]
            table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
                ("LINEBELOW", (0, 0), (-1, 0), 0.8, BORDER),
                ("LINEBELOW", (0, 1), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([table, Spacer(1, 12)])
            continue
        if line.startswith("> "):
            callout = Table([[Paragraph(inline(line[2:]), styles["PaperCallout"])]], colWidths=[WIDTH])
            callout.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
                ("LEFTPADDING", (0, 0), (-1, -1), 13),
                ("RIGHTPADDING", (0, 0), (-1, -1), 13),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.extend([callout, Spacer(1, 14)])
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["PaperTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["PaperH2"]))
        elif line.startswith("### "):
            if line == "### Selected references":
                references = True
            story.append(Paragraph(inline(line[4:]), styles["PaperH3"]))
        elif line.startswith("- "):
            story.append(Paragraph(inline(line[2:]), styles["PaperBullet"], bulletText="•"))
        else:
            parts = [line]
            while index + 1 < len(lines) and lines[index + 1].strip() and not lines[index + 1].startswith(("#", "|", ">", "```", "- ", "<!--")):
                index += 1
                parts.append(lines[index])
            story.append(Paragraph(inline(" ".join(parts)),
                                   styles["PaperReference" if references else "PaperBody"]))
        index += 1
    document = SimpleDocTemplate(
        str(args.output), pagesize=letter, leftMargin=66, rightMargin=66,
        topMargin=66, bottomMargin=55,
        title="A Citation Is Not a Check: Evidence Depth and Snapshot-Bound Quotations for AI Research",
        author="Aaron Michael Weis (ΩNeiron™)",
        subject="Working methods draft accompanying QuoteLedger v0.1.0",
    )
    document.build(story, onFirstPage=page, onLaterPages=page)
    print(args.output.name)


if __name__ == "__main__":
    main()