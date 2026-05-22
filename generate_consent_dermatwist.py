"""
Generate DermaTwist CIT Informed Consent Form — Treasury Aesthetics
Run: python3 generate_consent_dermatwist.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.platypus.flowables import Flowable

# ── Brand colours ───────────────────────────────────────────────────
CHARCOAL  = colors.HexColor("#0C0C0C")
CHARCOAL2 = colors.HexColor("#1A1A1A")
CHARCOAL3 = colors.HexColor("#2A2A2A")
GOLD      = colors.HexColor("#C4954A")
GOLD_LIGHT = colors.HexColor("#D4AF37")
TEXT_MUTED = colors.HexColor("#7A7060")
LIGHT_GREY = colors.HexColor("#F5F4F2")
MID_GREY   = colors.HexColor("#DDDBD7")
WHITE     = colors.white


# ── Custom Flowables ────────────────────────────────────────────────
class GoldBar(Flowable):
    def __init__(self, width, thickness=1.5):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness

    def draw(self):
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, 0, self.width, self.thickness, fill=1, stroke=0)

    def wrap(self, *args):
        return self.width, self.thickness + 4


class SectionHeader(Flowable):
    """Dark charcoal band with gold left accent and white label."""
    def __init__(self, width, label):
        Flowable.__init__(self)
        self.width = width
        self.label = label
        self.height = 22

    def draw(self):
        self.canv.setFillColor(CHARCOAL3)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, 0, 4, self.height, fill=1, stroke=0)
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 8)
        self.canv.drawString(12, 7, self.label.upper())

    def wrap(self, *args):
        return self.width, self.height + 6


class SignatureLine(Flowable):
    """Draws a labelled signature / date line."""
    def __init__(self, width, label, line_width=None):
        Flowable.__init__(self)
        self.width = width
        self.label = label
        self.line_width = line_width or (width * 0.65)
        self.height = 28

    def draw(self):
        self.canv.setStrokeColor(CHARCOAL)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 8, self.line_width, 8)
        self.canv.setFillColor(TEXT_MUTED)
        self.canv.setFont("Helvetica", 7)
        self.canv.drawString(0, 0, self.label)

    def wrap(self, *args):
        return self.width, self.height


class CheckBox(Flowable):
    """Simple checkbox with label text."""
    def __init__(self, width, text, style, indent=0):
        Flowable.__init__(self)
        self.width = width
        self.text = text
        self.style = style
        self.indent = indent
        self.height = 16

    def draw(self):
        self.canv.setStrokeColor(CHARCOAL)
        self.canv.setLineWidth(0.7)
        self.canv.rect(self.indent, 2, 9, 9, fill=0, stroke=1)

    def wrap(self, *args):
        return self.width, self.height


# ── Styles ──────────────────────────────────────────────────────────
def make_styles():
    return {
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=13,
            textColor=WHITE, leading=17, alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=8,
            textColor=GOLD, leading=11, alignment=TA_CENTER, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=8.5,
            textColor=CHARCOAL, leading=12, spaceAfter=3, alignment=TA_JUSTIFY,
        ),
        "body_bold": ParagraphStyle(
            "body_bold", fontName="Helvetica-Bold", fontSize=8.5,
            textColor=CHARCOAL, leading=12, spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=8.5,
            textColor=CHARCOAL, leading=12, spaceAfter=2,
            leftIndent=14, firstLineIndent=-14,
        ),
        "bullet_indent": ParagraphStyle(
            "bullet_indent", fontName="Helvetica", fontSize=8.5,
            textColor=CHARCOAL, leading=12, spaceAfter=2,
            leftIndent=28, firstLineIndent=-14,
        ),
        "note": ParagraphStyle(
            "note", fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=TEXT_MUTED, leading=10, spaceAfter=2,
        ),
        "field_label": ParagraphStyle(
            "field_label", fontName="Helvetica", fontSize=7.5,
            textColor=TEXT_MUTED, leading=10, spaceAfter=1,
        ),
        "check_label": ParagraphStyle(
            "check_label", fontName="Helvetica", fontSize=8.5,
            textColor=CHARCOAL, leading=12, spaceAfter=2,
            leftIndent=16,
        ),
        "warning": ParagraphStyle(
            "warning", fontName="Helvetica-Bold", fontSize=8,
            textColor=colors.HexColor("#8B1A1A"), leading=11, spaceAfter=3,
        ),
        "section_note": ParagraphStyle(
            "section_note", fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=TEXT_MUTED, leading=10, spaceAfter=4,
            leftIndent=4,
        ),
    }


# ── Page callback ────────────────────────────────────────────────────
def make_page_callback():
    counter = [1]

    def on_page(canvas_obj, doc):
        w, h = letter
        margin = 0.65 * inch
        header_h = 1.4 * inch

        canvas_obj.saveState()

        # Header background
        canvas_obj.setFillColor(CHARCOAL2)
        canvas_obj.rect(0, h - header_h, w, header_h, fill=1, stroke=0)

        # Gold top strip
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, h - 3, w, 3, fill=1, stroke=0)

        # Clinic line
        canvas_obj.setFillColor(GOLD)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(w / 2, h - 0.36 * inch,
                                     "TREASURY AESTHETICS  ·  TORONTO, ONTARIO  ·  DR. JASON LATSKY, MD")

        # Title
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica-Bold", 18)
        canvas_obj.drawString(margin, h - 0.78 * inch, "DermaTwist CIT")

        # Subtitle
        canvas_obj.setFillColor(TEXT_MUTED)
        canvas_obj.setFont("Helvetica", 8.5)
        canvas_obj.drawString(margin, h - 0.97 * inch,
                              "Collagen Induction Therapy  ·  Informed Consent & Patient Agreement")

        # Consent badge
        badge = "INFORMED CONSENT"
        bw = canvas_obj.stringWidth(badge, "Helvetica-Bold", 7) + 16
        bx = w - margin - bw
        by = h - 1.04 * inch
        canvas_obj.setFillColor(GOLD)
        canvas_obj.roundRect(bx, by, bw, 18, 3, fill=1, stroke=0)
        canvas_obj.setFillColor(CHARCOAL)
        canvas_obj.setFont("Helvetica-Bold", 7)
        canvas_obj.drawCentredString(bx + bw / 2, by + 5.5, badge)

        # Gold bottom rule on header
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, h - header_h, w, 1.5, fill=1, stroke=0)

        # Footer
        canvas_obj.setFillColor(CHARCOAL3)
        canvas_obj.rect(0, 0, w, 0.42 * inch, fill=1, stroke=0)
        canvas_obj.setFillColor(TEXT_MUTED)
        canvas_obj.setFont("Helvetica", 6.5)
        canvas_obj.drawString(margin, 0.15 * inch,
            "Treasury Aesthetics  ·  aesthetics@treasuryhealth.ca  ·  treasuryhealth.ca  ·  CONFIDENTIAL")
        canvas_obj.drawRightString(w - margin, 0.15 * inch, f"Page {counter[0]}")
        counter[0] += 1

        canvas_obj.restoreState()

    return on_page


# ── Patient info table ───────────────────────────────────────────────
def patient_info_table(cw, styles):
    """Renders labelled blank fields for patient demographics."""
    fields = [
        ("Full Legal Name", "Date of Birth (YYYY-MM-DD)"),
        ("Health Card / Photo ID #", "Date of Treatment"),
        ("Email Address", "Phone Number"),
        ("Referring Provider / How Did You Hear About Us?", ""),
    ]

    cell_style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_MUTED),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, CHARCOAL),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]

    table_data = []
    for left, right in fields:
        if right:
            table_data.append([left, right])
        else:
            table_data.append([left, ""])

    col_w = cw / 2 - 4
    t = Table(table_data, colWidths=[col_w, col_w + 8], rowHeights=28)
    t.setStyle(TableStyle(cell_style))
    return t


# ── Helpers ──────────────────────────────────────────────────────────
def b(text):
    return f"<b>{text}</b>"


def check(label, styles, story, indent=False):
    """Append a checkbox + label pair."""
    st = "bullet_indent" if indent else "bullet"
    story.append(Paragraph("☐  " + label, styles["check_label"]))


def bullet(text, styles, story, indent=False):
    st = "bullet_indent" if indent else "bullet"
    story.append(Paragraph("•  " + text, styles[st]))


def risk_table(rows, cw, styles):
    """Two-column risk table: Risk | Notes."""
    header = [
        Paragraph("Risk / Side Effect", styles["body_bold"]),
        Paragraph("Details", styles["body_bold"]),
    ]
    data = [header]
    for risk, detail in rows:
        data.append([
            Paragraph(risk, styles["body"]),
            Paragraph(detail, styles["body"]),
        ])

    t = Table(data, colWidths=[cw * 0.35, cw * 0.65])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CHARCOAL3),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ── Main content ─────────────────────────────────────────────────────
def build_consent(styles, cw):
    s = []

    # ── PATIENT INFORMATION ──────────────────────────────────────────
    s.append(SectionHeader(cw, "1.  Patient Information"))
    s.append(Spacer(1, 4))
    s.append(patient_info_table(cw, styles))
    s.append(Spacer(1, 6))

    # ── ABOUT DERMATWIST CIT ─────────────────────────────────────────
    s.append(SectionHeader(cw, "2.  About DermaTwist — Collagen Induction Therapy (CIT)"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "DermaTwist delivers <b>Collagen Induction Therapy (CIT)</b> through a mechanical microneedling "
        "device. A cartridge of fine, sterile needles is passed over the skin, creating thousands of "
        "controlled micro-injuries in the dermis. This triggers the body's natural wound-healing cascade — "
        "stimulating new collagen and elastin production — without removing or ablating the skin surface.",
        styles["body"]
    ))
    s.append(Paragraph(
        "At Treasury Aesthetics, DermaTwist is performed on the face, neck, décolleté, and scalp "
        "(for hair restoration). It is routinely paired with regenerative biologics (EXO|E, Avari Purasomes, "
        "DE|RIVE, KeraFactor) applied at the time of treatment to maximise the biological response.",
        styles["body"]
    ))
    s.append(Spacer(1, 4))

    s.append(Paragraph("Indications treated at Treasury Aesthetics:", styles["body_bold"]))
    for item in [
        "Acne scarring — rolling scars, boxcar scars, shallow atrophic scars",
        "Fine lines and early wrinkles",
        "Skin texture and enlarged pores",
        "Stretch marks (striae distensae)",
        "General skin quality, tone, and radiance",
        "Scalp and hair restoration (thinning hair, early androgenetic alopecia)",
    ]:
        bullet(item, styles, s)
    s.append(Spacer(1, 4))

    s.append(Paragraph(
        "<b>Needle depth and session parameters</b> are calibrated by the provider to your skin "
        "concern, anatomy, and tolerance. Depths typically range from 0.5 mm (fine lines, texture) "
        "to 2.5 mm (deep scars, scalp). Your provider will document the settings used at each visit.",
        styles["body"]
    ))
    s.append(Spacer(1, 4))

    # ── EXPECTED OUTCOMES ────────────────────────────────────────────
    s.append(SectionHeader(cw, "3.  Expected Outcomes & Realistic Expectations"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "Results from CIT are <b>gradual and cumulative</b>. Collagen remodeling occurs over weeks to months "
        "following each session — not immediately after treatment. Most patients require a course of "
        "treatments to achieve their goals.",
        styles["body"]
    ))

    outcome_data = [
        [Paragraph("<b>Concern</b>", styles["body_bold"]),
         Paragraph("<b>Typical Course</b>", styles["body_bold"]),
         Paragraph("<b>Onset of Visible Results</b>", styles["body_bold"])],
        [Paragraph("Acne scarring", styles["body"]),
         Paragraph("4–6 sessions, 4 weeks apart", styles["body"]),
         Paragraph("6–12 weeks after first session; full result at 3–6 months post-series", styles["body"])],
        [Paragraph("Fine lines / texture", styles["body"]),
         Paragraph("3–4 sessions, 4 weeks apart", styles["body"]),
         Paragraph("4–8 weeks", styles["body"])],
        [Paragraph("Stretch marks", styles["body"]),
         Paragraph("4–6 sessions, 4–6 weeks apart", styles["body"]),
         Paragraph("3–6 months", styles["body"])],
        [Paragraph("Scalp / hair restoration", styles["body"]),
         Paragraph("Monthly sessions × 4–6", styles["body"]),
         Paragraph("3–6 months; shedding may increase initially", styles["body"])],
    ]
    outcome_table = Table(outcome_data, colWidths=[cw * 0.28, cw * 0.30, cw * 0.42])
    outcome_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CHARCOAL3),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    s.append(outcome_table)
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "No provider or clinic can guarantee specific results. Individual outcomes depend on age, "
        "skin type, genetics, lifestyle, adherence to post-care instructions, and biological variation. "
        "Maintenance sessions may be required after the initial series.",
        styles["note"]
    ))
    s.append(Spacer(1, 4))

    # ── RISKS AND SIDE EFFECTS ───────────────────────────────────────
    s.append(SectionHeader(cw, "4.  Risks, Side Effects & Possible Complications"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "DermaTwist CIT is a well-established procedure with an excellent safety profile when performed "
        "by a trained provider. The following risks have been disclosed to me and I understand them:",
        styles["body"]
    ))
    s.append(Spacer(1, 4))

    s.append(Paragraph("COMMON — expected and typically resolve within days:", styles["body_bold"]))
    s.append(risk_table([
        ("Redness (erythema)", "Expected for 24–72 hours. Similar in appearance to moderate sunburn. Resolves without treatment."),
        ("Swelling (oedema)", "Mild swelling, especially around eyes and cheeks. Peaks at 24–48 hours, resolves within 3–5 days."),
        ("Pinpoint bleeding", "Microscopic during treatment — normal and expected at deeper settings. Stops immediately."),
        ("Skin sensitivity / tightness", "Skin feels tight, tender, and sensitive to touch for 2–5 days post-procedure."),
        ("Dryness and flaking", "Surface flaking as skin sheds and renews. Do not pick or peel — allow natural shedding."),
        ("Temporary discolouration", "Mild bronzing or uneven tone for 3–7 days. Not permanent."),
    ], cw, styles))
    s.append(Spacer(1, 4))

    s.append(Paragraph("UNCOMMON — occur in a minority of patients:", styles["body_bold"]))
    s.append(risk_table([
        ("Prolonged redness", "Erythema persisting beyond 7 days. More common at deeper settings or in sensitive skin. Usually self-resolving."),
        ("Post-inflammatory hyperpigmentation (PIH)", "Temporary darkening of the skin, more common in Fitzpatrick IV–VI. Risk is reduced with Noon DermShield-validated skincare and diligent SPF use. Typically resolves over weeks to months."),
        ("Herpes simplex (cold sore) reactivation", "Patients with a history of HSV are at risk. Antiviral prophylaxis is prescribed prior to treatment to reduce this risk."),
        ("Acne flare", "Temporary worsening of acne in acne-prone patients following treatment. Not a treatment failure — typically resolves within 2 weeks."),
        ("Milia", "Small white cysts that may form as skin heals. Usually resolve spontaneously or with gentle exfoliation."),
        ("Bruising", "Occasional at deeper settings or in patients on blood thinners/supplements. Resolves over 5–10 days."),
    ], cw, styles))
    s.append(Spacer(1, 4))

    s.append(Paragraph("RARE — uncommon but must be disclosed:", styles["body_bold"]))
    s.append(risk_table([
        ("Infection (bacterial)", "Risk is minimised by single-use sterile cartridges, aseptic technique, and proper post-care. Contact clinic immediately if warmth, pus, or spreading redness occurs."),
        ("Scarring", "Extremely rare with CIT when performed correctly. Risk is higher in patients with a history of keloid or hypertrophic scarring — this is a relative contraindication."),
        ("Hypopigmentation", "Lightening of treated skin, rare, most often at aggressive settings in darker skin tones."),
        ("Allergic reaction to biologics", "If exosomes, growth factors, or other add-ons are applied, allergic reaction is possible though very uncommon. Inform provider of any known allergies."),
        ("Unsatisfactory aesthetic outcome", "Results may not meet patient expectations despite technically successful treatment. Additional sessions may be needed."),
    ], cw, styles))
    s.append(Spacer(1, 4))

    s.append(Paragraph(
        "⚠  Contact Treasury Aesthetics immediately or go to an emergency department if you experience: "
        "significant spreading redness with warmth and pain (signs of infection), blistering, facial swelling "
        "beyond Day 3, or any other symptom that concerns you.",
        styles["warning"]
    ))
    s.append(Spacer(1, 4))

    # ── CONTRAINDICATIONS ────────────────────────────────────────────
    s.append(SectionHeader(cw, "5.  Contraindications — Treatment Cannot Proceed If Any Apply"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "I confirm I do <b>NOT</b> have any of the following absolute contraindications. "
        "If any of the below apply, I have disclosed this to my provider:",
        styles["body"]
    ))
    s.append(Spacer(1, 3))

    absolute = [
        "Active skin infection, open sores, cold sores, or rash in the treatment area",
        "Active acne cysts or pustules directly in the treatment zone (relative — provider to assess)",
        "Use of isotretinoin (Accutane / Epuris) within the past 6 months",
        "History of keloid or hypertrophic scarring (relative contraindication — provider to assess)",
        "Blood clotting disorders or use of anticoagulant medications (e.g. warfarin, Xarelto)",
        "Pregnancy or breastfeeding",
        "Immunosuppressive medications or active autoimmune disease affecting skin",
        "Uncontrolled diabetes (impairs wound healing)",
        "Active skin cancer or radiation treatment in the area",
        "Scleroderma or connective tissue disorders affecting the treatment area",
        "Allergy to topical anaesthetic agents (EMLA / lidocaine / prilocaine)",
    ]
    for item in absolute:
        bullet(item, styles, s)
    s.append(Spacer(1, 4))

    # ── PRE-TREATMENT REQUIREMENTS ───────────────────────────────────
    s.append(SectionHeader(cw, "6.  Pre-Treatment Requirements — Patient Obligations"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "I confirm I have followed, or will follow, the pre-treatment instructions below. "
        "Failure to comply may result in rescheduling of my appointment:",
        styles["body"]
    ))
    s.append(Spacer(1, 3))

    pre = [
        "Discontinued <b>retinoids</b> (tretinoin, retinol, retinaldehyde) at least <b>5–7 days</b> before treatment",
        "Discontinued <b>AHA and BHA exfoliants</b> (glycolic, lactic, salicylic acids) at least <b>5 days</b> before treatment",
        "Not used <b>self-tanner</b> for at least <b>2 weeks</b> prior",
        "Avoided <b>direct sun exposure and tanning beds</b> for at least <b>2 weeks</b> prior",
        "Avoided <b>blood thinners and supplements</b> (fish oil, vitamin E, aspirin unless prescribed by physician) for <b>5–7 days</b> prior",
        "No active skin infection or open breakouts in the treatment zone",
        "Not on isotretinoin (Accutane / Epuris) within the past 6 months",
        "Disclosed history of <b>cold sores (HSV)</b> to provider — antiviral prescription arranged if applicable",
        "Arriving with <b>clean, makeup-free skin</b> — no creams, serums, SPF, or any product on the face or scalp",
        "Arranged transport if concerned about tolerating topical anaesthetic",
    ]
    for item in pre:
        bullet(item, styles, s)
    s.append(Spacer(1, 4))

    # ── POST-TREATMENT RESPONSIBILITIES ─────────────────────────────
    s.append(SectionHeader(cw, "7.  Post-Treatment Responsibilities — Patient Obligations"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "I understand and agree to follow the post-treatment protocol provided to me. "
        "Non-compliance with post-care significantly increases the risk of complications and poor outcomes. "
        "Key obligations include:",
        styles["body"]
    ))
    s.append(Spacer(1, 3))

    post = [
        "Use only provider-approved products for the first <b>5–7 days</b>: Hale Derma Cleanser, Epicutis Lipid Serum, HYVIA Crème, Epicutis Lipid Recovery Mask, and Epicutis Hydrobiome Mist (or approved generic equivalents)",
        "Apply <b>broad-spectrum SPF 50+</b> every morning from Day 1 — non-negotiable",
        "Apply <b>no makeup</b> for at least <b>24–48 hours</b> after treatment",
        "Avoid heat: <b>no saunas, hot yoga, steam rooms, or very hot showers</b> for at least <b>48–72 hours</b>",
        "Avoid <b>vigorous exercise</b> for <b>24–48 hours</b> (sweating introduces bacteria to open micro-channels)",
        "Avoid <b>swimming in chlorinated water</b> for <b>5 days</b>",
        "Sleep on a <b>clean pillowcase</b> for the first 3 nights; elevated head position recommended",
        "<b>Do not pick, scratch, peel, or rub</b> the treated area — allow natural shedding",
        "<b>Do not apply retinoids, AHAs, BHAs, or vitamin C</b> for at least <b>5–7 days</b> after treatment",
        "For scalp treatments: avoid washing scalp for <b>24 hours</b>; no heat styling for <b>48 hours</b>; no chemical treatments (colour, relaxers, bleach) for <b>2 weeks</b>",
        "Contact Treasury Aesthetics immediately if I experience signs of infection, blistering, significant swelling beyond Day 3, or any concerning symptoms",
    ]
    for item in post:
        bullet(item, styles, s)
    s.append(Spacer(1, 4))

    # ── BIOLOGICS & ADD-ONS ──────────────────────────────────────────
    s.append(SectionHeader(cw, "8.  Biologics & Add-On Treatments"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "The following regenerative biologics and add-ons may be applied at the time of my DermaTwist treatment. "
        "These products are applied topically into the micro-channels immediately post-needling to maximise "
        "absorption and biological effect. I have been informed of the following:",
        styles["body"]
    ))
    s.append(Spacer(1, 3))

    bio_data = [
        [Paragraph("<b>Product</b>", styles["body_bold"]),
         Paragraph("<b>Type</b>", styles["body_bold"]),
         Paragraph("<b>Role</b>", styles["body_bold"]),
         Paragraph("<b>Include?</b>", styles["body_bold"])],
        [Paragraph("EXO|E Skin Revitalizing Complex", styles["body"]),
         Paragraph("Plant-derived exosome nanoparticles (PDENs)", styles["body"]),
         Paragraph("Skin recovery, collagen signalling, anti-inflammatory", styles["body"]),
         Paragraph("☐  Yes  ☐  No", styles["body"])],
        [Paragraph("Avari Purasomes", styles["body"]),
         Paragraph("True mammalian exosomes (premium)", styles["body"]),
         Paragraph("Strongest biological recovery signal; hair follicle stimulation when used on scalp", styles["body"]),
         Paragraph("☐  Yes  ☐  No", styles["body"])],
        [Paragraph("VAMP Advanced PDRN", styles["body"]),
         Paragraph("Polynucleotide tissue repair (PDRN)", styles["body"]),
         Paragraph("DNA fragment tissue repair, anti-inflammatory, wound healing support", styles["body"]),
         Paragraph("☐  Yes  ☐  No", styles["body"])],
        [Paragraph("DE|RIVE Scalp Treatment", styles["body"]),
         Paragraph("Exosome/plant-derived (scalp)", styles["body"]),
         Paragraph("Applied post-scalp needling for hair follicle stimulation", styles["body"]),
         Paragraph("☐  Yes  ☐  No", styles["body"])],
        [Paragraph("KeraFactor Growth Factor Serum", styles["body"]),
         Paragraph("Growth factor complex (scalp)", styles["body"]),
         Paragraph("Hair density support; massaged into scalp post-needling", styles["body"]),
         Paragraph("☐  Yes  ☐  No", styles["body"])],
    ]
    bio_table = Table(bio_data, colWidths=[cw * 0.26, cw * 0.22, cw * 0.34, cw * 0.18])
    bio_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CHARCOAL3),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    s.append(bio_table)
    s.append(Spacer(1, 3))
    s.append(Paragraph(
        "All biologics are Health Canada compliant. I confirm no known allergy to any of the above "
        "products. I understand that exosomes and growth factors are professional-grade adjuncts to "
        "treatment and results cannot be guaranteed.",
        styles["note"]
    ))
    s.append(Spacer(1, 4))

    # ── PHOTOGRAPHY CONSENT ──────────────────────────────────────────
    s.append(SectionHeader(cw, "9.  Clinical Photography & Documentation"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "Standard of care at Treasury Aesthetics includes clinical photography before and after treatments "
        "using the OBSERV 360 imaging system and standard photography. Images are stored securely in our "
        "EMR (Phorest) and are used for:",
        styles["body"]
    ))
    s.append(Spacer(1, 3))
    for item in [
        "Tracking treatment progress and outcomes",
        "Provider review and treatment planning",
        "Quality assurance and clinical education (internal use only, unless additional consent is granted below)",
    ]:
        bullet(item, styles, s)
    s.append(Spacer(1, 4))

    s.append(Paragraph("Please indicate your consent preferences:", styles["body_bold"]))
    s.append(Spacer(1, 3))
    check("I consent to clinical photography for my personal medical record and treatment planning.", styles, s)
    check("I consent to de-identified (face not shown / cropped) before/after photos for educational and internal staff training purposes.", styles, s)
    check("I consent to de-identified before/after photos for use on Treasury Aesthetics' social media and marketing materials.", styles, s)
    check("I do NOT consent to any use of my images beyond my personal medical record.", styles, s)
    s.append(Spacer(1, 4))

    # ── FINANCIAL POLICY ─────────────────────────────────────────────
    s.append(SectionHeader(cw, "10.  Financial Policy & Cancellation"))
    s.append(Spacer(1, 4))
    for item in [
        "All treatments are non-refundable once performed, regardless of outcome, unless there is a documented clinical error.",
        "Prepaid treatment packages are transferable to other services at equivalent value but are non-refundable.",
        "Cancellation with less than <b>24 hours notice</b> will incur a cancellation fee as outlined in the booking confirmation.",
        "I understand that results from CIT develop over time and that additional sessions may be recommended to achieve my goals. These are not included in the price of the initial session unless expressly agreed in writing.",
        "Treatment of complications arising from contraindicated behaviour (e.g., sun exposure, non-compliance with post-care) is billable.",
    ]:
        bullet(item, styles, s)
    s.append(Spacer(1, 4))

    # ── PATIENT ACKNOWLEDGEMENTS ─────────────────────────────────────
    s.append(SectionHeader(cw, "11.  Patient Acknowledgements & Declarations"))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "By initialling or checking each item below, I confirm I have read, understood, and agree "
        "to the following:",
        styles["body"]
    ))
    s.append(Spacer(1, 4))

    acknowledgements = [
        ("I have read and understood the full description of DermaTwist Collagen Induction Therapy, "
         "including how it works, its indications, and its limitations."),
        ("I understand that results are gradual, cumulative, and cannot be guaranteed. Individual "
         "results vary based on genetics, skin type, lifestyle, age, and compliance with post-care instructions."),
        ("I have been informed of all common, uncommon, and rare risks and side effects as listed in "
         "Section 4 of this document. I have had the opportunity to ask questions and all my questions "
         "have been answered to my satisfaction."),
        ("I confirm that none of the absolute contraindications listed in Section 5 apply to me, "
         "OR I have disclosed any relevant conditions to my provider prior to proceeding."),
        ("I confirm I will follow all pre-treatment and post-treatment instructions as outlined in "
         "Sections 6 and 7. I understand that non-compliance may lead to complications or suboptimal "
         "results, and that Treasury Aesthetics cannot be held responsible for outcomes resulting from "
         "non-compliance."),
        ("I understand the biologics and add-on treatments being applied (as selected in Section 8) "
         "and have confirmed no known allergies to those products."),
        ("I understand the financial and cancellation policy as outlined in Section 10."),
        ("I understand that topical anaesthetic (EMLA or equivalent) will be applied in-clinic prior "
         "to treatment. I have disclosed any known allergy to local anaesthetic agents."),
        ("I am 18 years of age or older, OR a parent / legal guardian has consented on my behalf "
         "(guardian must co-sign below)."),
        ("I consent to this treatment and have not been coerced. I understand I may withdraw consent "
         "at any time before or during treatment, and that refusing treatment will not negatively "
         "affect my care at Treasury Aesthetics."),
    ]

    for i, ack in enumerate(acknowledgements, 1):
        # Initials box + text
        ack_data = [[
            Paragraph(f"☐  Initials: _______", styles["field_label"]),
            Paragraph(f"<b>{i}.</b>  {ack}", styles["body"]),
        ]]
        ack_table = Table(ack_data, colWidths=[cw * 0.18, cw * 0.82])
        ack_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, LIGHT_GREY),
        ]))
        s.append(ack_table)

    s.append(Spacer(1, 6))

    # ── SIGNATURE BLOCK ──────────────────────────────────────────────
    s.append(SectionHeader(cw, "12.  Signatures"))
    s.append(Spacer(1, 6))

    sig_data = [
        [
            Paragraph("Patient / Legal Guardian Signature", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Print Full Name", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Date", styles["field_label"]),
        ],
        [
            Paragraph("_" * 38, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 28, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 14, styles["body"]),
        ],
    ]
    sig_table = Table(sig_data, colWidths=[cw * 0.38, 0.08 * inch, cw * 0.30, 0.08 * inch, cw * 0.22])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]))
    s.append(sig_table)
    s.append(Spacer(1, 10))

    # Guardian section (minor patients)
    s.append(Paragraph(
        "If the patient is a minor (under 18 years of age), a parent or legal guardian must also sign:",
        styles["section_note"]
    ))
    s.append(Spacer(1, 3))
    guardian_data = [
        [
            Paragraph("Guardian Signature", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Print Name", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Relationship to Patient", styles["field_label"]),
        ],
        [
            Paragraph("_" * 38, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 28, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 22, styles["body"]),
        ],
    ]
    guardian_table = Table(guardian_data, colWidths=[cw * 0.38, 0.08 * inch, cw * 0.30, 0.08 * inch, cw * 0.22])
    guardian_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]))
    s.append(guardian_table)
    s.append(Spacer(1, 10))

    # Provider sign-off
    s.append(GoldBar(cw, thickness=0.8))
    s.append(Spacer(1, 6))
    s.append(Paragraph("For Treasury Aesthetics Staff Use Only", styles["body_bold"]))
    s.append(Spacer(1, 3))

    staff_data = [
        [
            Paragraph("Provider / Injector Name (Print)", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Provider Signature", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Date", styles["field_label"]),
        ],
        [
            Paragraph("_" * 30, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 30, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 14, styles["body"]),
        ],
    ]
    staff_table = Table(staff_data, colWidths=[cw * 0.34, 0.08 * inch, cw * 0.34, 0.08 * inch, cw * 0.20])
    staff_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]))
    s.append(staff_table)
    s.append(Spacer(1, 6))

    treat_data = [
        [
            Paragraph("Treatment Area(s)", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Needle Depth(s) Used (mm)", styles["field_label"]),
            Spacer(1, 1),
            Paragraph("Biologics Applied", styles["field_label"]),
        ],
        [
            Paragraph("_" * 30, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 22, styles["body"]),
            Spacer(1, 1),
            Paragraph("_" * 28, styles["body"]),
        ],
    ]
    treat_table = Table(treat_data, colWidths=[cw * 0.34, 0.08 * inch, cw * 0.28, 0.08 * inch, cw * 0.26])
    treat_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]))
    s.append(treat_table)
    s.append(Spacer(1, 8))

    s.append(GoldBar(cw))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "This signed consent form is retained in the patient's medical record. "
        "A copy is available to the patient upon request. "
        "Treasury Aesthetics · aesthetics@treasuryhealth.ca · treasuryhealth.ca",
        styles["note"]
    ))
    return s


# ── Build ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(out, "DermaTwist_Informed_Consent.pdf")

    margin = 0.65 * inch
    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        leftMargin=margin, rightMargin=margin,
        topMargin=1.55 * inch, bottomMargin=0.55 * inch,
    )
    col_width = letter[0] - 2 * margin
    styles = make_styles()
    story = build_consent(styles, col_width)
    cb = make_page_callback()
    doc.build(story, onFirstPage=cb, onLaterPages=cb)
    print(f"Created: {filename}")
