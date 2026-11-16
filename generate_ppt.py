import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_accura_presentation(output_path="DataGuard_AI_Project_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette Constants
    NAVY = RGBColor(15, 23, 42)        # #0F172A (Deep Slate/Navy)
    BLUE = RGBColor(37, 99, 235)       # #2563EB (Primary Accent)
    DARK_BLUE = RGBColor(30, 58, 138)  # #1E3A8A (Header Primary)
    SLATE = RGBColor(71, 85, 105)      # #475569 (Secondary Text)
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC (Card Background)
    WHITE = RGBColor(255, 255, 255)
    EMERALD = RGBColor(5, 150, 105)    # #059669 (Success Accent)
    PURPLE = RGBColor(124, 58, 237)    # #7C3AED (AI Accent)
    BORDER_COLOR = RGBColor(226, 232, 240) # Slate-200

    def add_header(slide, title_text, category_text="DATAGUARD AI RESEARCH & IMPLEMENTATION"):
        # Category pill / banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = BLUE

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def add_card(slide, left, top, width, height, bg_color=LIGHT_BG, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide (Dark Theme)
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(3.0))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "IEEE ACCESS RESEARCH PROJECT PRESENTATION"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(96, 165, 250)
    p0.space_after = Pt(12)

    p1 = tf1.add_paragraph()
    p1.text = "DATAGUARD AI: Detecting Structural Inconsistencies\nin Migration Datasets Using GPT-4o"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(16)

    p2 = tf1.add_paragraph()
    p2.text = "Comprehensive Methodology, Layered Architecture, Development Methods & Step-by-Step User Guide"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(203, 213, 225)

    # Metadata card at bottom
    add_card(s1, Inches(1.0), Inches(5.0), Inches(11.3), Inches(1.6), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(5.1), Inches(10.9), Inches(1.4))
    tf_meta = meta_box.text_frame
    tf_meta.word_wrap = True
    
    pm1 = tf_meta.paragraphs[0]
    pm1.text = "Base Paper: IEEE Access, vol. 14, 2026 | DOI: 10.1109/ACCESS.2026.3723358"
    pm1.font.size = Pt(12)
    pm1.font.bold = True
    pm1.font.color.rgb = WHITE

    pm2 = tf_meta.add_paragraph()
    pm2.text = "Original Authors: Deyvid J. Guevara, Gwyneth L. Segura, and José Santisteban (UPC, Lima, Peru)"
    pm2.font.size = Pt(11)
    pm2.font.color.rgb = RGBColor(148, 163, 184)

    pm3 = tf_meta.add_paragraph()
    pm3.text = "Case Study: Inventiva Insurtech Solutions S.A.C. | Evaluated over 400,779 migration records across 4 templates"
    pm3.font.size = Pt(11)
    pm3.font.color.rgb = RGBColor(148, 163, 184)

    # -------------------------------------------------------------------------
    # SLIDE 2: Problem Statement & Motivation
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "The Critical Problem in Data Migration & Quality Assurance", "Industry Background & Motivation")

    # 4 Stat Cards
    stats = [
        ("84%", "Project Failure Rate", "Migration projects that fail to meet initial business expectations due to data flaws.", BLUE),
        ("37%", "Cost Overruns", "Projects incurring massive unexpected financial burdens during modernization.", RGBColor(225, 29, 72)),
        ("67%", "Delivery Delays", "Migrations delayed due to tedious manual data cleansing iterations.", RGBColor(217, 119, 6)),
        ("$600B", "Annual Global Losses", "Estimated enterprise losses directly attributed to inaccurate business data.", DARK_BLUE)
    ]

    for i, (stat, title, desc, col) in enumerate(stats):
        x = Inches(0.8 + i * 2.95)
        add_card(s2, x, Inches(1.7), Inches(2.8), Inches(2.2))
        sb = s2.shapes.add_textbox(x + Inches(0.2), Inches(1.9), Inches(2.4), Inches(1.8))
        tf = sb.text_frame
        tf.word_wrap = True
        p_st = tf.paragraphs[0]
        p_st.text = stat
        p_st.font.size = Pt(32)
        p_st.font.bold = True
        p_st.font.color.rgb = col
        
        p_tit = tf.add_paragraph()
        p_tit.text = title
        p_tit.font.size = Pt(12)
        p_tit.font.bold = True
        p_tit.font.color.rgb = NAVY
        p_tit.space_before = Pt(4)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = SLATE
        p_desc.space_before = Pt(4)

    # Comparison Bottom Card
    add_card(s2, Inches(0.8), Inches(4.2), Inches(11.7), Inches(2.6))
    comp_box = s2.shapes.add_textbox(Inches(1.1), Inches(4.4), Inches(11.1), Inches(2.2))
    tfc = comp_box.text_frame
    tfc.word_wrap = True

    pc_h = tfc.paragraphs[0]
    pc_h.text = "Why Traditional Pre-Migration Validation Workflows Break Down:"
    pc_h.font.size = Pt(14)
    pc_h.font.bold = True
    pc_h.font.color.rgb = NAVY
    pc_h.space_after = Pt(6)

    points = [
        "Manual Review & Spreadsheets: Error-prone, humanly impossible to scale to 400k+ records, and lacks reproducible audit trails.",
        "Ad-Hoc SQL Scripts: Rigid, tightly coupled to IT staff, creates lengthy iterative bottlenecks between functional and technical teams.",
        "Lack of Traceability: When errors occur during bulk inserts, pinpointing exact row, column, invalid value, and violated rule is difficult.",
        "Exclusion of Business Users: Non-technical domain experts (underwriters, claims officers) cannot participate directly in rule definition."
    ]
    for pt in points:
        p = tfc.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = SLATE
        p.space_after = Pt(4)

    # -------------------------------------------------------------------------
    # SLIDE 3: The Accura Proposed Solution
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "The DataGuard AI Framework: Hybrid AI + Deterministic Validation", "Core Methodology")

    pillars = [
        ("1. Natural Language Interpretation", "GPT-4o converts business specifications in plain language into structured, schema-constrained JSON rules with zero code requirement.", PURPLE),
        ("2. Coherence Verification", "Two-step verification engine checks schema validity, type consistency, and column existence before any rule is stored in the catalog.", BLUE),
        ("3. Deterministic Validation Engine", "Executes strict row-by-row rule evaluations over migration datasets, capturing every structural inconsistency with 100% precision.", EMERALD),
        ("4. Role-Based Traceability", "Decouples Administrator and Client lanes. Generates multi-sheet Excel audit reports linking violated rules to row/column coordinates.", DARK_BLUE)
    ]

    for i, (title, desc, col) in enumerate(pillars):
        x = Inches(0.8 + (i % 2) * 5.95)
        y = Inches(1.7 + (i // 2) * 2.65)
        add_card(s3, x, y, Inches(5.75), Inches(2.45))
        
        # Color bar
        cbar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.3), y + Inches(0.3), Inches(0.1), Inches(1.85))
        cbar.fill.solid()
        cbar.fill.fore_color.rgb = col
        cbar.line.fill.background()

        tb = s3.shapes.add_textbox(x + Inches(0.6), y + Inches(0.3), Inches(4.9), Inches(1.85))
        tf = tb.text_frame
        tf.word_wrap = True

        ptit = tf.paragraphs[0]
        ptit.text = title
        ptit.font.size = Pt(14)
        ptit.font.bold = True
        ptit.font.color.rgb = NAVY
        ptit.space_after = Pt(8)

        pdesc = tf.add_paragraph()
        pdesc.text = desc
        pdesc.font.size = Pt(11)
        pdesc.font.color.rgb = SLATE
        pdesc.space_after = Pt(6)

    # -------------------------------------------------------------------------
    # SLIDE 4: Layered System Architecture
    # -------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Multi-Layered Architecture & Implementation Tech Stack", "System Design")

    layers = [
        ("Presentation Layer", "Responsive Web UI", [
            "Single Page Application matching Figures 6-14 in paper",
            "Role Switcher: Admin, Technical QA, Client User",
            "Real-time validation progress & Chart.js benchmark graphs",
            "Tech: Vanilla JS, Tailwind CSS CDN, FontAwesome, Chart.js"
        ], DARK_BLUE),
        ("Application Layer", "FastAPI Core Services", [
            "RESTful API endpoints for templates, rules, and uploads",
            "Role-Based Access Control (RBAC) with JWT security",
            "Pydantic v2 schemas for strong type safety and validation",
            "Tech: FastAPI 0.128, Python 3.13, PyJWT, Pydantic"
        ], BLUE),
        ("AI / NLP Layer", "GPT-4o Rule Synthesizer", [
            "Contextual prompt engineering with template headers",
            "Temperature = 0.2, Max tokens = 800 (per Section III-B)",
            "Automated schema coherence validator + single retry loop",
            "Intelligent offline domain synthesizer fallback"
        ], PURPLE),
        ("Data & Storage Layer", "Relational Persistence & Excel", [
            "Normalized 12-table relational database schema (SQLAlchemy)",
            "SQLite portability (default) / SQL Server enterprise ready",
            "openpyxl engine for styled multi-sheet Excel audit reports",
            "Tech: SQLAlchemy ORM, openpyxl, pandas"
        ], EMERALD)
    ]

    for i, (title, sub, bullets, col) in enumerate(layers):
        x = Inches(0.8 + i * 2.95)
        add_card(s4, x, Inches(1.7), Inches(2.8), Inches(5.1))
        
        # Header banner inside card
        hb = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.7), Inches(2.8), Inches(0.8))
        hb.fill.solid()
        hb.fill.fore_color.rgb = col
        hb.line.fill.background()

        htbox = s4.shapes.add_textbox(x + Inches(0.15), Inches(1.75), Inches(2.5), Inches(0.7))
        htf = htbox.text_frame
        hp1 = htf.paragraphs[0]
        hp1.text = title
        hp1.font.size = Pt(12)
        hp1.font.bold = True
        hp1.font.color.rgb = WHITE
        hp2 = htf.add_paragraph()
        hp2.text = sub
        hp2.font.size = Pt(9)
        hp2.font.color.rgb = RGBColor(226, 232, 240)

        # Bullet list
        bb = s4.shapes.add_textbox(x + Inches(0.15), Inches(2.6), Inches(2.5), Inches(4.0))
        btf = bb.text_frame
        btf.word_wrap = True
        for b_idx, b in enumerate(bullets):
            p = btf.paragraphs[0] if b_idx == 0 else btf.add_paragraph()
            p.text = "• " + b
            p.font.size = Pt(10)
            p.font.color.rgb = SLATE
            p.space_after = Pt(8)

    # -------------------------------------------------------------------------
    # SLIDE 5: Method 1 - GPT-4o Rule Generation
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Method 1: Natural-Language Rule Synthesis via GPT-4o", "Development Methods (AI Engine)")

    # Left: Explanation & Parameters
    add_card(s5, Inches(0.8), Inches(1.7), Inches(5.75), Inches(5.1))
    tb_l = s5.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.35), Inches(4.7))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Prompt Engineering & Model Configuration"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    items_l = [
        "Model Selection: OpenAI GPT-4o (gpt-4o) accessed via OpenAI Python SDK.",
        "Hyperparameters: Temperature = 0.2 (low randomness for deterministic output), Max tokens = 800.",
        "Contextual Prompt Assembly: Each prompt embeds the target column name, list of available template headers, supported rule categories, and insurance sector business context.",
        "Guided Instruction Pattern (Paper Section III-B):",
        "  'Validate that the field [Field name] is of type [Data type] and satisfies [Condition]; otherwise display: [Error message]. Valid example: [Val]. Invalid example: [Inval].'",
        "Free-Form Natural Language: If unguided, GPT-4o infers constraints using template headers and insurance domain heuristics."
    ]
    for it in items_l:
        p = tf_l.add_paragraph()
        p.text = it
        p.font.size = Pt(10)
        p.font.color.rgb = SLATE
        p.space_after = Pt(4)

    # Right: JSON Rule Structure
    add_card(s5, Inches(6.75), Inches(1.7), Inches(5.75), Inches(5.1))
    tb_r = s5.shapes.add_textbox(Inches(6.95), Inches(1.9), Inches(5.35), Inches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "Standardized Output JSON Structure (Section III-C)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    sample_json = (
        "{\n"
        '  "Rule name": "Policy Premium Range",\n'
        '  "Data type": "Number",\n'
        '  "Required field": true,\n'
        '  "Header": ["Prima_Total"],\n'
        '  "Header rule": ["Prima_Total"],\n'
        '  "Error message": "Total premium must be between 1 and 1,000,000.",\n'
        '  "Description": "Validates policy gross premium bounds.",\n'
        '  "Example": {\n'
        '    "Valid example": 1500.50,\n'
        '    "Invalid example": -50.00\n'
        '  },\n'
        '  "Rule": {\n'
        '    "Minimum value": 1.00,\n'
        '    "Maximum value": 1000000.00,\n'
        '    "Number of decimals": 2\n'
        '  }\n'
        "}"
    )
    p_code = tf_r.add_paragraph()
    p_code.text = sample_json
    p_code.font.name = "Consolas"
    p_code.font.size = Pt(9.5)
    p_code.font.color.rgb = RGBColor(16, 185, 129)

    # -------------------------------------------------------------------------
    # SLIDE 6: Method 2 - Coherence Verification & Retry
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Method 2: Coherence Verification & Self-Correction Retry Loop", "Development Methods (Quality Gate)")

    steps = [
        ("Step 1: Structural JSON Validation", "Checks if the LLM output is valid, parseable JSON and conforms to required top-level keys ('Rule name', 'Data type', 'Header', 'Rule')."),
        ("Step 2: Supported Data Type Verification", "Verifies that the generated 'Data type' matches one of the 9 officially supported DataGuard AI validation types."),
        ("Step 3: Column Header Compatibility Check", "Validates that all column names in 'Header' and 'Header rule' actually exist in the current migration template. Rejects phantom columns."),
        ("Step 4: Parameter Completeness Check", "Ensures type-specific parameter blocks are populated (e.g. 'List' contains values array, 'Number' has min/max, 'Dependency' has conditions)."),
        ("Step 5: Automatic Single Retry Loop", "If any check fails, DataGuard AI prompts GPT-4o with the specific error context for an immediate self-correction. If attempt 2 fails, the rule is discarded.")
    ]

    for i, (title, desc) in enumerate(steps):
        y = Inches(1.7 + i * 1.0)
        add_card(s6, Inches(0.8), y, Inches(11.7), Inches(0.85))
        
        # Step Number badge
        nb = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), y + Inches(0.18), Inches(1.5), Inches(0.48))
        nb.fill.solid()
        nb.fill.fore_color.rgb = BLUE
        nb.line.fill.background()
        ntf = nb.text_frame
        np = ntf.paragraphs[0]
        np.text = f"GATE {i+1}"
        np.font.size = Pt(11)
        np.font.bold = True
        np.font.color.rgb = WHITE
        np.alignment = PP_ALIGN.CENTER

        tb = s6.shapes.add_textbox(Inches(2.7), y + Inches(0.12), Inches(9.6), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        ptit = tf.paragraphs[0]
        ptit.text = title
        ptit.font.size = Pt(12)
        ptit.font.bold = True
        ptit.font.color.rgb = NAVY

        pdesc = tf.add_paragraph()
        pdesc.text = desc
        pdesc.font.size = Pt(10)
        pdesc.font.color.rgb = SLATE

    # -------------------------------------------------------------------------
    # SLIDE 7: Method 3 - The 9 Validation Rule Categories
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Method 3: Deterministic Rule Evaluator (9 Categories)", "Development Methods (Validation Engine)")

    rule_types = [
        ("1. Text", "Alphanumeric length constraints.", "Minimum length, Maximum length"),
        ("2. Number", "Numeric bounds & decimal places.", "Minimum value, Maximum value, Decimals"),
        ("3. Document", "Identity document length (DNI/RUC).", "Min/Max length (e.g. 8 for DNI, 11 for RUC)"),
        ("4. List", "Fixed set of allowable categories.", "List: ['EMITIDA', 'VIGENTE', 'ANULADA']"),
        ("5. Complex List", "Multi-column valid combinations.", "Complex list: [{Dept: Lima, Prov: Lima}]"),
        ("6. Phone", "Phone format and country codes.", "Minimum length: 9, Country code: '+51'"),
        ("7. Email", "RFC syntax and character limits.", "Format: 'email', Maximum length: 100"),
        ("8. Date", "Date formats and inception boundaries.", "Format: 'yyyy-MM-dd', Min & Max dates"),
        ("9. Dependency", "Conditional cross-column rules.", "Specific rules: If PJ -> RUC; If PN -> DNI")
    ]

    for i, (name, purpose, params) in enumerate(rule_types):
        col_idx = i % 3
        row_idx = i // 3
        x = Inches(0.8 + col_idx * 3.95)
        y = Inches(1.7 + row_idx * 1.75)
        add_card(s7, x, y, Inches(3.8), Inches(1.6))

        tb = s7.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(3.4), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = name
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = DARK_BLUE
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = purpose
        p2.font.size = Pt(10)
        p2.font.color.rgb = NAVY
        p2.space_after = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = "Params: " + params
        p3.font.size = Pt(9)
        p3.font.color.rgb = SLATE

    # -------------------------------------------------------------------------
    # SLIDE 8: Method 4 - Database Architecture
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Method 4: Normalized Relational Database Design", "Development Methods (Data Layer)")

    entities = [
        ("Role & User", "Identity & Access", "role (id, name, status)\nuser (id, role_id, email, password, department, is_active)\ntemplate_user_access (template_id, user_id, start_date)"),
        ("Template & Columns", "Target Schema Definition", "template (id, name, table_name, description, status)\ntemplate_column (id, template_id, name, data_type, is_required)"),
        ("Rule & Assignments", "Validation Logic", "rule (id, name, data_type, json_rule, effectiveness)\ntemplate_column_rule (template_column_id, rule_id)"),
        ("Load & Inconsistencies", "Audit & Reporting", "load (id, template_id, status, total_rows, valid_rows, error_rows)\nloaded_file (load_id, name, path, size)\nvalidation_error (load_id, row, col, rule, value, severity, msg)\nnotification & audit_log")
    ]

    for i, (name, subtitle, tables) in enumerate(entities):
        col_idx = i % 2
        row_idx = i // 2
        x = Inches(0.8 + col_idx * 5.95)
        y = Inches(1.7 + row_idx * 2.65)
        add_card(s8, x, y, Inches(5.75), Inches(2.45))

        tb = s8.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), Inches(5.15), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = name + f" — {subtitle}"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = BLUE
        p1.space_after = Pt(6)

        p2 = tf.add_paragraph()
        p2.text = tables
        p2.font.name = "Consolas"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = SLATE

    # -------------------------------------------------------------------------
    # SLIDE 9: Method 5 - Validation Pipeline & Reports
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Method 5: Dataset Ingestion & Styled Excel Reporting", "Development Methods (Execution Engine)")

    add_card(s9, Inches(0.8), Inches(1.7), Inches(5.75), Inches(5.1))
    tb_p = s9.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.35), Inches(4.7))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True

    p = tf_p.paragraphs[0]
    p.text = "Deterministic Execution Pipeline"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    pipe_steps = [
        "1. File Parsing: Ingests .xlsx, .xls, or .csv using openpyxl & pandas into in-memory tabular records.",
        "2. Structural Header Gate: Compares uploaded file headers against expected template columns. Rejects immediately if required columns are missing.",
        "3. In-Memory Rule Indexing: Pre-loads rules mapped to columns into hash tables for sub-second execution.",
        "4. Row-by-Row Evaluation: Iterates every row, evaluating active column rules, recording row index (matching Excel numbers).",
        "5. Inconsistency Categorization: Logs violated rule ID, violated rule name, invalid value, severity (Error/Warning), and error message.",
        "6. Status Determination: 'Completed' if 0 errors; 'Rejected' if >= 1 errors."
    ]
    for ps in pipe_steps:
        p = tf_p.add_paragraph()
        p.text = ps
        p.font.size = Pt(10)
        p.font.color.rgb = SLATE
        p.space_after = Pt(4)

    add_card(s9, Inches(6.75), Inches(1.7), Inches(5.75), Inches(5.1))
    tb_rep = s9.shapes.add_textbox(Inches(6.95), Inches(1.9), Inches(5.35), Inches(4.7))
    tf_rep = tb_rep.text_frame
    tf_rep.word_wrap = True

    p = tf_rep.paragraphs[0]
    p.text = "Traceable Multi-Sheet Excel Reports (.xlsx)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    rep_features = [
        "Sheet 1 — Validation Summary:",
        "  • Executive KPI table: Template Name, Source File, Execution Status, Total Evaluated Records, Valid Rows, Error Rows.",
        "  • Accuracy Rate (%) & Validation Duration in seconds.",
        "  • Rule Breakdown Table: Aggregated violation count per rule.",
        "Sheet 2 — Structural Inconsistencies:",
        "  • Granular Table: #, Row Number, Column Header, Violated Rule Name, Invalid Value, Severity, Observation.",
        "  • Conditional Formatting: Red highlight (#FEE2E2) on erroneous values for rapid correction.",
        "Audit Compliance: Every report is timestamped, saved to disk, and linked to Load ID for historical traceability."
    ]
    for rf in rep_features:
        p = tf_rep.add_paragraph()
        p.text = rf
        p.font.size = Pt(10)
        p.font.color.rgb = SLATE
        p.space_after = Pt(3)

    # -------------------------------------------------------------------------
    # SLIDE 10: How to Use DataGuard AI - Administrator Lane
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "How to Use DataGuard AI: Administrator & Technical QA Lane", "User Guide (Configuration)")

    admin_steps = [
        ("Step 1: User & Role Administration", "Manage user accounts, assign roles (Administrator, Technical user, Client user), and control department access in the Users module (Figure 6)."),
        ("Step 2: Define Migration Templates", "Create a new template with template name, description, and target database table (e.g. Plantilla_polizas) in Templates module (Figure 9)."),
        ("Step 3: Configure Expected Columns", "Register expected column headers, data types (Text, Number, Date, Document), and mandatory status flags (Figure 10)."),
        ("Step 4: AI-Assisted Rule Generation", "Click 'AI Rule Generator (GPT-4o)', type natural language requirements or pick a quick pattern, verify JSON schema, and save to catalog (Figure 8)."),
        ("Step 5: Publish & Assign Client Permissions", "Review template configuration, toggle status from 'Draft' to 'Published', and grant authorized access to client accounts (Figure 11).")
    ]

    for i, (stitle, sdesc) in enumerate(admin_steps):
        y = Inches(1.7 + i * 1.0)
        add_card(s10, Inches(0.8), y, Inches(11.7), Inches(0.85))

        nb = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), y + Inches(0.18), Inches(1.4), Inches(0.48))
        nb.fill.solid()
        nb.fill.fore_color.rgb = DARK_BLUE
        nb.line.fill.background()
        ntf = nb.text_frame
        np = ntf.paragraphs[0]
        np.text = f"STEP {i+1}"
        np.font.size = Pt(11)
        np.font.bold = True
        np.font.color.rgb = WHITE
        np.alignment = PP_ALIGN.CENTER

        tb = s10.shapes.add_textbox(Inches(2.6), y + Inches(0.12), Inches(9.7), Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True
        ptit = tf.paragraphs[0]
        ptit.text = stitle
        ptit.font.size = Pt(12)
        ptit.font.bold = True
        ptit.font.color.rgb = NAVY

        pdesc = tf.add_paragraph()
        pdesc.text = sdesc
        pdesc.font.size = Pt(10)
        pdesc.font.color.rgb = SLATE

    # -------------------------------------------------------------------------
    # SLIDE 11: How to Use DataGuard AI - Client Reviewer Lane
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "How to Use DataGuard AI: Client & Reviewer Validation Lane", "User Guide (Execution)")

    client_steps = [
        ("Step 1: Select Authorized Template", "Client user views assigned published templates (e.g. Policies, Customers) and selects target dataset structure (Figure 12)."),
        ("Step 2: Download Empty Template (.xlsx)", "Click 'Download Empty Template' to get a blank Excel spreadsheet with the exact expected headers and column widths."),
        ("Step 3: Drag & Drop Migration Dataset", "Upload the populated dataset (.xlsx, .xls, or .csv) or use the pre-configured One-Click Test buttons."),
        ("Step 4: Automated Validation Execution", "Click 'Execute Structural Validation'. DataGuard AI runs real-time progress scanning across all rows and assigned rules (Figure 13)."),
        ("Step 5: Inspect Inconsistencies & Traceability", "Review the Compliance Rate %, total valid rows, and granular table listing each violated rule with invalid value and row number."),
        ("Step 6: Download Excel Audit Report", "Click 'Download Excel Report (.xlsx)' to obtain the multi-sheet report, correct errors in the file, and re-upload until 100% compliant.")
    ]

    for i, (stitle, sdesc) in enumerate(client_steps):
        col_idx = i % 2
        row_idx = i // 2
        x = Inches(0.8 + col_idx * 5.95)
        y = Inches(1.7 + row_idx * 1.75)
        add_card(s11, x, y, Inches(5.75), Inches(1.6))

        nb = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), y + Inches(0.2), Inches(1.2), Inches(0.35))
        nb.fill.solid()
        nb.fill.fore_color.rgb = BLUE
        nb.line.fill.background()
        ntf = nb.text_frame
        np = ntf.paragraphs[0]
        np.text = f"ACTION {i+1}"
        np.font.size = Pt(9.5)
        np.font.bold = True
        np.font.color.rgb = WHITE
        np.alignment = PP_ALIGN.CENTER

        tb = s11.shapes.add_textbox(x + Inches(1.55), y + Inches(0.12), Inches(4.0), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True
        ptit = tf.paragraphs[0]
        ptit.text = stitle
        ptit.font.size = Pt(12)
        ptit.font.bold = True
        ptit.font.color.rgb = NAVY

        pdesc = tf.add_paragraph()
        pdesc.text = sdesc
        pdesc.font.size = Pt(9.5)
        pdesc.font.color.rgb = SLATE

    # -------------------------------------------------------------------------
    # SLIDE 12: Empirical Results & IEEE Access Benchmark
    # -------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Empirical Findings: Scenario 1 (Manual) vs Scenario 2 (DataGuard AI)", "Case Study Results (Section VI)")

    # 3 Summary Cards
    cards = [
        ("Rule Definition Accuracy", "82.86% -> 97.14%", "+14.28 percentage point improvement. Manual adjustment rate (ADR) dropped from 17.14% down to only 2.86% (34 of 35 rules correct on first try).", BLUE),
        ("Validation Time per Template", "183.75 min -> 28.00 min", "84.76% overall time reduction (TRV). Rule creation plummeted from 77.5 to 14.25 min (81.61% TRC) and rule verification from 46.25 to 5.75 min.", EMERALD),
        ("Error Detection Performance", "F1-Score: 94.32% -> 99.92%", "Precision: 100.00% (zero false positives!). Recall: 99.83% (only 121 false negatives across 200 pooled participant executions totaling 71,909 errors).", PURPLE)
    ]

    for i, (title, highlight, text, col) in enumerate(cards):
        x = Inches(0.8 + i * 3.95)
        add_card(s12, x, Inches(1.7), Inches(3.8), Inches(2.6))

        tb = s12.shapes.add_textbox(x + Inches(0.2), Inches(1.85), Inches(3.4), Inches(2.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.text = highlight
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = col
        p2.space_before = Pt(4)
        p2.space_after = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = text
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = SLATE

    # Datasets Summary Table at Bottom
    add_card(s12, Inches(0.8), Inches(4.5), Inches(11.7), Inches(2.3))
    dtb = s12.shapes.add_textbox(Inches(1.0), Inches(4.65), Inches(11.3), Inches(2.0))
    dtf = dtb.text_frame
    dtf.word_wrap = True

    dp1 = dtf.paragraphs[0]
    dp1.text = "InsurTech Dataset Case Study Evaluation (Inventiva Insurtech Solutions S.A.C.):"
    dp1.font.size = Pt(12)
    dp1.font.bold = True
    dp1.font.color.rgb = NAVY
    dp1.space_after = Pt(4)

    ds_lines = [
        "• Plantilla_ordenes (Issue Orders): 138,725 records | 23 columns | 14 validation rules (Largest volume)",
        "• Plantilla_polizas (Master Policies): 126,403 records | 19 columns | 5 validation rules",
        "• Plantilla_clientes (Customers): 23,914 records | 34 columns | 18 validation rules (Most complex: dependencies & complex lists)",
        "• Plantilla_facturas (Invoices): 111,737 records | 19 columns | 12 validation rules",
        "TOTAL: 400,779 records evaluated across 95 columns and 49 validation rules with 50 industry participants."
    ]
    for dl in ds_lines:
        p = dtf.add_paragraph()
        p.text = dl
        p.font.size = Pt(10)
        p.font.color.rgb = SLATE
        p.space_after = Pt(2)

    # -------------------------------------------------------------------------
    # SLIDE 13: Live Viva / Demo Walkthrough Script
    # -------------------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Step-by-Step Viva & Project Demonstration Script", "Viva & Presentation Walkthrough")

    demo_steps = [
        ("1. Introduction (1 min)", "Introduce DataGuard AI, cite IEEE Access 2026 base paper, explain InsurTech migration failure stats ($600B loss) and the need for pre-migration structural validation."),
        ("2. Dashboard Overview (30 sec)", "Open http://localhost:8000. Show KPI cards (4 templates, 49 rules, 97.14% ACC, 84.76% TRV), role switcher, and active migration datasets."),
        ("3. Client Dataset Ingestion (1 min)", "Switch to 'Client' role. Select Plantilla_polizas, click 'Policies with Inconsistencies' button, run validation, show progress bar and rejected status."),
        ("4. Error Inspection & Excel Report (1 min)", "Show the granular error table (negative premium, invalid DNI length, bad status). Click 'Download Excel Report (.xlsx)' and show the two formatted sheets."),
        ("5. Dependency Rule Demonstration (30 sec)", "Select Plantilla_clientes, run validation with customer inconsistencies, show how DataGuard AI detects Person Type PJ with personal DNI instead of corporate RUC."),
        ("6. AI Rule Generator in Real Time (1 min)", "Switch to 'Admin' role, open AI Rule Generator, select a column, click a quick prompt, click 'Generate & Verify Schema', and show GPT-4o output passing coherence."),
        ("7. Case Study Benchmark & Q&A", "Navigate to 'Case Study & Benchmark' tab. Walk through the interactive Chart.js graphs proving the 14.28% ACC gain and 84.76% time savings.")
    ]

    for i, (title, script) in enumerate(demo_steps):
        y = Inches(1.7 + i * 0.75)
        add_card(s13, Inches(0.8), y, Inches(11.7), Inches(0.68))

        tb = s13.shapes.add_textbox(Inches(1.0), y + Inches(0.08), Inches(11.3), Inches(0.55))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title + " — " + script
        p.font.size = Pt(10.5)
        p.font.color.rgb = NAVY

    # -------------------------------------------------------------------------
    # SLIDE 14: Conclusion & Future Scope (Dark Theme)
    # -------------------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    bg14 = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg14.fill.solid()
    bg14.fill.fore_color.rgb = NAVY
    bg14.line.fill.background()

    tb14 = s14.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(6.0))
    tf14 = tb14.text_frame
    tf14.word_wrap = True

    p = tf14.paragraphs[0]
    p.text = "CONCLUSION & FUTURE HORIZONS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(96, 165, 250)
    p.space_after = Pt(8)

    p_c1 = tf14.add_paragraph()
    p_c1.text = "Summary of Contributions:"
    p_c1.font.size = Pt(20)
    p_c1.font.bold = True
    p_c1.font.color.rgb = WHITE
    p_c1.space_after = Pt(12)

    bullets_c = [
        "Bridged Business & Technical Teams: Enabled non-technical InsurTech stakeholders to specify structural validation criteria in plain natural language without writing SQL or code.",
        "Deterministic Accuracy with Generative Flexibility: Safely leveraged GPT-4o for rule drafting while maintaining 100% deterministic, verifiable execution over migration datasets.",
        "Traceability & Governance: Solved migration opacity by linking every inconsistent row to its exact column, invalid value, and violated business rule in multi-sheet Excel reports.",
        "Proven Empirical Superiority: Slashed validation time from 183.75 to 28 minutes per template (84.76% faster) while achieving a near-flawless 99.92% F1-score."
    ]
    for b in bullets_c:
        p = tf14.add_paragraph()
        p.text = "✔ " + b
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_after = Pt(8)

    p_f = tf14.add_paragraph()
    p_f.text = "\nFuture Directions (Paper Section VIII):"
    p_f.font.size = Pt(15)
    p_f.font.bold = True
    p_f.font.color.rgb = RGBColor(147, 197, 253)
    p_f.space_after = Pt(6)

    future_pts = [
        "1. Semantic Validation: Incorporating cross-system entity reconciliation and anomaly detection beyond structural types.",
        "2. Direct Pipeline Connectors: Connecting DataGuard AI directly to Kafka streams, cloud data lakes, and enterprise ERP staging tables.",
        "3. Multi-LLM Benchmarking: Evaluating Gemini 1.5/2.0, Claude 3.5, and Llama 3 for rule accuracy, speed, and cost efficiency."
    ]
    for fp in future_pts:
        p = tf14.add_paragraph()
        p.text = "• " + fp
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(203, 213, 225)
        p.space_after = Pt(4)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    prs.save(output_path)
    print(f"[+] Presentation saved successfully to: {output_path}")

    # Also save with base paper name for complete reference
    alt_path = "Accura_Project_Presentation.pptx"
    prs.save(alt_path)
    print(f"[+] Presentation copy also saved to: {alt_path}")

if __name__ == "__main__":
    create_accura_presentation("DataGuard_AI_Project_Presentation.pptx")

