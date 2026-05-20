"""
Generate combined pre & post care PDFs for all Treasury Aesthetics modalities.
Run: python3 generate_care_pdfs.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.flowables import Flowable
from reportlab.lib.enums import TA_CENTER


# ── Brand colours ──────────────────────────────────────────────────
CHARCOAL  = colors.HexColor("#0C0C0C")
CHARCOAL2 = colors.HexColor("#1A1A1A")
CHARCOAL3 = colors.HexColor("#222222")
GOLD      = colors.HexColor("#C4954A")
TEXT_MUTED = colors.HexColor("#7A7060")
WHITE     = colors.white


def alt(text):
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
        "day_label": ParagraphStyle(
            "day_label", fontName="Helvetica-Bold", fontSize=9,
            textColor=CHARCOAL, leading=14, spaceAfter=4, spaceBefore=10,
        ),
        "note": ParagraphStyle(
            "note", fontName="Helvetica-Oblique", fontSize=8,
            textColor=TEXT_MUTED, leading=13, spaceAfter=4,
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
    if title:
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


# ── Page callback factory ──────────────────────────────────────────
def make_page_callback(device_name, device_sub):
    counter = [1]

    def on_page(canvas_obj, doc):
        w, h = letter
        margin = 0.65 * inch
        header_h = 1.5 * inch

        canvas_obj.saveState()
        canvas_obj.setFillColor(CHARCOAL2)
        canvas_obj.rect(0, h - header_h, w, header_h, fill=1, stroke=0)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, h - 3, w, 3, fill=1, stroke=0)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(w / 2, h - 0.38 * inch,
                                     "TREASURY AESTHETICS  ·  TORONTO, ONTARIO")
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica-Bold", 20)
        canvas_obj.drawString(margin, h - 0.82 * inch, device_name)
        canvas_obj.setFillColor(TEXT_MUTED)
        canvas_obj.setFont("Helvetica", 8.5)
        canvas_obj.drawString(margin, h - 1.02 * inch, device_sub)
        badge = "PRE & POST-TREATMENT CARE"
        bw = canvas_obj.stringWidth(badge, "Helvetica-Bold", 7) + 16
        bx = w - margin - bw
        by = h - 1.08 * inch
        canvas_obj.setFillColor(GOLD)
        canvas_obj.roundRect(bx, by, bw, 18, 3, fill=1, stroke=0)
        canvas_obj.setFillColor(CHARCOAL)
        canvas_obj.setFont("Helvetica-Bold", 7)
        canvas_obj.drawCentredString(bx + bw / 2, by + 5.5, badge)
        canvas_obj.setFillColor(GOLD)
        canvas_obj.rect(0, h - header_h, w, 1.5, fill=1, stroke=0)
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
        filename, pagesize=letter,
        leftMargin=margin, rightMargin=margin,
        topMargin=1.65 * inch, bottomMargin=0.6 * inch,
    )
    col_width = letter[0] - 2 * margin
    styles = make_styles()
    story = content_fn(styles, col_width)
    cb = make_page_callback(device_name, device_sub)
    doc.build(story, onFirstPage=cb, onLaterPages=cb)
    print(f"  Created: {filename}")


# ══════════════════════════════════════════════════════════════════
# VIRTUERF
# ══════════════════════════════════════════════════════════════════
def virtuerf(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "VirtueRF delivers radiofrequency energy through microneedles to remodel collagen and tighten "
        "skin on the face, neck, and body. Proper preparation protects the skin barrier and maximises results.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "The <b>Noon Pre-Procedure Program (Gear Up Kit)</b>"
        + alt("or your own gentle fragrance-free prep routine")
        + " is <i>recommended</i> 10–14 days prior — not required, but optimises outcomes.",
        "Discontinue <b>retinoids</b> (tretinoin, retinol), <b>AHAs, BHAs, and vitamin C</b> 5–7 days before treatment.",
        "Do not use any <b>self-tanner or sunless bronzer</b> for 2 weeks prior.",
        "<b>Arrive with clean, makeup-free skin</b> — no creams, serums, SPF, or any product on the face.",
    ], styles)

    s += section("Sun & Lifestyle", [
        "Avoid <b>direct sun exposure and tanning beds</b> for 2 weeks prior.",
        "If you have a history of <b>cold sores (HSV)</b>, antiviral medication will be prescribed — begin as directed.",
        "Avoid <b>Accutane (isotretinoin)</b> within 6 months of treatment.",
        "Avoid <b>blood thinners and supplements</b> (fish oil, vitamin E, aspirin unless prescribed) 5–7 days prior.",
    ], styles)

    s += section("Day of Treatment", [
        "Arrive 30–45 minutes early — <b>topical anaesthetic (EMLA)</b> is applied in-clinic and requires time to work.",
        "Avoid caffeine if you are sensitive.",
        "Wear comfortable, loose clothing. Avoid tight collars if treating the neck.",
        "Arrange transport if you are sensitive to anaesthetic or anticipate significant redness.",
    ], styles)

    s += section("Medical History — Please Inform Us If You Have:", [
        "Active skin infection, open sores, or rash in the treatment area.",
        "History of keloid or hypertrophic scarring.",
        "Pregnancy or breastfeeding.",
        "Pacemaker or implanted electronic devices (contraindicated).",
        "Recent laser or RF treatment — minimum 6-week gap required.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your skin has been micro-channelled and needs barrier-first recovery. "
        "No actives until the skin is fully healed.",
        styles["body"]
    ))

    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free occlusive barrier mask")
            + " — zone-matched (face, neck, or eyes) — applied in-clinic.",
            "<b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " applied before leaving the clinic.",
            "<b>Epicutis Hydrobiome Mist</b>"
            + alt("or your own fragrance-free hydrating mist")
            + " for cooling and comfort as needed.",
        ]),
        ("Days 1–3", [
            "Barrier protection and soothing <b>ONLY</b> — no actives of any kind.",
            "Cleanse gently with <b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser") + ".",
            "Apply <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " 2× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — reapply every 2 hours if outdoors.",
            "Continue <b>Epicutis Hydrobiome Mist</b>"
            + alt("or your own fragrance-free mist")
            + " as needed for comfort.",
        ]),
        ("Days 3–5", [
            "Continue Epicutis system; may add <b>Noon Igloo Moist</b>"
            + alt("or your own lightweight fragrance-free hydrating cream")
            + " for added hydration.",
            "Continue gentle cleansing and SPF daily.",
        ]),
        ("Day 5+", [
            "Gradual reintroduction of Noon actives — start gentle: <b>Halo-Ronic Serum</b>"
            + alt("or your own hyaluronic acid serum")
            + ", <b>HydroCalming + Vit Complex</b>"
            + alt("or your own calming antioxidant serum") + ".",
            "The <b>Noon Accelerate Kit</b>"
            + alt("or your own concern-appropriate active skincare")
            + " is <i>recommended</i> post-treatment to support results.",
        ]),
        ("Week 2+", [
            "Return to your full Noon protocol appropriate to your skin concern.",
            "Next VirtueRF session: <b>4–6 weeks</b> after this treatment — never sooner.",
            "Minimum <b>6 weeks</b> between VirtueRF and any laser treatment.",
        ]),
    ])

    s += section("General Rules", [
        "No makeup for <b>24–48 hours</b>.",
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
        "VirtueRF sessions are spaced <b>4–6 weeks</b> apart. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))
    return s


# ══════════════════════════════════════════════════════════════════
# NOUVADERM
# ══════════════════════════════════════════════════════════════════
def nouvaderm(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Please follow these instructions carefully before your NouvaDerm treatment to ensure "
        "the best possible results and minimise any risk of adverse reactions.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "The <b>Noon Pre-Procedure Program (Gear Up Kit)</b>"
        + alt("or your own gentle fragrance-free prep routine")
        + " is <i>recommended</i> 10–14 days prior — not required, but optimises results.",
        "The <b>AMP D|TOX Pre-Treatment Skincare Serum</b>"
        + alt("or your own gentle pre-treatment prep serum")
        + " <i>may also be recommended</i> by your provider — optional.",
        "Discontinue <b>retinoids</b> (tretinoin, retinol) and <b>AHA/BHA exfoliants</b> 7 days before treatment.",
        "Discontinue <b>vitamin C serums</b> 3–5 days before treatment.",
        "Do not use any <b>self-tanner or sunless bronzer</b> for 2 weeks prior.",
        "<b>Arrive with clean, makeup-free skin</b> — no creams, serums, SPF, or any product on the face.",
    ], styles)

    s += section("Sun & Lifestyle", [
        "Avoid direct <b>sun exposure and tanning beds</b> for 2–4 weeks prior "
        "(2 weeks minimum for NOUVAGlo; strict for Ablative).",
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

    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your skin is in an active healing phase. Following these instructions precisely protects "
        "your investment and significantly improves your final result.",
        styles["body"]
    ))

    s.append(Paragraph("NOUVAGlo (Non-Ablative Mode)", styles["section_label"]))
    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
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
            + alt("or your own gentle fragrance-free cleanser")
            + " or <b>Noon MicroSoft Cleanser</b>"
            + alt("or any gentle sulfate-free cleanser") + " — gentle pressure only.",
            "Apply <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " 2–4× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — reapply every 2 hours if outdoors.",
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
        ]),
        ("Day 5+", [
            "Reintroduce Noon concern-specific products: start gentle — "
            "<b>Halo-Ronic Serum</b>" + alt("or your own hyaluronic acid serum")
            + ", <b>HydroCalming + Vit Complex</b>" + alt("or your own calming antioxidant serum") + ".",
            "Return to your full skincare protocol by Week 2.",
        ]),
    ])

    s.append(Spacer(1, 6))
    s.append(GoldBar(cw, thickness=0.8))
    s.append(Spacer(1, 10))

    s.append(Paragraph("Ablative Mode", styles["section_label"]))
    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
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
            "Hale Derma Cleanser" + alt("or gentle non-foaming cleanser")
            + " → <b>Epicutis Lipid Serum</b>" + alt("or fragrance-free hydrating serum")
            + " → <b>HYVIA Crème</b>" + alt("or fragrance-free barrier moisturiser")
            + " → <b>Epicutis Lipid Recovery Mask</b>" + alt("or occlusive barrier mask") + ".",
            "Keep skin continuously moisturised — do not allow treated areas to dry out.",
            "Do <b>not</b> pick, peel, or rub any flaking — allow natural shedding.",
            "Social downtime of <b>5–10 days</b> is typical — plan accordingly.",
        ]),
        ("Week 2+", [
            "Begin <b>SPF 50+</b> as soon as re-epithelialization is complete.",
            "No retinoids, AHAs, BHAs, or vitamin C until your physician clears them.",
            "<b>Strict sun avoidance</b> for a minimum of 2 weeks.",
            "Follow-up <b>OBSERV 360 skin analysis</b> at 4–6 weeks post-treatment.",
        ]),
    ])

    s += section("General Rules — Both Modes", [
        "No makeup for <b>24–48 hours</b> (longer for Ablative).",
        "Avoid heat — saunas, hot yoga, steam rooms — for <b>72 hours</b>.",
        "No swimming in chlorinated water for <b>5 days</b>.",
        "Sleep on a clean pillowcase; elevated head position for the first 2 nights.",
        "Avoid vigorous exercise for <b>48 hours</b>.",
        "Call us immediately if you develop blistering, significant swelling, or signs of infection.",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "NOUVAGlo sessions: <b>4 weeks apart</b>. Ablative timing as directed by your physician. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))
    return s


# ══════════════════════════════════════════════════════════════════
# PLADUO PRO
# ══════════════════════════════════════════════════════════════════
def pladuo(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "PlaDuo Pro uses patented SpinShot Technology to deliver both nitrogen plasma and argon plasma. "
        "These simple steps maximise efficacy and keep your skin safe.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "The <b>AMP D|TOX Pre-Treatment Skincare Serum</b>"
        + alt("or a gentle fragrance-free pre-treatment prep serum")
        + " <i>may be recommended</i> by your provider before your appointment — not required but beneficial.",
        "Discontinue <b>retinoids and AHA/BHA exfoliants</b> 3–5 days before your appointment.",
        "<b>Arrive with clean, makeup-free skin</b> — no serums, oils, moisturisers, SPF, or any product on the face.",
        "Avoid any harsh or active skincare the day before treatment.",
    ], styles)

    s += section("Important — Hair on the Treatment Area", [
        "It is <i>recommended</i> that <b>vellus hair (peach fuzz) be removed</b> from the treatment area "
        "before plasma is applied. Plasma energy can singe fine facial hair, which may cause uneven "
        "treatment and unwanted odour.",
        "Your provider will assess this at your appointment and can arrange gentle dermaplaning or shave "
        "prep in-clinic if needed.",
        "Do <b>not</b> wax, thread, or use depilatory creams on the treatment area within 5 days prior.",
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
        "<b>Arrive with clean, makeup-free skin</b> — no SPF, serums, oils, or any product on the face.",
        "Topical anaesthetic is not routinely required; inform your provider if you have low pain tolerance.",
        "Treatment sessions are typically 30–45 minutes.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

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
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>EXO|E Skin Revitalizing Complex</b>"
            + alt("or your own exosome or growth factor serum")
            + " applied immediately post-procedure in-clinic.",
            "<b>RE|PAIR Post-Treatment Skincare Serum</b>"
            + alt("or your own fragrance-free barrier repair serum")
            + " applied to maintain hydration and minimise redness.",
            "Mild redness and warmth are normal for 24–48 hours, particularly after Argon mode.",
        ]),
        ("Days 1–2", [
            "Cleanse gently with <b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser") + ".",
            "Apply <b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free occlusive barrier mask") + " as a soothing layer.",
            "Follow with <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser") + " 2× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — do not skip.",
            "No retinoids, AHAs, BHAs, or vitamin C.",
        ]),
        ("Days 3–5", [
            "Continue <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free barrier moisturiser") + " for ongoing barrier support.",
            "Most patients experience minimal visible downtime by Day 2–3.",
            "Continue SPF diligently — plasma treatments increase photosensitivity.",
        ]),
        ("Day 5+", [
            "For acne: resume <b>Noon Lacto-S Oil Control</b>"
            + alt("or your own oil-control treatment serum")
            + " + <b>Noon S-Peel</b>" + alt("or your own gentle enzyme exfoliant") + " as tolerated.",
            "For rosacea: resume <b>Noon HydroCalming + Vit Complex</b>"
            + alt("or your own calming antioxidant serum")
            + " + <b>Noon MicroSoft Cleanser</b>" + alt("or your own gentle fragrance-free cleanser") + ".",
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
        + " or <b>Avari Purasomes</b>" + alt("or your own premium exosome serum")
        + " applied at each session for enhanced regeneration.",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Your next session will be scheduled per your treatment protocol. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))
    return s


# ══════════════════════════════════════════════════════════════════
# QUANTA ULTRALIGHT
# ══════════════════════════════════════════════════════════════════
def quanta(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Quanta UltraLight combines KTP, Nd:YAG, IPL, Plasma Frax, and Carbon Facial (NATURA PEEL) "
        "modalities. Instructions apply to all modes unless otherwise noted.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "Discontinue <b>retinoids</b> (tretinoin, retinol) 5–7 days before treatment.",
        "Discontinue <b>AHA/BHA exfoliants</b> 5–7 days before treatment.",
        "Do not use any <b>self-tanner or bleaching creams</b> for 2 weeks prior.",
        "<b>Arrive with clean, makeup-free skin</b> — no creams, serums, SPF, or any product on the face.",
        "For <b>KTP / IPL:</b> avoid waxing or depilatory creams on the treatment area for 1 week prior.",
    ], styles)

    s += section("Important — Hair on the Treatment Area (Plasma Frax)", [
        "For <b>Plasma Frax mode</b>: it is <i>recommended</i> that vellus hair (peach fuzz) be removed "
        "from the treatment area beforehand. Your provider will assess and can arrange prep in-clinic.",
        "Do <b>not</b> wax, thread, or use depilatory creams on the area within 5 days prior.",
    ], styles)

    s += section("Sun & Lifestyle", [
        "Avoid <b>direct sun exposure and tanning beds</b> for 2–4 weeks prior.",
        "Darker skin tones (Fitzpatrick IV–VI): your physician will use <b>Noon DermShield-validated settings</b> "
        "appropriate for your skin type — please disclose your Fitzpatrick type.",
        "If you have a history of <b>cold sores (HSV)</b> and are having Plasma Frax: "
        "antiviral prophylaxis will be prescribed.",
        "Avoid <b>isotretinoin (Accutane)</b> within 6 months of treatment.",
    ], styles)

    s += section("Day of Treatment", [
        "<b>Arrive with clean, makeup-free skin</b> — no SPF, serums, oils, or any product on the face.",
        "Topical anaesthetic may be applied in-clinic for Plasma Frax — arrive 30–45 minutes early if advised.",
        "For <b>Carbon Facial (NATURA PEEL)</b>: a carbon lotion will be applied in-clinic — no prep needed.",
        "Protective goggles are worn by both patient and provider throughout the session.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))

    s.append(Paragraph("KTP / IPL / Nd:YAG Modes", styles["section_label"]))
    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " applied before leaving the clinic.",
            "<b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free barrier mask")
            + " if significant redness or heat is present.",
        ]),
        ("Days 1–3", [
            "Apply <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser") + " 2× daily.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning — reapply if outdoors.",
            "Avoid heat and friction for <b>48–72 hours</b>.",
            "Do not pick or peel — especially after Nd:YAG / NATURA PEEL Carbon Facial.",
            "<b>Pigmentation may appear darker</b> before it lifts — this is expected and normal.",
        ]),
        ("Day 3+", [
            "Reintroduce <b>Noon concern-specific serums</b>"
            + alt("or your own concern-appropriate actives") + " gradually.",
            "Continue SPF daily — non-negotiable for pigmentation patients.",
        ]),
    ])

    s.append(Spacer(1, 6))
    s.append(GoldBar(cw, thickness=0.8))
    s.append(Spacer(1, 10))

    s.append(Paragraph("Plasma Frax / Eyelid Mode", styles["section_label"]))
    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free occlusive barrier mask")
            + " applied in-clinic.",
            "<b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and thick barrier cream")
            + " applied before leaving.",
        ]),
        ("Days 1–7", [
            "Apply <b>Epicutis full recovery protocol</b> up to 4× daily: "
            "Hale Derma Cleanser" + alt("or gentle non-foaming cleanser")
            + " → <b>Epicutis Lipid Serum</b>" + alt("or fragrance-free hydrating serum")
            + " → <b>HYVIA Crème</b>" + alt("or fragrance-free barrier moisturiser")
            + " → <b>Epicutis Lipid Recovery Mask</b>" + alt("or occlusive barrier mask") + ".",
            "<b>Crusting and grid marks</b> are expected for 5–7 days — do not pick.",
            "Longer avoidance of actives than standard laser — follow physician guidance.",
            "SPF as soon as re-epithelialization is complete.",
        ]),
    ])

    s += section("General Rules — All Modes", [
        "No makeup for <b>24–48 hours</b> (longer for Plasma Frax).",
        "Avoid heat — saunas, hot yoga, steam — for <b>48–72 hours</b>.",
        "No swimming for <b>3–5 days</b> depending on mode.",
        "Avoid vigorous exercise for <b>48 hours</b>.",
        "Call us immediately if you develop blistering, significant swelling, or signs of infection.",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Session spacing varies by mode — your provider will advise. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))
    return s


# ══════════════════════════════════════════════════════════════════
# OXYGENEO
# ══════════════════════════════════════════════════════════════════
def oxygeneo(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "OxyGeneo is a no-downtime 3-in-1 super facial combining OxyPod effervescence, "
        "ultrasound infusion, and optional TriPollar RF. Suitable for all skin types with minimal preparation.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "No special preparation required for most patients — this is the most accessible treatment in our stack.",
        "If you have <b>sensitive skin</b>: discontinue retinoids and AHA/BHA products 2–3 days prior.",
        "<b>Arrive with clean, makeup-free skin</b> — no creams, serums, SPF, or any product on the face.",
    ], styles)

    s += section("Day of Treatment", [
        "No topical anaesthetic required — OxyGeneo is comfortable for all patients.",
        "Sessions are typically 45–60 minutes.",
        "Safe to combine with LED TriWave on the same day (LED applied after OxyGeneo).",
    ], styles)

    s += section("Who Is This Ideal For?", [
        "First-time patients and those new to medical aesthetics.",
        "Prejuvenation (under 35) — glow, hydration, and skin quality maintenance.",
        "Patients looking for a no-downtime option between energy device sessions.",
        "All Fitzpatrick types including IV–VI.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "OxyGeneo requires minimal aftercare. Your skin may appear slightly flushed for 1–2 hours — "
        "this is normal and resolves quickly.",
        styles["body"]
    ))

    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>Noon Halo-Ronic Serum</b>"
            + alt("or your own hyaluronic acid serum")
            + " applied to lock in hydration and amplify OxyGeneo benefits.",
            "Follow with your <b>Noon concern-appropriate moisturiser</b>"
            + alt("or your own fragrance-free moisturiser") + ".",
            "<b>Broad-spectrum SPF 50+</b> applied before leaving the clinic if going outdoors.",
        ]),
        ("Same Day / Evening", [
            "You may resume your <b>full skincare routine the same evening</b>.",
            "Skin is primed for enhanced absorption — ideal time to apply Noon concern serums.",
            "Slight pinkness resolves within 1–2 hours.",
        ]),
        ("Ongoing", [
            "No activity restrictions — OxyGeneo has zero downtime.",
            "The <b>Noon Accelerate Kit</b>"
            + alt("or your own concern-appropriate active skincare")
            + " is recommended at checkout after each visit to extend results.",
            "For best results, space sessions <b>3–4 weeks apart</b>.",
        ]),
    ])

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "OxyGeneo sessions are spaced <b>3–4 weeks apart</b> and can be combined with most other treatments. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))
    return s


# ══════════════════════════════════════════════════════════════════
# LED TRIWAVE
# ══════════════════════════════════════════════════════════════════
def led_triwave(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "LED TriWave phototherapy is a gentle, no-downtime treatment using red, near-infrared, "
        "and blue wavelengths to stimulate collagen, reduce inflammation, and target acne. "
        "It requires virtually no preparation.",
        styles["body"]
    ))

    s += section("Preparation", [
        "No special preparation required.",
        "<b>Arrive with clean, makeup-free skin</b> — no creams, serums, or SPF on the face.",
        "Safe immediately before or after most other treatments — your provider will sequence it appropriately.",
        "No contraindications with other treatments in the same appointment.",
    ], styles)

    s += section("Wavelength Guide", [
        "<b>Red (630nm):</b> Collagen stimulation, anti-aging, wound healing acceleration.",
        "<b>Near-Infrared (830nm):</b> Deep tissue healing, inflammation reduction, post-procedure recovery.",
        "<b>Blue (415nm):</b> Active acne, antibacterial (targets P. acnes bacteria).",
    ], styles)

    s += section("Optimise Your Session — Optional Pre-LED Primer", [
        "Applying <b>Epicutis Lipid Serum</b>"
        + alt("or your own antioxidant serum")
        + " <i>before</i> your LED session is recommended. The Glucosylrutin flavonoid in Epicutis "
        "has direct mechanistic relevance for photobiomodulation — it enhances the LED's effect.",
        "<b>Noon Halo-Ronic Serum</b>"
        + alt("or your own hyaluronic acid serum")
        + " is an alternative pre-LED primer for hydration amplification.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "LED TriWave has no downtime. Your skin is primed for maximum product absorption immediately after treatment.",
        styles["body"]
    ))

    s += section("", [], styles, day_groups=[
        ("Immediately After Treatment", [
            "Apply your <b>Noon concern-specific serum</b>"
            + alt("or your own concern-appropriate active serum")
            + " — skin absorption is significantly enhanced post-LED.",
            "Follow with your <b>Noon moisturiser</b>"
            + alt("or your own fragrance-free moisturiser") + ".",
            "Apply <b>broad-spectrum SPF 50+</b> if going outdoors.",
            "You may resume your full skincare routine immediately.",
        ]),
        ("Ongoing", [
            "No restrictions on activity, makeup, or skincare.",
            "For <b>acne patients</b>: LED TriWave sessions may be weekly — consistent frequency drives results.",
            "For <b>post-procedure recovery</b>: LED is often combined same-day with energy device treatments "
            "(VirtueRF, NouvaDerm, PlaDuo Pro) — near-infrared accelerates healing.",
            "For <b>rosacea</b>: red and near-infrared wavelengths used; avoid blue wavelength.",
        ]),
    ])

    s += section("Membership Note", [
        "1 complimentary LED session per month is included in the <b>Treasury Reserve</b> membership tier.",
        "Dedicated LED memberships are available for acne, rosacea, and chronic skin conditions "
        "($550/month for up to 4 sessions/month).",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "LED TriWave is safe, gentle, and compatible with all skin types and Fitzpatrick tones. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
        styles["note"]
    ))
    return s


# ══════════════════════════════════════════════════════════════════
# DERMATWIST (CIT)
# ══════════════════════════════════════════════════════════════════
def dermatwist(styles, cw):
    s = []

    s.append(PhaseDivider(cw, "Pre-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "DermaTwist delivers Collagen Induction Therapy (CIT) through mechanical microneedling. "
        "It is used for acne scarring, fine lines, texture, stretch marks, and scalp/hair restoration.",
        styles["body"]
    ))

    s += section("Skincare Preparation", [
        "The <b>Noon Pre-Procedure Program</b>"
        + alt("or your own gentle fragrance-free prep routine")
        + " is <i>recommended</i> 10–14 days prior — not required but optimises outcomes.",
        "Discontinue <b>retinoids and AHA/BHA exfoliants</b> 5–7 days before treatment.",
        "Do not use any <b>self-tanner</b> for 2 weeks prior.",
        "<b>Arrive with clean, makeup-free skin</b> — no creams, serums, SPF, or any product on the treatment area.",
    ], styles)

    s += section("Sun & Lifestyle", [
        "Avoid <b>direct sun exposure and tanning beds</b> for 2 weeks prior.",
        "Avoid <b>isotretinoin (Accutane)</b> within 6 months of treatment.",
        "No active skin infections or open breakouts on the treatment area.",
        "Avoid <b>blood thinners and supplements</b> (fish oil, vitamin E, aspirin unless prescribed) 5–7 days prior.",
    ], styles)

    s += section("Day of Treatment", [
        "Arrive 30–45 minutes early — <b>topical anaesthetic</b> is applied in-clinic and requires time to work.",
        "<b>Arrive with clean, makeup-free skin</b> — no product on the face or scalp.",
        "For scalp treatments: arrive with clean, dry hair — no oils or styling products.",
    ], styles)

    s += section("Medical History — Please Inform Us If You Have:", [
        "Active skin infection, open sores, or rash in the treatment area.",
        "History of keloid or hypertrophic scarring.",
        "Pregnancy or breastfeeding.",
        "Blood clotting disorders or anticoagulant medications.",
    ], styles)

    s.append(Spacer(1, 14))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 18))

    s.append(PhaseDivider(cw, "Post-Treatment Instructions"))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "Micro-channels remain open for several hours post-treatment — skin is highly receptive to "
        "applied biologics and serums during this window.",
        styles["body"]
    ))

    s += section("", [], styles, day_groups=[
        ("Day 0 — Immediately After Treatment", [
            "<b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser")
            + " — used in-clinic at end of treatment.",
            "<b>EXO|E Skin Revitalizing Complex</b>"
            + alt("or your own exosome or growth factor serum")
            + " applied into micro-channels immediately post-treatment for maximum absorption.",
            "<b>Epicutis Lipid Recovery Mask</b>"
            + alt("or your own fragrance-free occlusive barrier mask")
            + " — zone-appropriate (face or neck) — applied in-clinic.",
            "<b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser")
            + " applied before leaving the clinic.",
            "<b>Epicutis Hydrobiome Mist</b>"
            + alt("or your own fragrance-free hydrating mist")
            + " for cooling and microbiome support.",
        ]),
        ("Days 1–2", [
            "Cleanse gently with <b>Hale Derma Cleanser</b>"
            + alt("or your own gentle fragrance-free non-foaming cleanser") + ".",
            "Apply <b>Epicutis Lipid Serum + HYVIA Crème</b>"
            + alt("or your own fragrance-free hydrating serum and barrier moisturiser") + " 2× daily.",
            "Continue <b>Epicutis Hydrobiome Mist</b>"
            + alt("or your own fragrance-free mist") + " for comfort.",
            "Apply <b>broad-spectrum SPF 50+</b> every morning.",
            "No makeup for <b>24–48 hours</b>.",
            "No retinoids, AHAs, BHAs, or vitamin C.",
        ]),
        ("Days 2–5", [
            "May reintroduce gentle Noon products: <b>Noon Igloo Moist</b>"
            + alt("or your own lightweight fragrance-free hydrating cream")
            + ", <b>Halo-Ronic Serum</b>" + alt("or your own hyaluronic acid serum") + ".",
            "Continue SPF daily.",
        ]),
        ("Week 2+", [
            "Return to your full Noon concern-appropriate protocol.",
            "Next DermaTwist session: <b>4 weeks</b> after this treatment.",
        ]),
    ])

    s.append(Paragraph("For Scalp / Hair Restoration (DermaTwist Scalp)", styles["section_label"]))
    s += section("", [
        "<b>DE|RIVE Scalp Treatment</b>"
        + alt("or your own scalp exosome or growth factor serum")
        + " applied post-needling into the scalp — maximum absorption window.",
        "<b>KeraFactor Growth Factor Serum</b>"
        + alt("or your own growth factor hair serum")
        + " applied and massaged in.",
        "<b>Avari Purasomes</b>"
        + alt("or your own premium exosome serum")
        + " as a premium upgrade for enhanced hair follicle stimulation.",
        "Avoid washing the scalp for <b>24 hours</b> after treatment.",
        "No heat styling for <b>48 hours</b>.",
        "No chemical treatments (colour, relaxers) for <b>2 weeks</b>.",
    ], styles)

    s += section("General Rules", [
        "Avoid heat — saunas, hot yoga, steam — for <b>48–72 hours</b>.",
        "No swimming in chlorinated water for <b>5 days</b>.",
        "Sleep on a clean pillowcase for the first 3 nights.",
        "Avoid vigorous exercise for <b>24–48 hours</b>.",
        "Call us immediately if you develop significant swelling, unusual crusting, or signs of infection.",
    ], styles)

    s.append(Spacer(1, 12))
    s.append(GoldBar(cw))
    s.append(Spacer(1, 8))
    s.append(Paragraph(
        "DermaTwist sessions are spaced <b>4 weeks apart</b>. "
        "Contact us anytime at <b>aesthetics@treasuryhealth.ca</b>",
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

    docs = [
        ("VirtueRF_Care_Instructions.pdf",
         "VirtueRF", "RF Microneedling (SmartRF · DeepRF · ExactRF)  ·  Pre & Post-Treatment Care",
         virtuerf),
        ("NouvaDerm_Care_Instructions.pdf",
         "NouvaDerm", "1927nm Thulium Fractional Laser  ·  Pre & Post-Treatment Care",
         nouvaderm),
        ("PlaDuo_Pro_Care_Instructions.pdf",
         "PlaDuo Pro", "Dual Plasma (Nitrogen + Argon)  ·  Pre & Post-Treatment Care",
         pladuo),
        ("Quanta_UltraLight_Care_Instructions.pdf",
         "Quanta UltraLight", "Multi-Platform Laser (KTP · Nd:YAG · IPL · Plasma Frax · Carbon)  ·  Pre & Post-Treatment Care",
         quanta),
        ("OxyGeneo_Care_Instructions.pdf",
         "OxyGeneo", "3-in-1 Super Facial  ·  Pre & Post-Treatment Care",
         oxygeneo),
        ("LED_TriWave_Care_Instructions.pdf",
         "LED TriWave", "Photobiomodulation Therapy  ·  Pre & Post-Treatment Care",
         led_triwave),
        ("DermaTwist_Care_Instructions.pdf",
         "DermaTwist", "Collagen Induction Therapy (CIT)  ·  Pre & Post-Treatment Care",
         dermatwist),
    ]

    for filename, device_name, device_sub, fn in docs:
        build_pdf(os.path.join(out, filename), device_name, device_sub, fn)

    print(f"Done — {len(docs)} PDFs created.")
