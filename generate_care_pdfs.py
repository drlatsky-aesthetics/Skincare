"""
Generate pre & post care PDFs for NouvaDerm and PlaDuo Pro.
Run: python3 generate_care_pdfs.py
Outputs two PDFs in the current directory.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas


# ── Brand colours ──────────────────────────────────────────────────
CHARCOAL   = colors.HexColor("#0C0C0C")
CHARCOAL2  = colors.HexColor("#1A1A1A")
CHARCOAL3  = colors.HexColor("#222222")
GOLD       = colors.HexColor("#C4954A")
GOLD_LIGHT = colors.HexColor("#D4AF37")
TEXT       = colors.HexColor("#E8E2D9")
TEXT_MUTED = colors.HexColor("#7A7060")
TEXT_DIM   = colors.HexColor("#4A4540")
BORDER     = colors.HexColor("#2A2520")
WHITE      = colors.white
OFF_WHITE  = colors.HexColor("#F5F0EB")


# ── Styles ─────────────────────────────────────────────────────────
def make_styles():
    return {
        "clinic": ParagraphStyle(
            "clinic", fontName="Helvetica", fontSize=7.5,
            textColor=GOLD, letterSpacing=2, spaceAfter=2, alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=7,
            textColor=TEXT_MUTED, letterSpacing=1, alignment=TA_CENTER, spaceAfter=0,
        ),
        "device_title": ParagraphStyle(
            "device_title", fontName="Helvetica-Bold", fontSize=18,
            textColor=CHARCOAL, spaceAfter=2, leading=22,
        ),
        "device_sub": ParagraphStyle(
            "device_sub", fontName="Helvetica", fontSize=9,
            textColor=TEXT_MUTED, spaceAfter=14, letterSpacing=0.5,
        ),
        "section_label": ParagraphStyle(
            "section_label", fontName="Helvetica-Bold", fontSize=7,
            textColor=GOLD, letterSpacing=2, spaceBefore=18, spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9,
            textColor=CHARCOAL, leading=15, spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=9,
            textColor=CHARCOAL, leading=15, spaceAfter=4,
            leftIndent=12, firstLineIndent=-12,
        ),
        "day_label": ParagraphStyle(
            "day_label", fontName="Helvetica-Bold", fontSize=9,
            textColor=CHARCOAL, leading=14, spaceAfter=3,
        ),
        "note": ParagraphStyle(
            "note", fontName="Helvetica-Oblique", fontSize=8,
            textColor=TEXT_MUTED, leading=13, spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica", fontSize=7,
            textColor=TEXT_MUTED, alignment=TA_CENTER, letterSpacing=0.5,
        ),
    }


class GoldBar(Flowable):
    """Thin gold rule the full column width."""
    def __init__(self, width, thickness=1.5):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness

    def draw(self):
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, 0, self.width, self.thickness, fill=1, stroke=0)

    def wrap(self, *args):
        return self.width, self.thickness + 2


def section_block(title, items, styles, col_width, day_groups=None):
    """
    Build a visually boxed section.
    items = list of strings (bullet points)
    day_groups = list of (day_label, [bullet strings]) for day-by-day layout
    """
    story = []
    story.append(Paragraph(title.upper(), styles["section_label"]))

    if day_groups:
        for day, bullets in day_groups:
            story.append(Paragraph(day, styles["day_label"]))
            for b in bullets:
                story.append(Paragraph("•  " + b, styles["bullet"]))
            story.append(Spacer(1, 4))
    else:
        for item in items:
            story.append(Paragraph("•  " + item, styles["bullet"]))

    return story


def draw_header(canvas_obj, doc, device_name, device_sub, doc_type):
    """Draw the dark branded header on each page."""
    w, h = letter
    margin = 0.65 * inch
    header_h = 1.5 * inch

    # Dark background
    canvas_obj.setFillColor(CHARCOAL2)
    canvas_obj.rect(0, h - header_h, w, header_h, fill=1, stroke=0)

    # Gold bar at very top
    canvas_obj.setFillColor(GOLD)
    canvas_obj.rect(0, h - 3, w, 3, fill=1, stroke=0)

    # Clinic name
    canvas_obj.setFillColor(GOLD)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawCentredString(w / 2, h - 0.38 * inch, "TREASURY AESTHETICS  ·  TORONTO, ONTARIO")

    # Device name
    canvas_obj.setFillColor(WHITE)
    canvas_obj.setFont("Helvetica-Bold", 20)
    canvas_obj.drawString(margin, h - 0.82 * inch, device_name)

    # Sub-label
    canvas_obj.setFillColor(TEXT_MUTED)
    canvas_obj.setFont("Helvetica", 8.5)
    canvas_obj.drawString(margin, h - 1.02 * inch, device_sub)

    # Doc type badge
    badge_text = doc_type.upper()
    badge_w = canvas_obj.stringWidth(badge_text, "Helvetica-Bold", 7) + 16
    bx = w - margin - badge_w
    by = h - 1.08 * inch
    canvas_obj.setFillColor(GOLD)
    canvas_obj.roundRect(bx, by, badge_w, 18, 3, fill=1, stroke=0)
    canvas_obj.setFillColor(CHARCOAL)
    canvas_obj.setFont("Helvetica-Bold", 7)
    canvas_obj.drawCentredString(bx + badge_w / 2, by + 5.5, badge_text)

    # Gold divider line at bottom of header
    canvas_obj.setFillColor(GOLD)
    canvas_obj.rect(0, h - header_h, w, 1.5, fill=1, stroke=0)


def draw_footer(canvas_obj, doc, page_num):
    w, h = letter
    margin = 0.65 * inch
    canvas_obj.setFillColor(CHARCOAL3)
    canvas_obj.rect(0, 0, w, 0.45 * inch, fill=1, stroke=0)
    canvas_obj.setFillColor(TEXT_MUTED)
    canvas_obj.setFont("Helvetica", 6.5)
    canvas_obj.drawString(margin, 0.16 * inch,
        "Treasury Aesthetics  ·  aesthetics@treasuryhealth.ca  ·  treasuryhealth.ca")
    canvas_obj.drawRightString(w - margin, 0.16 * inch, f"Page {page_num}")


def build_pdf(filename, device_name, device_sub, doc_type, content_fn):
    """Build one PDF file."""
    styles = make_styles()
    margin = 0.65 * inch
    top_margin = 1.65 * inch  # below dark header
    bot_margin = 0.6 * inch

    page_num_holder = [1]

    def on_page(canvas_obj, doc):
        canvas_obj.saveState()
        draw_header(canvas_obj, doc, device_name, device_sub, doc_type)
        draw_footer(canvas_obj, doc, page_num_holder[0])
        page_num_holder[0] += 1
        canvas_obj.restoreState()

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=margin, rightMargin=margin,
        topMargin=top_margin, bottomMargin=bot_margin,
    )

    col_width = letter[0] - 2 * margin
    story = content_fn(styles, col_width)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"  Created: {filename}")


# ══════════════════════════════════════════════════════════════════════
# NOUVADERM — Pre-Treatment
# ══════════════════════════════════════════════════════════════════════

def nouvaderm_pre(styles, col_width):
    s = []

    s.append(Paragraph(
        "Please follow these instructions carefully before your NouvaDerm treatment to ensure "
        "the best possible results and minimise any risk of adverse reactions.",
        styles["body"]
    ))
    s.append(Spacer(1, 6))

    # Skincare prep
    s += section_block("Skincare Preparation", [
        "Begin the <b>Noon Pre-Procedure Program</b> 10–14 days prior to your appointment.",
        "Discontinue <b>retinoids</b> (tretinoin, retinol) and <b>AHA/BHA exfoliants</b> 7 days before treatment.",
        "Discontinue <b>vitamin C serums</b> 3–5 days before treatment.",
        "Do not use any <b>self-tanner</b> or sunless bronzer for 2 weeks prior.",
        "Arrive with <b>clean, makeup-free skin</b> — no creams, serums, or SPF.",
    ], styles, col_width)

    # Sun & lifestyle
    s += section_block("Sun & Lifestyle", [
        "Avoid direct <b>sun exposure and tanning beds</b> for 2–4 weeks prior "
        "(strict for Ablative mode; 2 weeks minimum for NOUVAGlo).",
        "If you have a history of <b>cold sores (HSV)</b>, antiviral medication will be prescribed — "
        "begin as directed by your physician.",
        "Avoid <b>Accutane (isotretinoin)</b> within 6 months of treatment (12 months for Ablative mode).",
        "Discontinue <b>blood thinners and supplements</b> (fish oil, vitamin E, aspirin unless prescribed) "
        "7 days prior to minimise bruising risk.",
    ], styles, col_width)

    # Day of
    s += section_block("Day of Treatment", [
        "Arrive 30–45 minutes early — topical anaesthetic cream is applied in-clinic and requires time to take effect.",
        "Avoid caffeine on the day of treatment if you are sensitive.",
        "Do not drive yourself home following Ablative mode — arrange transport in advance.",
        "Wear comfortable, loose clothing. Avoid tight collars if treating the neck.",
    ], styles, col_width)

    # Medical history note
    s += section_block("Medical History — Please Inform Us If You Have:", [
        "Active skin infection, open sores, or rash in the treatment area.",
        "History of keloid or hypertrophic scarring.",
        "Autoimmune conditions or immunosuppressive medications.",
        "Pregnancy or breastfeeding.",
        "Pacemaker or implanted electronic devices.",
    ], styles, col_width)

    s.append(Spacer(1, 12))
    s.append(GoldBar(col_width))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Questions before your appointment? Contact us at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))

    return s


# ══════════════════════════════════════════════════════════════════════
# NOUVADERM — Post-Treatment
# ══════════════════════════════════════════════════════════════════════

def nouvaderm_post(styles, col_width):
    s = []

    s.append(Paragraph(
        "Your skin is in an active healing phase. Following these instructions precisely protects "
        "your investment and significantly improves your final result.",
        styles["body"]
    ))
    s.append(Spacer(1, 6))

    # NOUVAGlo (non-ablative)
    s.append(Paragraph("NOUVAGlo (Non-Ablative Mode)", styles["section_label"]))

    s += section_block("", [], styles, col_width, day_groups=[
        ("Days 1–3", [
            "Apply <b>Epicutis Lipid Recovery Mask</b> as directed — use in-clinic application as your baseline.",
            "Apply <b>Epicutis Lipid Serum + HYVIA Crème</b> 2–4× daily.",
            "Cleanse gently with <b>Epicutis Oil Cleanser</b> or <b>Noon MicroSoft Cleanser</b> only.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — reapply every 2 hours if outdoors. Non-negotiable.",
            "Mild redness, warmth, and bronzing are expected and normal during this period.",
            "No exfoliants, retinoids, AHAs, BHAs, or vitamin C.",
        ]),
        ("Days 3–5", [
            "Continue Epicutis Lipid Serum + HYVIA Crème; pinpoint micro-crusting is normal — do not pick.",
            "Continue gentle cleansing; continue SPF daily.",
            "Noon <b>Igloo Moist</b> may be added for additional hydration comfort.",
        ]),
        ("Day 5+", [
            "Begin reintroducing Noon concern-specific products — start with gentle options "
            "(<b>Halo-Ronic Serum</b>, <b>HydroCalming + Vit Complex</b>).",
            "Return to full Noon protocol appropriate to your skin concern by Week 2.",
        ]),
    ])

    s.append(GoldBar(col_width, thickness=0.8))
    s.append(Spacer(1, 10))

    # Ablative
    s.append(Paragraph("Ablative Mode", styles["section_label"]))
    s += section_block("", [], styles, col_width, day_groups=[
        ("Days 1–5 (Active Healing)", [
            "Apply <b>Epicutis full recovery protocol</b> up to 4× daily: "
            "Oil Cleanser → Lipid Serum → HYVIA Crème → Lipid Recovery Mask.",
            "Keep skin continuously moisturised — do not allow treated areas to dry out.",
            "Do not pick, peel, or rub any flaking or crusting — allow natural shedding.",
            "Social downtime of <b>5–10 days</b> is typical — plan accordingly.",
        ]),
        ("Week 2+", [
            "Begin broad-spectrum <b>SPF 50+</b> as soon as re-epithelialization is complete.",
            "No retinoids, AHAs, BHAs, or vitamin C until your physician clears their reintroduction — "
            "typically 2 weeks minimum.",
            "<b>Strict sun avoidance</b> for a minimum of 2 weeks — any UV exposure risks pigmentation.",
            "Follow-up <b>OBSERV 360 skin analysis</b> at 4–6 weeks post-treatment to assess results.",
        ]),
    ])

    # General rules (both modes)
    s += section_block("General Rules — Both Modes", [
        "No makeup for <b>24–48 hours</b> post-treatment (longer for ablative).",
        "Avoid heat exposure — saunas, hot yoga, steam rooms, very hot showers — for <b>72 hours</b>.",
        "No swimming in chlorinated water for <b>5 days</b>.",
        "Sleep on a <b>clean pillowcase</b>; consider elevated head position for the first 2 nights.",
        "Avoid vigorous exercise for <b>48 hours</b> — elevated body temperature slows healing.",
        "Call us immediately if you develop <b>blistering, significant swelling, or signs of infection</b>.",
    ], styles, col_width)

    s.append(Spacer(1, 12))
    s.append(GoldBar(col_width))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your next treatment will be booked 4 weeks after NOUVAGlo, or as directed by your physician for Ablative mode. "
        "Contact us at <b>aesthetics@treasuryhealth.ca</b> with any concerns.",
        styles["note"]
    ))

    return s


# ══════════════════════════════════════════════════════════════════════
# PLADUO PRO — Pre-Treatment
# ══════════════════════════════════════════════════════════════════════

def pladuo_pre(styles, col_width):
    s = []

    s.append(Paragraph(
        "PlaDuo Pro uses patented SpinShot Technology to deliver both nitrogen plasma and argon plasma. "
        "These simple preparation steps maximise efficacy and safety.",
        styles["body"]
    ))
    s.append(Spacer(1, 6))

    s += section_block("Skincare Preparation", [
        "Your provider may apply <b>AMP D|TOX Pre-Treatment Skincare Serum</b> at the start of your appointment — "
        "no prep action required from you.",
        "Discontinue <b>retinoids and AHA/BHA exfoliants</b> 3–5 days before your appointment.",
        "Arrive with <b>clean, makeup-free skin</b>. No serums, oils, or moisturisers on the treatment area.",
        "Avoid using any <b>harsh or active skincare</b> on the day before treatment.",
    ], styles, col_width)

    s += section_block("Sun & Lifestyle", [
        "Avoid <b>direct sun exposure and tanning beds</b> for 2 weeks prior.",
        "Do not use <b>self-tanner</b> for 2 weeks prior.",
        "If you have a history of <b>cold sores (HSV)</b>, inform your provider — "
        "antiviral prophylaxis may be prescribed.",
        "Do not use <b>isotretinoin (Accutane)</b> within 6 months of treatment.",
    ], styles, col_width)

    s += section_block("Acne & Rosacea Patients — Additional Notes", [
        "If you are being treated with <b>PlaDuo Pro Argon</b> for active acne: "
        "your provider may schedule more frequent initial sessions (weekly) to achieve clearance before spacing out.",
        "A temporary <b>purging period</b> is normal and expected after Argon plasma for acne — this is a sign the treatment is working.",
        "Continue any prescribed oral or topical acne medications unless your physician advises otherwise.",
        "For rosacea: avoid spicy foods, alcohol, and temperature extremes in the 48 hours before treatment.",
    ], styles, col_width)

    s += section_block("Day of Treatment", [
        "Arrive with completely clean skin — no SPF, makeup, or skincare products.",
        "Topical anaesthetic is not routinely required for PlaDuo Pro, but inform your provider "
        "if you have low pain tolerance.",
        "Treatment sessions are typically 30–45 minutes.",
    ], styles, col_width)

    s.append(Spacer(1, 12))
    s.append(GoldBar(col_width))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Questions before your appointment? Contact us at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))

    return s


# ══════════════════════════════════════════════════════════════════════
# PLADUO PRO — Post-Treatment
# ══════════════════════════════════════════════════════════════════════

def pladuo_post(styles, col_width):
    s = []

    s.append(Paragraph(
        "PlaDuo Pro treatments are low-downtime, but your skin still benefits from careful post-care "
        "to maximise results and protect the treated barrier.",
        styles["body"]
    ))
    s.append(Spacer(1, 6))

    s += section_block("Immediately After Treatment", [
        "<b>EXO|E Skin Revitalizing Complex</b> (AMP exosome product) is applied immediately post-procedure in-clinic.",
        "<b>RE|PAIR Post-Treatment Skincare Serum</b> (AMP) helps maintain hydration and minimise redness.",
        "Mild redness and warmth are normal for 24–48 hours, particularly after Argon mode.",
        "Do not touch or rub the treated area for the first few hours.",
    ], styles, col_width)

    s += section_block("", [], styles, col_width, day_groups=[
        ("Days 1–2", [
            "Cleanse gently with a non-foaming, fragrance-free cleanser or <b>Epicutis Oil Cleanser</b>.",
            "Apply <b>Epicutis Lipid Recovery Mask</b> as a soothing barrier layer.",
            "Follow with <b>Epicutis Lipid Serum + HYVIA Crème</b> 2× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — do not skip.",
            "No active skincare: avoid retinoids, AHAs, BHAs, and vitamin C.",
        ]),
        ("Days 3–5", [
            "Continue Epicutis Lipid Serum + HYVIA Crème for barrier support.",
            "Most patients experience minimal visible downtime by Day 2–3.",
            "Continue SPF diligently — plasma treatments increase photosensitivity.",
            "Avoid exfoliants until Day 5 minimum.",
        ]),
        ("Day 5+", [
            "Reintroduce your Noon concern-specific skincare gradually.",
            "For acne: resume <b>Noon Lacto-S Oil Control</b> + <b>Noon S-Peel</b> as tolerated.",
            "For rosacea: resume <b>Noon HydroCalming + Vit Complex</b> + <b>Noon MicroSoft Cleanser</b>.",
            "Return to full protocol by Week 2.",
        ]),
    ])

    s += section_block("General Rules", [
        "Avoid <b>makeup</b> for 24 hours post-treatment.",
        "Avoid <b>heat</b> (saunas, steam, hot yoga) for 48 hours.",
        "No <b>swimming</b> in chlorinated water for 3 days.",
        "Avoid vigorous exercise for <b>24–48 hours</b>.",
        "<b>Acne patients:</b> an initial purging phase is expected — call us if cysts become painful or widespread.",
        "Contact us immediately for blistering, significant swelling, or signs of infection.",
    ], styles, col_width)

    s += section_block("Session Frequency", [
        "<b>Acne protocol (Argon mode):</b> weekly sessions for the first 4 weeks, then monthly maintenance.",
        "<b>Rosacea/skin quality (Argon or Nitrogen):</b> every 4 weeks for 4–6 sessions.",
        "<b>Biologics add-on:</b> EXO|E Skin Revitalizing Complex or Avari Purasomes applied at each session "
        "for enhanced regeneration.",
    ], styles, col_width)

    s.append(Spacer(1, 12))
    s.append(GoldBar(col_width))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your next session will be scheduled as per your treatment protocol. "
        "Reach us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))

    return s


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))

    print("Generating Treasury Aesthetics care PDFs…")

    build_pdf(
        os.path.join(out, "NouvaDerm_Pre_Treatment_Care.pdf"),
        "NouvaDerm", "1927nm Thulium Fractional Laser  ·  Pre-Treatment Instructions",
        "Pre-Treatment Care",
        nouvaderm_pre,
    )
    build_pdf(
        os.path.join(out, "NouvaDerm_Post_Treatment_Care.pdf"),
        "NouvaDerm", "1927nm Thulium Fractional Laser  ·  Post-Treatment Instructions",
        "Post-Treatment Care",
        nouvaderm_post,
    )
    build_pdf(
        os.path.join(out, "PlaDuo_Pro_Pre_Treatment_Care.pdf"),
        "PlaDuo Pro", "Dual Plasma (Nitrogen + Argon)  ·  Pre-Treatment Instructions",
        "Pre-Treatment Care",
        pladuo_pre,
    )
    build_pdf(
        os.path.join(out, "PlaDuo_Pro_Post_Treatment_Care.pdf"),
        "PlaDuo Pro", "Dual Plasma (Nitrogen + Argon)  ·  Post-Treatment Instructions",
        "Post-Treatment Care",
        pladuo_post,
    )

    print("Done — 4 PDFs created.")
