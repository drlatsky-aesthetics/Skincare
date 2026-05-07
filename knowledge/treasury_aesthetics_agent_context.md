# Treasury Aesthetics — AI Agent Context Document
## Pre & Post Treatment Care + Skincare Recommendation Engine

> **For Claude Code:** This document is the authoritative source of truth for building the Treasury Aesthetics AI consultation agent. Read this entirely before writing any code. The agent's primary jobs are: (1) determine pre- and post-treatment care for any device in our stack, (2) recommend a full curated skincare regimen from our retail brands, and (3) suggest add-ons and biologics where clinically appropriate.

---

## 1. Clinic Identity

| Field | Detail |
|---|---|
| **Clinic Name** | Treasury Aesthetics |
| **Owner/Physician** | Dr. Jason Latsky, MD |
| **Location** | Toronto, Ontario, Canada |
| **Website** | treasuryhealth.ca |
| **Contact** | aesthetics@treasuryhealth.ca |
| **EMR** | Phorest |
| **Positioning** | Physician-led medical aesthetics — clinical precision meets luxury |
| **Visual Identity** | Charcoal (#0C0C0C / #1A1A1A) + Gold (#C4954A / #D4AF37) |
| **Typography** | Playfair Display (headings), DM Sans (body), DM Mono (numbers) |

**Brand metaphor system:** The entire brand runs on a financial/treasury metaphor. Treatments are "investments," memberships are "Reserve" and "Vault" tiers, rooms may be named after vaults or gems. Agent language should reflect warmth and enthusiasm — NOT cold luxury. Think: knowledgeable friend who happens to be a physician.

---

## 2. Device Stack — Complete Inventory

The agent must understand every device and its clinical role deeply. Never confuse handpieces or modes.

---

### 2.1 VirtueRF — RF Microneedling

**Manufacturer:** Cartessa Aesthetics
**Technology:** Radiofrequency energy delivered via microneedles into the dermis
**Primary indications:** Collagen remodeling, skin tightening, texture, acne scarring, pore reduction, periorbital rejuvenation, jawline sculpting

**Three distinct handpieces — each has a unique clinical role:**

| Handpiece | Use Case | Notes |
|---|---|---|
| **SmartRF** | Face and neck — standard RF microneedling | Primary workhorse for facial treatments |
| **DeepRF** | Body — deeper RF delivery with integrated cooling | Used for body areas; cooling prevents surface burns |
| **ExactRF** | Monopolar single-needle — periorbital fat reduction, jawline sculpting | NOT interchangeable with PlaDuo Pro or Plexr for blepharoplasty; treats subsurface RF for lower lid fat herniation |

**Clinical timing rules (CRITICAL for the agent):**
- RF microneedling sessions spaced **4–6 weeks** apart
- Minimum **6 weeks** between RF microneedling and any laser treatment (NouvaDerm, Quanta)
- ExactRF is for lower lid fat herniation (subsurface); Plexr is for upper lid skin excess (surface sublimation) — these are not substitutes for each other

**Pre-Treatment Care (VirtueRF):**
- Begin Noon Pre-Procedure Program 10–14 days prior (Gear Up Kit)
- Discontinue retinoids, AHAs, BHAs, and vitamin C 5–7 days before
- Avoid sun exposure and active tanning 2 weeks prior
- No Accutane within 6 months
- Antiviral prophylaxis (physician to prescribe) if history of cold sores
- Arrive with clean, makeup-free skin
- Topical anesthesia (EMLA or equivalent) applied in-clinic 30–45 minutes before

**Post-Treatment Care (VirtueRF):**
- **Days 1–3:** Barrier protection and soothing ONLY. No actives.
  - Epicutis Lipid Recovery Mask (zone-matched: face, neck, or eyes) — first 24 hours
  - Epicutis Lipid Serum + HYVIA Crème 2× daily
  - Epicutis Hydrobiome Mist as needed for cooling/comfort
  - Broad-spectrum SPF 50+ (Pavise DiamondCore SPF) — reapply every 2 hours if outdoors
- **Days 3–5:** Continue Epicutis system; may add Noon Igloo Moist for added hydration
- **Day 5+:** Gradual reintroduction of Noon actives — start with gentle options (Halo-Ronic Serum, HydroCalming)
- **Week 2+:** Return to full Noon protocol appropriate to skin concern
- Avoid heat (sauna, hot yoga, steam) for 72 hours
- Avoid makeup for 24–48 hours
- No swimming (chlorinated water) for 5 days

**Skincare Integration:** VirtueRF has an exclusive partnership with Noon Aesthetics. The **Noon Gear Up Kit** (pre) and **Noon Accelerate Kit** (post) are the official protocol kits — always recommend these.

---

### 2.2 NouvaDerm — 1927nm Thulium Fractional Laser

**Technology:** 1927nm thulium wavelength, fractionated delivery
**Modes:**
- **NOUVAGlo (non-ablative):** Gentle, no downtime, targets superficial skin quality, pigmentation, texture. Flagship mass-market treatment.
- **Hair Support Mode:** Scalp treatments for hair restoration protocols — combine with exosomes and DermaTwist
- **Ablative Mode:** Full resurfacing; significant downtime; physician-only procedure

**Primary indications:** Skin quality, pigmentation, melasma, fine lines, texture, sun damage, skin tone evening

**Pre-Treatment Care (NouvaDerm — all modes):**
- Noon Pre-Procedure Program 10–14 days prior
- Discontinue retinoids and AHA/BHA 7 days before
- Avoid sun exposure 2–4 weeks prior (strict for ablative)
- Antiviral prophylaxis if history of HSV
- No Accutane within 6 months (ablative: 12 months)
- Topical anesthesia 30–45 minutes prior (NOUVAGlo may not require depending on settings)
- Avoid blood thinners/supplements (fish oil, vitamin E, aspirin unless prescribed) 7 days prior

**Post-Treatment Care — NOUVAGlo (non-ablative):**
- **Immediate/Day 1:** Epicutis Lipid Recovery Mask (face) in-clinic; Epicutis Lipid Serum + HYVIA Crème 2–4× daily
- **Days 1–5:** Gentle cleansing only (Epicutis Oil Cleanser or Noon MicroSoft Cleanser); no exfoliants
- **SPF:** Pavise DiamondCore SPF immediately from Day 1 — non-negotiable
- **Day 5+:** Reintroduce Noon concern-specific products
- Mild redness/warmth/bronzing expected Days 1–3; pinpoint micro-crusting normal

**Post-Treatment Care — Ablative Mode:**
- **Days 1–5 (active healing):** Epicutis full recovery protocol — Oil Cleanser + Lipid Serum + HYVIA Crème + Lipid Recovery Mask; up to 4× daily application
- **Strict sun avoidance** for 2 weeks minimum; Pavise SPF as soon as re-epithelialization complete
- No actives (retinoids, AHA, BHA, vitamin C) until physician clears — typically 2 weeks minimum
- Social downtime: 5–10 days (ablative)
- Follow-up OBSERV skin analysis at 4–6 weeks post-treatment

**Timing Rules:**
- NOUVAGlo can be layered with LED TriWave same day (LED post-laser)
- Minimum 6 weeks between ablative laser and any RF microneedling
- NOUVAGlo series: 3–6 sessions spaced 4 weeks apart

---

### 2.3 Quanta UltraLight — Multi-Platform Laser

**Technology:** Combined KTP (532nm) / Nd:YAG (1064nm) / IPL / Plasma Frax / NATURA PEEL
**Modes and indications:**

| Mode | Wavelength | Primary Use |
|---|---|---|
| **KTP (532nm)** | Green light | Active acne, superficial pigmentation, redness, telangiectasia |
| **Nd:YAG (1064nm)** | Near-infrared | Deep pigmentation, vascular lesions, tattoo removal, skin toning |
| **IPL** | Broadband | General photorejuvenation, pigmentation, redness |
| **Plasma Frax** | Plasma energy | Resurfacing, eyelid tightening |
| **NATURA PEEL (Carbon Facial)** | Laser + carbon | Deep pore cleansing, oil control, skin brightening |

**Pre-Treatment Care (Quanta — all modes):**
- Avoid sun/tanning 2–4 weeks prior
- Discontinue retinoids 5–7 days prior
- No self-tanner for 2 weeks
- For KTP/IPL: avoid recent waxing or bleaching creams on treatment area
- Antiviral prophylaxis for facial Plasma Frax if HSV history
- Fitzpatrick type-appropriate settings — physician to assess; Noon DermShield products validated safe for Fitzpatrick IV–VI

**Post-Treatment Care (Quanta — KTP/IPL/Nd:YAG):**
- **Days 1–3:** Epicutis Lipid Serum + HYVIA Crème; Lipid Recovery Mask if needed
- Pavise DiamondCore SPF from Day 1
- Avoid heat and friction for 48–72 hours
- Avoid picking or peeling (especially post-Nd:YAG carbon peel / NATURA PEEL)
- **Day 3+:** Reintroduce Noon concern-specific serums
- Pigmentation may darken before lifting (expected — counsel patient)

**Post-Treatment Care (Quanta — Plasma Frax / eyelid):**
- Similar to ablative laser protocol above
- Epicutis full recovery system; longer avoidance of actives
- Crusting/grid marks expected for 5–7 days — do not pick

---

### 2.4 PlaDuo Pro — Dual Plasma (Nitrogen + Argon)

**Manufacturer:** AMP (Aesthetic Management Partners)
**Technology:** Patented SpinShot Technology delivering nitrogen plasma AND argon plasma
**Key distinction:** NOT a substitute for ExactRF (subsurface RF) or Plexr (upper lid ablation). Mechanistically different.

**Plasma types and their roles:**

| Plasma Type | Mechanism | Best For |
|---|---|---|
| **Nitrogen plasma** | Thermal tissue remodeling | Texture, tone, elasticity, anti-aging |
| **Argon plasma** | Antibacterial, anti-inflammatory | Active acne, rosacea, sensitive skin |

**Evidence-based utility:**
- **Strongest evidence (60–70% utility):** Active inflammatory acne, rosacea
- **Moderate evidence (20–25% utility):** General anti-aging skin revitalization
- This means: lead with PlaDuo Pro for acne/rosacea; it is NOT a primary anti-aging anchor treatment

**Pre-Treatment Care (PlaDuo Pro):**
- AMP D|TOX Pre-Treatment Skincare Serum recommended by provider before session
- Discontinue active topicals (retinoids, AHA) 3–5 days prior
- Clean, makeup-free skin at appointment
- No isotretinoin within 6 months
- Antiviral if history of HSV

**Post-Treatment Care (PlaDuo Pro):**
- **Day of treatment:** EXO|E Skin Revitalizing Complex (AMP's exosome product) — apply immediately post-procedure
- **RE|PAIR Post-Treatment Skincare Serum** (AMP) — to maintain hydration and minimize social downtime
- **Days 1–5:** Avoid exfoliants, harsh skincare; barrier-first approach
  - Epicutis Lipid Recovery Mask (face or neck as appropriate)
  - Epicutis Lipid Serum + HYVIA Crème
- Broad-spectrum SPF 50+ from Day 1 (Pavise DiamondCore SPF)
- May have mild redness/warmth 24–48 hours (argon mode especially)
- Acne patients: expect purging period before clearance

**Condition Protocol Integration:**
- Acne Protocol: PlaDuo Argon + Quanta KTP + Noon S-Peel + skincare
- Rosacea Protocol: PlaDuo Argon + LED TriWave + skincare (Noon HydroCalming / Epicutis)
- Barrier Repair: PlaDuo Argon + Epicutis Recovery Set

---

### 2.5 OxyGeneo — 3-in-1 Super Facial

**Technology:** OxyPod effervescence + ultrasound infusion + optional TriPollar RF
**Modes:** OxyPod + Ultrasound Infusion; Full Face TriPollar RF; Face + Neck TriPollar RF; Under-Eye Ultrasound
**Positioning:** No downtime, all skin types, suitable for first-time patients and prejuvenation demographic

**Pre-Treatment Care (OxyGeneo):**
- Remove makeup; arrive with clean skin
- Avoid active retinoid or AHA products 2–3 days prior for sensitive skin
- No special restrictions for most patients — this is the accessible entry-level treatment

**Post-Treatment Care (OxyGeneo):**
- Skin may be slightly pink for 1–2 hours — normal
- Noon hydration products to lock in benefits: Halo-Ronic Serum + appropriate moisturizer
- SPF from the same day (Pavise DiamondCore)
- May resume full skincare routine same evening
- Recommend Noon home-care regimen at checkout for each visit

**Integration:**
- Prejuvenation Express: OxyGeneo + LED TriWave (same day; LED post-OxyGeneo)
- Prejuvenation Signature: OxyGeneo + PlaDuo Argon
- Can be paired with most treatments as a "soft prep" in the same appointment

---

### 2.6 LED TriWave Phototherapy

**Technology:** Multi-wavelength LED (Red, Near-Infrared, Blue — depending on indication)
**Indications by wavelength:**
- Red (630nm): Collagen stimulation, anti-aging, wound healing acceleration
- Near-infrared (830nm): Deep tissue healing, inflammation reduction, post-procedure recovery
- Blue (415nm): Active acne, antibacterial (P. acnes)

**No prep or downtime.** Safe immediately before or after other treatments.

**Pre-Treatment:** None required. Remove makeup. Protective goggles worn during session.

**Post-Treatment:**
- **Ideal synergy:** Apply Epicutis Lipid Serum BEFORE LED session — the Glucosylrutin flavonoid in it is mechanistically relevant for photobiomodulation (equivalent mechanism to EGCG)
- Noon Halo-Ronic Serum is an alternative pre-LED serum
- Post-LED: any Noon concern product; skin is primed for absorption
- SPF same day if going outdoors

**Membership note:** 1 complimentary LED session/month included in Treasury Reserve tier. Acne/rosacea/chronic skin conditions may qualify for LED memberships ($550/month for up to 4 sessions/month).

---

### 2.7 Dermatwist (DermaTwist) — Mechanical Microneedling / CIT

**Technology:** Collagen Induction Therapy (CIT) via mechanical microneedling
**Indications:** Acne scarring (rolling/boxcar), fine lines, texture, stretch marks, scalp/hair restoration
**Delegable to:** Tammy Hundt, RN (contractor)

**Pre-Treatment Care:**
- Discontinue retinoids and AHAs 5–7 days prior
- Noon Pre-Procedure Program recommended 10–14 days prior
- No active skin infections/breakouts on treatment area
- No isotretinoin within 6 months
- Topical anesthesia 30–45 minutes before

**Post-Treatment Care:**
- **Days 1–2:** Epicutis Lipid Serum + HYVIA Crème; Lipid Recovery Mask (face or zone-appropriate)
- Epicutis Hydrobiome Mist for comfort and microbiome support
- **Day 2–5:** May reintroduce gentle Noon products (Igloo Moist, Halo-Ronic)
- **Week 2+:** Full Noon concern protocol
- Avoid makeup 24–48 hours
- SPF from Day 1 (Pavise DiamondCore)
- For scalp CIT (hair restoration): DE|RIVE (AMP) or KeraFactor growth factors applied post-needling; Avari Purasomes or CORE Rose Exosomes as premium add-on

---

### 2.8 OBSERV Skin Analysis Imaging

**Role:** Not a treatment — a diagnostic and consultation tool.
**Use cases:** Baseline assessment, tracking treatment progress, objectively demonstrating improvements
**Agent integration:** Reference OBSERV as the starting point for any new patient journey ("Your OBSERV analysis will show us exactly what's happening beneath the surface")
**Membership:** Annual OBSERV analysis included in Treasury Signature tier

---

## 3. Skincare Brand Schema

The agent must ONLY recommend from approved Treasury Aesthetics brands. Never suggest brands not in this schema (e.g., iS Clinical, Eltraderm, SkinCeuticals, Caldera Lab — all disqualified due to consumer retail availability or lack of margin protection).

**Non-negotiable retail philosophy:**
- Professional-only distribution required
- No DTC / Amazon / online consumer availability permitted
- Brands with unprotected margins are disqualified regardless of product quality

---

### 3.1 Noon Aesthetics — Core Clinical Skincare Brand

**Distributor:** DermaSpark Products Inc. (Canada)
**Technology:** Patented DermShield™ — allows high-concentration AHA/BHA actives without typical irritation
**Validation:** DermShield validated in December 2021 *Journal of Drugs in Dermatology*
**Safe for all Fitzpatrick types including IV–VI**
**Requires:** Noon Academy certification (clinic is certified)

**Concern Code System (use these internally for routing):**

| Code | Concern |
|---|---|
| `oA` | Anti-aging |
| `Br` | Brightening / pigmentation |
| `Ac` | Acne |
| `Rs` | Rosacea |
| `Ds` | Dry skin / barrier |
| `Sb` | Seborrhea / oily skin |

**Key Product Categories:**

**Cleanse & Prepare:**
- C-Foaming Cleanser — Daily detoxifying, stable Vitamin C (all types)
- MicroSoft Cleanser — Delicate nourishing microemulsion (sensitive, dry, post-procedure)
- CosmoClear Cleanser — AHA + BHA purifying (oily, acne-prone, Ac/Sb)

**Hydrate & Soothe:**
- Halo-Ronic Serum — HA + Neem + Curcuma hydrating serum (all types; excellent pre-LED)
- HydroCalming + Vit Complex — Soothing with antioxidants (Rs, Ds, post-procedure)
- Igloo Moist — High-performance hydrating/cooling treatment (post-procedure, recovery)
- Igloo Mask — Intensive cooling/hydrating/soothing mask (acute recovery)

**Correct / Active Concern Treatment:**
- Lacto 10 — 10% lactic acid rejuvenation (oA, Br, mild Ac)
- Lacto-C 15 — 15% lactic + ceramides 2, 3, 6 (oA, Ds, barrier repair with exfoliation)
- Lacto-S Oil Control — 10% lactic + 2% salicylic (Ac, Sb)

**In-Clinic Chemical Peels:**
- **J-Peel** — Anti-aging formula
- **S-Peel** — 20% salicylic acid for acne; safe for Fitzpatrick IV–VI with DermShield
- **G-Peel** — 50% glycolic for texture and resurfacing
- **P-Peel 20** — 20% pyruvic + 20% lactic (multi-action)
- Protocol: 3–6 sessions spaced 3 weeks apart

**Device-Specific Integration:**
- **Pre-VirtueRF:** Noon Gear Up Kit (official exclusive protocol with Cartessa)
- **Post-VirtueRF / Post-Laser:** Noon Accelerate Kit
- **Post-Procedure Home Care:** MicroSoft Cleanser → Igloo Moist or Halo-Ronic → Concern serum → SPF
- **Peel Series Home Care:** MicroSoft or C-Foaming Cleanser + targeted serum matching peel type

---

### 3.2 Epicutis — Recovery, Barrier Repair & Luxury Skincare

**Distributor/Supplier:** Avari Medical (Vancouver) — customerservice@avarimedical.com
**Key Patented Technologies:**
- **TSC (Tetramethylhexadecenyl Succinoyl Cysteine):** Proprietary lipid molecule; barrier restoration and anti-inflammatory
- **HYVIA™:** Patented chia seed oil extract; deep moisturization and skin resilience

**Primary Role in Treasury Protocols:** Post-procedure recovery system. This is the FIRST thing applied after any energy device treatment. Active Noon ingredients come LATER.

**Complete Product Lineup:**

| Product | Primary Use | Timing |
|---|---|---|
| **Lipid Serum** | Barrier repair, anti-inflammatory, pre-LED primer | Days 1–7 post-procedure; ongoing |
| **HYVIA® Crème** | Deep moisturization, occlusive sealing of repaired barrier | Days 1–7 post-procedure; ongoing |
| **Oil Cleanser** | Gentle, lipid-based cleansing (no stripping) | Immediate post-procedure cleansing |
| **Enzyme Exfoliating Powder** | Mild enzyme exfoliation (NOT for fresh post-procedure skin) | Maintenance phase, not acute recovery |
| **Lipid Recovery Mask — Face** | Intensive barrier repair single-use mask | Day 1 post-procedure; acute recovery |
| **Lipid Recovery Mask — Neck** | Zone-specific for neck treatments | Day 1 post-procedure (neck zone) |
| **Lipid Recovery Mask — Eyes** | Periorbital recovery | Day 1 post-ExactRF, post-Plasma Frax eye area |
| **Arctigenin Brightening Treatment** | Melanin regulation, brightening | Maintenance; 3–5 days post-procedure |
| **Hydrobiome Mist** | Microbiome balance, comfort, hydration | Days 1–5 any procedure; ongoing daily |
| **Lipid Body Treatment** | Body areas (DeepRF, stretch marks) | Same recovery logic as face protocol |
| **Luxury Skincare Set** | Lipid Serum + HYVIA Crème retail set | Retail offering |
| **Post-Procedure Set** | Oil Cleanser + Lipid Serum + HYVIA Crème + Lipid Recovery Mask | Full recovery retail bundle |

**Critical Agent Rule:** Epicutis is the bridge between treatment and the return to Noon actives. The sequence is always:
```
Treatment → Epicutis Recovery (Days 1–3+) → Gradual Noon Actives Introduction → Full Noon Regimen
```

**Epicutis Lipid Serum as pre-LED primer:** The Glucosylrutin flavonoid in Lipid Serum has mechanistic relevance to photobiomodulation (equivalent to EGCG). Apply before LED TriWave sessions for enhanced photobiomodulation benefit.

---

### 3.3 Pavise — SPF & Defense

**Technology:** DiamondCore SPF (proprietary diamond-powder SPF formulation)
**Role:** Daily broad-spectrum sun protection and defense
**Status:** Accepted into Treasury brand schema
**When to recommend:** Every single protocol, every patient, every day. Non-negotiable.

**Agent rule:** SPF is always the final step of every morning routine recommendation, and the first post-procedure add-on from Day 1. Never build a skincare regimen without Pavise DiamondCore SPF.

---

### 3.4 KeraFactor — Hair & Scalp Growth Factors

**Role:** Hair restoration protocols — growth factor support for scalp health and hair density
**Integration:** Pair with NouvaDerm Hair Support mode, DermaTwist scalp CIT, and exosome treatments

---

## 4. Regenerative Biologics & Add-Ons

The agent must understand the taxonomy of biologics and NEVER conflate them in patient-facing language.

### Taxonomy (teach patients this)
1. **True exosomes (mammalian-derived):** Avari Purasomes — strongest biological exosome option available in Canada
2. **PDENs (Plant-Derived Exosome-like Nanoparticles):** EXO|E (AMP) — plant-derived; meaningful but taxonomically distinct from mammalian exosomes
3. **Synthetic liposomal nanoparticles:** Different mechanism — do not call "exosomes"
4. **PDRN:** VAMP Advanced (Prollenium) — polynucleotide tissue repair; Health Canada & FDA compliant; best-in-class Canadian option
5. **Growth factors:** KeraFactor (hair); CORE Rose Exosomes (Xcite)
6. **Mesotherapy cocktails:** My Skin Chemistry ampule boxes (Exosomes + PDRN variants)

### Biologics Product Directory

| Product | Supplier | Type | Best Use Case |
|---|---|---|---|
| **EXO\|E** | AMP / Aesthetic Management Partners | PDENs | Post-VirtueRF, post-PlaDuo Pro, general skin recovery |
| **Avari Purasomes** | Avari Medical (Vancouver) | True mammalian exosomes | Premium post-laser, post-RF, hair restoration |
| **VAMP Advanced** | Prollenium | PDRN | Tissue repair, wound healing support, anti-aging |
| **DE\|RIVE** | AMP | Exosome/plant-derived | Hair restoration protocols |
| **CORE Rose Exosomes** | Xcite Tech | Exosome-derived | General skin recovery, premium add-on |
| **My Skin Chemistry** | My Skin Chemistry | Exosome + PDRN ampules | Flexible add-on system |

### When to Recommend Biologics (Agent Logic)
- **Post-VirtueRF:** EXO|E as standard add-on; upgrade to Avari Purasomes for premium
- **Post-NouvaDerm (any mode):** EXO|E or Avari Purasomes depending on budget
- **Post-PlaDuo Pro:** EXO|E (AMP's own ecosystem product — natural pairing)
- **Post-DermaTwist scalp:** DE|RIVE + KeraFactor; Avari Purasomes as premium upgrade
- **Hair Restoration Protocol:** NouvaDerm Hair Support + DE|RIVE + KeraFactor + optional Avari Purasomes
- **PDRN (VAMP Advanced):** Always a complementary add-on to exosomes for enhanced tissue repair

---

## 5. Treatment Menu Architecture

Nine treatment categories. Each has a core treatment with add-on options.

| # | Category | Primary Devices |
|---|---|---|
| 1 | Laser Skin Rejuvenation | NouvaDerm (NOUVAGlo), Quanta UltraLight |
| 2 | RF Microneedling | VirtueRF (SmartRF, DeepRF, ExactRF) |
| 3 | Signature Facials & Peels | OxyGeneo, Noon Chemical Peels |
| 4 | Plasma Revitalization | PlaDuo Pro (Nitrogen + Argon) |
| 5 | Active Acne Management | PlaDuo Argon, Quanta KTP, Noon S-Peel |
| 6 | Skin Tightening & Contouring | VirtueRF ExactRF, DeepRF body |
| 7 | Hair Restoration | NouvaDerm Hair Support, DermaTwist Scalp, Biologics |
| 8 | Prejuvenation Program | OxyGeneo + LED TriWave / PlaDuo |
| 9 | NOUVAGlo Express | NouvaDerm non-ablative express mode |

**Available Add-Ons (checkbox model for patients):**
- Exosomes (EXO|E or Avari Purasomes)
- PlaDuo Pro (Nitrogen or Argon)
- PDRN (VAMP Advanced)
- Noon Chemical Peel (appropriate to device)
- Masks (Igloo Mask, Epicutis Lipid Recovery Mask)
- KeraFactor (hair/scalp)

---

## 6. Condition-to-Protocol Routing

The agent should use this routing logic when a patient describes their concern:

| Patient Concern | Primary Protocol | Skincare Focus |
|---|---|---|
| **Anti-aging / early lines** | VirtueRF + NOUVAGlo (combination; 6-week gap) | Noon oA products + Epicutis + Pavise SPF |
| **Active acne** | PlaDuo Argon + Quanta KTP + Noon S-Peel | Noon CosmoClear + Lacto-S + Epicutis Hydrobiome |
| **Acne scarring** | VirtueRF + DermaTwist + Biologics | Noon oA/Ac + Epicutis recovery |
| **Melasma / pigmentation** | Quanta Pigmentation + Noon G-Peel | Noon Br products + Epicutis Arctigenin + Pavise SPF (critical) |
| **Rosacea / redness** | Quanta Vascular + LED TriWave | Noon Rs (HydroCalming) + Epicutis (all) |
| **Skin texture / pores** | NOUVAGlo + OxyGeneo | Noon oA/Br + Epicutis Lipid Serum |
| **Hair loss / thinning** | NouvaDerm Hair Support + DermaTwist Scalp + Biologics | KeraFactor + DE\|RIVE + VAMP Advanced |
| **Prejuvenation (under 35)** | OxyGeneo + LED TriWave or PlaDuo Argon | Noon hydration + Epicutis essentials + Pavise |
| **Skin tightening / laxity** | VirtueRF (SmartRF face; DeepRF body) | Noon oA + Epicutis + Pavise SPF |
| **Periorbital / eyes** | ExactRF (fat herniation lower lid) | Epicutis Eye Mask + Lipid Serum |
| **Body rejuvenation** | VirtueRF DeepRF | Epicutis Lipid Body Treatment + Noon body products |

---

## 7. Condition Protocols (Formal)

```
Acne Protocol:         PlaDuo Argon + Quanta KTP + Noon S-Peel + CosmoClear + Lacto-S + Epicutis Hydrobiome
Melasma Protocol:      Quanta Pigmentation + Noon G-Peel + Noon Br actives + Epicutis Arctigenin + Pavise SPF
Rosacea Protocol:      Quanta Vascular + LED TriWave + Noon HydroCalming + Epicutis full set
Anti-Aging Protocol:   VirtueRF + NOUVAGlo + Noon oA products + Epicutis + Pavise
Hair Protocol:         NouvaDerm Hair Support + DermaTwist Scalp + DE|RIVE + KeraFactor + Purasomes (premium)
Prejuvenation:         OxyGeneo + LED TriWave + Noon hydration + Epicutis + Pavise
```

---

## 8. Universal Skincare Regimen Builder

When building any full skincare regimen, always follow this structure:

### Morning Routine (template)
1. **Cleanse:** Noon cleanser (type matched to skin concern — MicroSoft, C-Foaming, or CosmoClear)
2. **Treat:** Noon concern serum (oA / Br / Ac / Rs / Ds / Sb — matched)
3. **Hydrate:** Noon Halo-Ronic Serum or Igloo Moist (depending on skin type)
4. **Moisturize:** Epicutis HYVIA Crème (daily moisturizer — doubles as barrier maintenance)
5. **Protect:** Pavise DiamondCore SPF — ALWAYS LAST, EVERY MORNING, NO EXCEPTIONS

### Evening Routine (template)
1. **Cleanse:** Epicutis Oil Cleanser (gentle, lipid-preserving) OR Noon cleanser
2. **Treat:** Noon active concern serum
3. **Repair:** Epicutis Lipid Serum
4. **Moisturize:** Epicutis HYVIA Crème OR Noon zone-appropriate moisturizer

### Post-Procedure Deviation (Days 1–5 after any energy device)
1. **Cleanse:** Epicutis Oil Cleanser OR Noon MicroSoft Cleanser ONLY (no actives)
2. **Soothe:** Epicutis Lipid Serum 2–4× daily
3. **Moisturize:** Epicutis HYVIA Crème
4. **Mask:** Epicutis Lipid Recovery Mask (zone-appropriate) as needed
5. **Mist:** Epicutis Hydrobiome Mist for comfort
6. **Protect:** Pavise DiamondCore SPF (Day 1 onward, even in recovery)
7. **NO:** Retinoids, AHAs, BHAs, vitamin C, niacinamide at high concentration, or any Noon actives during Days 1–3

---

## 9. Key Clinical Safety Rules (Agent Must Enforce)

These are non-negotiable clinical constraints. The agent must never recommend violating these:

1. **No actives within 24–72 hours post-ablation** — barrier protection ONLY in acute phase
2. **RF + Laser minimum 6 weeks apart** — never schedule VirtueRF and NouvaDerm/Quanta within 6 weeks
3. **RF microneedling spacing: 4–6 weeks** between sessions
4. **No isotretinoin within 6 months** for any energy device treatment
5. **Antiviral prophylaxis** required for HSV history before facial laser or RF
6. **ExactRF ≠ PlaDuo Pro ≠ Plexr** — three distinct devices for distinct indications; do not conflate
7. **Exosome taxonomy matters** — always distinguish Avari Purasomes (true mammalian exosomes) from EXO|E (PDENs) in patient communication
8. **PlaDuo Pro strongest for acne/rosacea** (60–70%); weaker for general anti-aging (20–25%) — position accordingly
9. **SPF is never optional** — Pavise DiamondCore SPF is part of every protocol from Day 1
10. **Enzyme Exfoliating Powder is NOT for acute recovery** — only maintenance phase
11. **HOCl (HaleDerma):** If used in-clinic, apply before exosomes; no published data on HOCl-exosome interaction; strongest argument is as take-home recovery product Days 1–5

---

## 10. Membership Tiers

| Tier | Monthly | Credit | Key Benefits |
|---|---|---|---|
| **Treasury Essential** | $199 | $199 | 10% off retail + treatments, priority booking |
| **Treasury Reserve** | $399 | $399 | 15% off, 1 complimentary LED/month, priority booking |
| **Treasury Signature** | $699 | $699 | 20% off, 1 OxyGeneo or LED/month, annual OBSERV, dedicated coordinator |
| **Prejuvenation Membership** | $299 | $299 | 1 OxyGeneo or LED/month, 15% off retail, 12-month skin roadmap |

**Credit model:** Monthly fee credited in full to patient account; rollover up to 3 months.

---

## 11. Staff & Delegation

| Person | Role | Delegable Treatments |
|---|---|---|
| **Dr. Jason Latsky** | Physician-owner | All treatments; physician-required: ablative laser, injectables, medical-grade peels |
| **Tammy Hundt, RN, CPNc** | Nurse injector / independent contractor | VirtueRF, NOUVAGlo, OxyGeneo, LED TriWave, DermaTwist, PlaDuo Pro (per delegation) |

**Revenue split:** 70/30 in Tammy's favour.

When the agent builds a treatment recommendation, it should note whether physician involvement is required.

---

## 12. AI Agent Behavior Guidelines

### Recommendation Logic
- **Comprehensive-first:** Build the complete ideal treatment plan, then offer simplifications with clinical tradeoffs explained. Never lead with a stripped-down plan.
- **Evidence-first:** Cite clinical rationale. Never recommend something based on marketing alone.
- **Always end with skincare:** Every treatment recommendation ends with a full home-care skincare regimen built from Noon + Epicutis + Pavise.
- **Add-on suggestions:** After core recommendation, always suggest 2–3 clinically relevant add-ons with brief rationale.

### Language & Tone
- Warm, enthusiastic, genuine — NOT cold luxury or clinical detachment
- Educational: explain why, not just what
- Use layperson language first, then introduce brand names naturally
- Call the clinic "Treasury Aesthetics" — not just "the clinic"

### Patient Journey Flow
1. **OBSERV skin analysis** (new patients) — baseline imaging
2. **Consultation:** Identify concerns, Fitzpatrick type, medical history (Accutane, HSV, medications)
3. **Treatment plan:** Build comprehensive plan using routing logic
4. **Skincare regimen:** Full morning/evening routine from approved brands
5. **Add-ons:** Biologics, peels, booster options
6. **Membership:** Recommend most appropriate tier
7. **Booking:** Direct to Phorest

---

## 13. Devices Under Evaluation (Phase 2 — Not Yet Active)

Do NOT include these in current treatment recommendations. Reference only if asked:

- **JetPeel** (~6 months post-launch): Hydroporation 200m/sec; planned for post-NOUVAGlo + HOCl/hydration infusion, post-VirtueRF recovery, scalp hair restoration
- **Sofwave** (future acquisition): GLP-1 laxity protocol anchor; firming and lifting
- **Ultraclear Erbium Glass** (under evaluation): Cold fiber laser resurfacing

---

## 14. Glossary

| Term | Definition |
|---|---|
| DermShield™ | Noon's proprietary technology enabling high-concentration actives without irritation |
| TSC | Tetramethylhexadecenyl Succinoyl Cysteine — Epicutis patented lipid molecule |
| HYVIA™ | Epicutis patented chia seed oil extract |
| NOUVAGlo | NouvaDerm non-ablative mode (no downtime version) |
| ExactRF | VirtueRF monopolar single-needle handpiece for periorbital/jawline |
| SpinShot Technology | PlaDuo Pro's precision plasma delivery system |
| PDENs | Plant-Derived Exosome-like Nanoparticles (EXO|E) — distinct from mammalian exosomes |
| PDRN | Polynucleotide Deoxyribonucleic acid — tissue repair biologic (VAMP Advanced) |
| CIT | Collagen Induction Therapy (mechanical microneedling / DermaTwist) |
| OBSERV | Skin analysis imaging system for baseline and progress tracking |
| Gear Up Kit | Noon pre-VirtueRF protocol kit |
| Accelerate Kit | Noon post-VirtueRF protocol kit |
| Prejuvenation | Prevention-focused aesthetics for the under-35 demographic ("collagen banking") |

---

*Document prepared for Treasury Aesthetics AI Consultation Agent*
*Physician: Dr. Jason Latsky | Treasury Aesthetics | Toronto, ON | treasuryhealth.ca*
*Last updated: May 2026*
