"""
Generate combined pre & post care PDFs for NouvaDerm and PlaDuo Pro.
Run: python3 generate_care_pdfs.py
Outputs two PDFs in the current directory.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── Brand colours ──────────────────────────────────────────────────
CHARCOAL  = colors.HexColor("#0C0C0C")
CHARCOAL2 = colors.HexColor("#1A1A1A")
CHARCOAL3 = colors.HexColor("#222222")
GOLD      = colors.HexColor("#C4954A")
TEXT_MUTED = colors.HexColor("#7A7060")
WHITE     = colors.white


# ── Helper: italic generic alternative ─────────────────────────────
def alt(text):
    """Wrap generic alternative text in grey italic."""
    return f' <i><font color="#7A7060">({text})</font></i>'


# ── Styles ─────────────────────────────────────────────────────────
def make_styles():
    return {
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9,
            textColor=CHARCOAL, leading=15, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=9,
            textColor=CHARCOAL, leading=15, spaceAfter=5,
            leftIndent=14, firstLineIndent=-14,
        ),
        "section_label": ParagraphStyle(
            "section_label", fontName="Helvetica-Bold", fontSize=7,
            textColor=GOLD, letterSpacing=2, spaceBefore=16, spaceAfter=8,
        ),
        "phase_label": ParagraphStyle(
            "phase_label", fontName="Helvetica-Bold", fontSize=11,
            textColor=CHARCOAL, spaceBefore=20, spaceAfter=6, leading=14,
        ),
        "day_label": ParagraphStyle(
            "day_label", fontName="Helvetica-Bold", fontSize=9,
            textColor=CHARCOAL, leading=14, spaceAfter=4, spaceBefore=10,
        ),
        "note": ParagraphStyle(
            "note", fontName="Helvetica-Oblique", fontSize=8,
            textColor=TEXT_MUTED, leading=13, spaceAfter=4,
        ),
        "divider_label": ParagraphStyle(
            "divider_label", fontName="Helvetica-Bold", fontSize=8,
            textColor=WHITE, letterSpacing=2, alignment=TA_CENTER,
        ),
    }


# ── Flowables ──────────────────────────────────────────────────────
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


class PhaseDivider(Flowable):
    """Full-width dark bar used to separate PRE from POST sections."""
    def __init__(self, width, label):
        Flowable.__init__(self)
        self.width = width
        self.label = label
        self.height = 28

    def draw(self):
        self.canv.setFillColor(CHARCOAL2)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, self.height - 2, self.width, 2, fill=1, stroke=0)
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 8)
        self.canv.drawCentredString(self.width / 2, 9, self.label.upper())

    def wrap(self, *args):
        return self.width, self.height + 8


# ── Section builder ────────────────────────────────────────────────
def section(title, items, styles, day_groups=None):
    story = []
    story.append(Paragraph(title.upper(), styles["section_label"]))
    if day_groups:
        for day, bullets in day_groups:
            story.append(Paragraph(day, styles["day_label"]))
            for b in bullets:
                story.append(Paragraph("•  " + b, styles["bullet"]))
    else:
        for item in items:
            story.append(Paragraph("•  " + item, styles["bullet"]))
    return story


# ── Page callbacks ─────────────────────────────────────────────────
def make_page_callback(device_name, device_sub):
    counter = [1]

    def on_page(canvas_obj, doc):
        w, h = letter
        margin = 0.65 * inch
        header_h = 1.5 * inch

        canvas_obj.saveState()

        # Dark header background
        canvas_obj.setFillColor(CHARCOAL2)
        canvas_obj.rect(0, h - header_h, w, header_h, fill=1, stroke=0)

        # Gold top strip
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, h - 3, w, 3, fill=1, stroke=0)

        # Clinic name
        canvas_obj.setFillColor(GOLD)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(w / 2, h - 0.38 * inch,
                                     "TREASURY AESTHETICS  ·  TORONTO, ONTARIO")

        # Device name
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica-Bold", 20)
        canvas_obj.drawString(margin, h - 0.82 * inch, device_name)

        # Sub-label
        canvas_obj.setFillColor(TEXT_MUTED)
        canvas_obj.setFont("Helvetica", 8.5)
        canvas_obj.drawString(margin, h - 1.02 * inch, device_sub)

        # Badge
        badge = "PRE & POST-TREATMENT CARE"
        bw = canvas_obj.stringWidth(badge, "Helvetica-Bold", 7) + 16
        bx = w - margin - bw
        by = h - 1.08 * inch
        canvas_obj.setFillColor(GOLD)
        canvas_obj.roundRect(bx, by, bw, 18, 3, fill=1, stroke=0)
        canvas_obj.setFillColor(CHARCOAL)
        canvas_obj.setFont("Helvetica-Bold", 7)
        canvas_obj.drawCentredString(bx + bw / 2, by + 5.5, badge)

        # Gold divider at bottom of header
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, h - header_h, w, 1.5, fill=1, stroke=0)

        # Footer
        canvas_obj.setFillColor(CHARCOAL3)
        canvas_obj.rect(0, 0, w, 0.45 * inch, fill=1, stroke=0)
        canvas_obj.setFillColor(TEXT_MUTED)
        canvas_obj.setFont("Helvetica", 6.5)
        canvas_obj.drawString(margin, 0.16 * inch,
            "Treasury Aesthetics  ·  aesthetics@treasuryhealth.ca  ·  treasuryhealth.ca")
        canvas_obj.drawRightString(w - margin, 0.16 * inch, f"Page {counter[0]}")

        counter[0] += 1
        canvas_obj.restoreState()

    return on_page


def build_pdf(filename, device_name, device_sub, content_fn):
    margin = 0.65 * inch
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=margin, rightMargin=margin,
        topMargin=1.65 * inch,
        bottomMargin=0.6 * inch,
    )
    col_width = letter[0] - 2 * margin
    styles = make_styles()
    story = content_fn(styles, col_width)
    cb = make_page_callback(device_name, device_sub)
    doc.build(story, onFirstPage=cb, onLaterPages=cb)
    print(f"  Created: {filename}")


# ══════════════════════════════════════════════════════════════════
# NOUVADERM — Combined
# ══════════════════════════════════════════════════════════════════

def nouvaderm(styles, cw):
    s = []

    # ── PRE-TREATMENT ──────────────────────────────────────────────
    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Please follow these instructions carefully before your NouvaDerm treatment to ensure "
        "the best possible results and minimise any risk of adverse reactions.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "Begin the <b>Noon Pre-Procedure Program (Gear Up Kit)</b>"
        + alt("or your own gentle, fragrance-free prep routine")
        + " 10–14 days prior to your appointment.",
        "Discontinue <b>retinoids</b> (tretinoin, retinol) and <b>AHA/BHA exfoliants</b> 7 days before treatment.",
        "Discontinue <b>vitamin C serums</b> 3–5 days before treatment.",
        "Do not use any <b>self-tanner or sunless bronzer</b> for 2 weeks prior.",
        "Arrive with <b>clean, makeup-free skin</b> — no creams, serums, or SPF.",
    ], styles)

    s += section("Sun & Lifestyle", [
        "Avoid direct <b>sun exposure and tanning beds</b> for 2–4 weeks prior "
        "(2 weeks minimum for NOUVAGlo; strict for Ablative mode).",
        "If you have a history of <b>cold sores (HSV)</b>, antiviral medication will be prescribed — begin as directed.",
        "Avoid <b>Accutane (isotretinoin)</b> within 6 months of treatment (12 months for Ablative).",
        "Discontinue <b>blood thinners and supplements</b> (fish oil, vitamin E, aspirin unless prescribed) 7 days prior.",
    ], styles)

    s += section("Day of Treatment", [
        "Arrive 30–45 minutes early — topical anaesthetic is applied in-clinic and requires time to work.",
        "Avoid caffeine if you are sensitive.",
        "Do <b>not</b> drive yourself home after Ablative mode — arrange transport in advance.",
        "Wear comfortable, loose clothing. Avoid tight collars if treating the neck.",
    ], styles)

    s += section("Medical History — Please Inform Us If You Have:", [
        "Active skin infection, open sores, or rash in the treatment area.",
        "History of keloid or hypertrophic scarring.",
        "Autoimmune conditions or immunosuppressive medications.",
        "Pregnancy or breastfeeding.",
        "Pacemaker or implanted electronic devices.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    # ── POST-TREATMENT ─────────────────────────────────────────────
    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your skin is in an active healing phase. Following these instructions precisely protects "
        "your investment and significantly improves your final result.",
        styles["body"]
    ))

    # NOUVAGlo
    s.append(Paragraph("NOUVAGlo (Non-Ablative Mode)", styles["section_label"]))
    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle, fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free barrier/occlusive mask")
            + " applied in-clinic as first recovery layer.",
            "<b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " applied before leaving the clinic.",
        ]),
        ("Days 1–3", [
            "Cleanse with <b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " or <b>Noon MicroSoft Cleanser</b>"
            + alt("or any gentle sulfate-free cleanser")
            + " — gentle pressure only.",
            "Apply <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " 2–4× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — reapply every 2 hours if outdoors. Non-negotiable.",
            "Mild redness, warmth, and bronzing are expected and normal — do not pick or exfoliate.",
            "No retinoids, AHAs, BHAs, or vitamin C.",
        ]),
        ("Days 3–5", [
            "Continue <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free barrier moisturiser")
            + "; pinpoint micro-crusting is normal — do not pick.",
            "<b>Noon Igloo Moist</b>"
            + alt("or your own lightweight fragrance-free hydrating cream")
            + " may be added for extra comfort.",
            "Continue SPF daily.",
        ]),
        ("Day 5+", [
            "Reintroduce Noon concern-specific products: start with gentle options — "
            "<b>Halo-Ronic Serum</b>"
            + alt("or your own hyaluronic acid serum")
            + ", <b>HydroCalming + Vit Complex</b>"
            + alt("or your own calming antioxidant serum")
            + ".",
            "Return to your full skincare protocol by Week 2.",
        ]),
    ])

    s.append(Spacer(1, 6))
    s.append(GoldBar(cw, thickness=0.8))
    s.append(Spacer(1, 10))

    # Ablative
    s.append(Paragraph("Ablative Mode", styles["section_label"]))
    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle, fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free occlusive barrier mask")
            + " applied in-clinic.",
            "<b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and thick barrier cream")
            + " — apply before leaving.",
        ]),
        ("Days 1–5 (Active Healing)", [
            "Apply <b>Epicutis full recovery protocol</b> up to 4× daily: "
            "Hale Derma Cleanser"
            + alt("or gentle non-foaming cleanser")
            + " → <b>Epicutis Lipid Serum</b>"
            + alt("or fragrance-free hydrating serum")
            + " → <b>HYVIA Crème</b>"
            + alt("or fragrance-free barrier moisturiser")
            + " → <b>Epicutis Lipid Recovery Mask</b>"
            + alt("or occlusive barrier mask")
            + ".",
            "Keep skin continuously moisturised — do not allow treated areas to dry out.",
            "Do <b>not</b> pick, peel, or rub any flaking — allow natural shedding.",
            "Social downtime of <b>5–10 days</b> is typical — plan accordingly.",
        ]),
        ("Week 2+", [
            "Begin <b>SPF 50+</b> as soon as re-epithelialization is complete.",
            "No retinoids, AHAs, BHAs, or vitamin C until your physician clears them — typically 2 weeks minimum.",
            "<b>Strict sun avoidance</b> for a minimum of 2 weeks.",
            "Follow-up <b>OBSERV 360 skin analysis</b> at 4–6 weeks post-treatment to assess results.",
        ]),
    ])

    s += section("General Rules — Both Modes", [
        "No makeup for <b>24–48 hours</b> (longer for Ablative).",
        "Avoid heat — saunas, hot yoga, steam rooms, very hot showers — for <b>72 hours</b>.",
        "No swimming in chlorinated water for <b>5 days</b>.",
        "Sleep on a clean pillowcase; elevated head position recommended for the first 2 nights.",
        "Avoid vigorous exercise for <b>48 hours</b>.",
        "Call us immediately if you develop blistering, significant swelling, or signs of infection.",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "NOUVAGlo series: sessions spaced <b>4 weeks apart</b>. Ablative timing as directed by your physician. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))

    return s


# ══════════════════════════════════════════════════════════════════
# PLADUO PRO — Combined
# ══════════════════════════════════════════════════════════════════

def pladuo(styles, cw):
    s = []

    # ── PRE-TREATMENT ──────────────────────────────────────────────
    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "PlaDuo Pro uses patented SpinShot Technology to deliver both nitrogen plasma and argon plasma. "
        "These simple steps maximise efficacy and keep your skin safe.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "Your provider will apply <b>AMP D|TOX Pre-Treatment Skincare Serum</b>"
        + alt("or a gentle fragrance-free pre-treatment prep serum")
        + " at the start of your appointment — no action required from you.",
        "Discontinue <b>retinoids and AHA/BHA exfoliants</b> 3–5 days before your appointment.",
        "Arrive with <b>clean, makeup-free skin</b> — no serums, oils, or moisturisers on the treatment area.",
        "Avoid using any harsh or active skincare the day before treatment.",
    ], styles)

    s += section("Sun & Lifestyle", [
        "Avoid <b>direct sun exposure and tanning beds</b> for 2 weeks prior.",
        "Do not use <b>self-tanner</b> for 2 weeks prior.",
        "If you have a history of <b>cold sores (HSV)</b>, inform your provider — antiviral prophylaxis may be prescribed.",
        "Avoid <b>isotretinoin (Accutane)</b> within 6 months of treatment.",
    ], styles)

    s += section("Acne & Rosacea Patients — Additional Notes", [
        "If treated with <b>PlaDuo Pro Argon</b> for active acne: initial sessions may be weekly to achieve "
        "clearance before spacing out.",
        "A temporary <b>purging period</b> is normal after Argon plasma for acne — this is a sign the treatment is working.",
        "Continue any prescribed oral or topical acne medications unless your physician advises otherwise.",
        "For rosacea: avoid spicy foods, alcohol, and temperature extremes in the 48 hours before treatment.",
    ], styles)

    s += section("Day of Treatment", [
        "Arrive with completely clean skin — no SPF, makeup, or skincare products.",
        "Topical anaesthetic is not routinely required; inform your provider if you have low pain tolerance.",
        "Treatment sessions are typically 30–45 minutes.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    # ── POST-TREATMENT ─────────────────────────────────────────────
    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "PlaDuo Pro treatments are low-downtime, but your skin benefits from careful post-care "
        "to maximise results and protect the treated barrier.",
        styles["body"]
    ))

    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle, fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>EXO|E Skin Revitalizing Complex</b>"
            + alt("or your own exosome or growth factor serum")
            + " (AMP) — applied immediately post-procedure in-clinic.",
            "<b>RE|PAIR Post-Treatment Skincare Serum</b>"
            + alt("or your own fragrance-free barrier repair serum")
            + " (AMP) — applied to maintain hydration and minimise redness.",
            "Mild redness and warmth are normal for 24–48 hours, particularly after Argon mode.",
        ]),
        ("Days 1–2", [
            "Cleanse gently with <b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + ".",
            "Apply <b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free occlusive barrier mask")
            + " as a soothing layer.",
            "Follow with <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " 2× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — do not skip.",
            "No retinoids, AHAs, BHAs, or vitamin C.",
        ]),
        ("Days 3–5", [
            "Continue <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free barrier moisturiser")
            + " for ongoing barrier support.",
            "Most patients experience minimal visible downtime by Day 2–3.",
            "Continue SPF diligently — plasma treatments increase photosensitivity.",
        ]),
        ("Day 5+", [
            "Reintroduce your concern-specific skincare gradually.",
            "For acne: resume <b>Noon Lacto-S Oil Control</b>"
            + alt("or your own oil-control treatment serum")
            + " + <b>Noon S-Peel</b>"
            + alt("or your own gentle enzyme exfoliant")
            + " as tolerated.",
            "For rosacea: resume <b>Noon HydroCalming + Vit Complex</b>"
            + alt("or your own calming antioxidant serum")
            + " + <b>Noon MicroSoft Cleanser</b>"
            + alt("or your own gentle fragrance-free cleanser")
            + ".",
            "Return to your full skincare protocol by Week 2.",
        ]),
    ])

    s += section("General Rules", [
        "No makeup for <b>24 hours</b> post-treatment.",
        "Avoid heat — saunas, steam, hot yoga — for <b>48 hours</b>.",
        "No swimming in chlorinated water for <b>3 days</b>.",
        "Avoid vigorous exercise for <b>24–48 hours</b>.",
        "<b>Acne patients:</b> purging is expected — call us if cysts become painful or widespread.",
        "Contact us immediately for blistering, significant swelling, or signs of infection.",
    ], styles)

    s += section("Session Frequency", [
        "<b>Acne — Argon mode:</b> weekly for the first 4 weeks, then monthly maintenance.",
        "<b>Rosacea / skin quality:</b> every 4 weeks for 4–6 sessions.",
        "<b>Biologics add-on:</b> <b>EXO|E Skin Revitalizing Complex</b>"
        + alt("or your own exosome or growth factor serum")
        + " or <b>Avari Purasomes</b>"
        + alt("or your own premium exosome serum")
        + " applied at each session for enhanced regeneration.",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your next session will be scheduled per your treatment protocol. "
        "Reach us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))

    return s


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))

    print("Generating Treasury Aesthetics care PDFs…")

    build_pdf(
        os.path.join(out, "NouvaDerm_Care_Instructions.pdf"),
        "NouvaDerm",
        "1927nm Thulium Fractional Laser  ·  Pre & Post-Treatment Care",
        nouvaderm,
    )
    build_pdf(
        os.path.join(out, "PlaDuo_Pro_Care_Instructions.pdf"),
        "PlaDuo Pro",
        "Dual Plasma (Nitrogen + Argon)  ·  Pre & Post-Treatment Care",
        pladuo,
    )

    print("Done — 2 PDFs created.")
