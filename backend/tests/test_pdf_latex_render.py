"""Tests for PDF LaTeX rendering."""

from app.services.pdf_latex_render import render_mixed_latex_for_pdf


def test_newline_and_backslash_newline_become_line_breaks():
    tex = render_mixed_latex_for_pdf(
        "Given:\\nAll mammals are warm-blooded.\\newline Therefore B."
    )
    assert "\\textbackslash{}newline" not in tex
    assert "\\\\" in tex
    assert "Given:" in tex


def test_no_triple_dollar_from_display_math():
    tex = render_mixed_latex_for_pdf(
        "Data: $$\\text{Apple: } 35 \\quad \\text{Banana: } 25$$"
    )
    assert "$$$" not in tex
    assert "\\[" in tex or "\\(" in tex


def test_analogy_stem_renders_safely():
    tex = render_mixed_latex_for_pdf("Book : Page :: Letter : ?")
    assert "$$$" not in tex
    assert "Book" in tex


def test_percent_in_prose_is_escaped():
    tex = render_mixed_latex_for_pdf("Discount = 25% of total")
    assert "25\\%" in tex
