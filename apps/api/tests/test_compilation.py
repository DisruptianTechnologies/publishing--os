import io
import zipfile
import pytest
from services.compilation_service import generate_epub3_archive, generate_print_pdf_6x9
from services.cover_service import calculate_cover_dimensions, generate_cover_art_prompt
from services.chapter_service import assist_chapter_draft, calculate_readability


def test_epub_generation_valid_structure():
    chapters = [
        {"title": "Chapter 1: The Attention Paradox", "content": "Paragraph 1 text.\n\nParagraph 2 text."},
        {"title": "Chapter 2: Deep Work Waves", "content": "Rhythm and focus."},
    ]
    epub_bytes = generate_epub3_archive(
        title="Mindful Productivity",
        author="Kindlepreneur Author",
        chapters=chapters
    )
    assert epub_bytes.startswith(b"PK")
    
    zf = zipfile.ZipFile(io.BytesIO(epub_bytes))
    file_list = zf.namelist()
    
    # 1. mimetype must be the very first entry per EPUB 3 spec
    assert file_list[0] == "mimetype"
    assert zf.read("mimetype") == b"application/epub+zip"
    
    # 2. Required EPUB 3 container and package files
    assert "META-INF/container.xml" in file_list
    assert "OEBPS/content.opf" in file_list
    assert "OEBPS/nav.xhtml" in file_list
    assert "OEBPS/chapter_1.xhtml" in file_list
    assert "OEBPS/chapter_2.xhtml" in file_list
    assert "OEBPS/style.css" in file_list


def test_pdf_generation_valid_pdf14_header():
    chapters = [
        {"title": "Chapter 1: Introduction", "content": "Focus in an age of distractions."}
    ]
    pdf_bytes = generate_print_pdf_6x9(
        title="Mindful Productivity",
        author="Kindlepreneur Author",
        chapters=chapters
    )
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"%%EOF" in pdf_bytes
    assert b"/MediaBox [0 0 432 648]" in pdf_bytes  # 6x9 inches in points


def test_cover_dimension_math():
    # 164 pages on white paper
    dims = calculate_cover_dimensions(page_count=164, trim_size="6x9", paper_type="white")
    assert dims["page_count"] == 164
    assert dims["trim_size"] == "6x9"
    # Spine width: 164 * 0.002252 = 0.3693
    assert dims["spine_width_inches"] == 0.3693
    # Total width: 0.125 + 6.0 + 0.3693 + 6.0 + 0.125 = 12.6193
    assert dims["total_width_inches"] == 12.6193
    assert dims["total_height_inches"] == 9.25  # 9.0 + 0.125*2
    assert dims["can_print_spine_text"] is True
    assert dims["barcode_box"]["width_inches"] == 2.0


def test_cover_cream_paper_dimension():
    # 200 pages on cream paper: 200 * 0.0025 = 0.50 inches
    dims = calculate_cover_dimensions(page_count=200, trim_size="6x9", paper_type="cream")
    assert dims["spine_width_inches"] == 0.5
    assert dims["total_width_inches"] == 12.75


def test_cover_prompt_generator():
    prompt_res = generate_cover_art_prompt(
        title="Mindful Productivity",
        genre="productivity",
        visual_style="minimalist_editorial"
    )
    assert "Mindful Productivity" in prompt_res["prompt"]
    assert "blurry" in prompt_res["negative_prompt"]
    assert prompt_res["aspect_ratio"] == "1:1.5"


def test_trope_removal_and_readability():
    text = "In conclusion, we must delve into the tapestry of deep work. It is crucial to remember this fact."
    res = assist_chapter_draft(action="polish_active_voice", text=text)
    assert "delve into" not in res["improved_text"].lower()
    assert "tapestry" not in res["improved_text"].lower()
    assert len(res["metrics_after"]["trope_flags"]) == 0


def test_editorial_qa_critique():
    text = "The system was configured by the user, and an audit was conducted by the compliance engine."
    res = assist_chapter_draft(action="run_editorial_qa", text=text)
    assert "findings" in res
    assert len(res["findings"]) > 0
