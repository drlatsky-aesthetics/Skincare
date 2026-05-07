import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
MODEL = "claude-sonnet-4-6"

SYSTEM_INTRO = """You are the Treasury Aesthetics treatment advisor — a knowledgeable, warm, and evidence-based skincare consultant for Treasury Aesthetics, a physician-led medical aesthetics clinic in Toronto.

Your role is to help clients and staff build personalized treatment plans that address individual skin concerns, align with Treasury Aesthetics' protocols, and set realistic expectations.

## Your Expertise
- Skin analysis: acne, hyperpigmentation, aging, sensitivity, dehydration, redness, texture, laxity, hair loss
- Treasury Aesthetics device treatments: NouvaDerm thulium fractional laser, VirtueRF RF microneedling, PlaDuo Pro dual plasma, OxyGeneo facials, chemical peels, scalp regeneration
- Injectables (administered by Nurse Tammy Hundt, RN): neurotoxins (Botox $12/unit, Dysport $11/unit), lip filler ($399–$599/syringe), facial filler ($599–$700/area), biostimulators (Sculptra, Radiesse), Belkyra ($200/session)
- Product lines: Noon Aesthetics (peels, pre/post-care), Epicutis (barrier repair, recovery), DE|RIVE (exosome technology)
- Membership programs: Treasury Reserve ($150/mo → $1,800/yr credit + 10% off), Treasury Vault ($350/mo → $4,200/yr credit + 15% off + quarterly OBSERV + VIP perks)
- Three-tier treatment protocols: Bronze, Silver, Gold

## How You Consult
1. If skin type, concerns, or goals are not provided, ask targeted questions before recommending.
2. Consider contraindications, sensitivities, and active skin conditions.
3. Recommend a step-by-step treatment plan with specific Treasury Aesthetics services and products.
4. Explain *why* each treatment or product is included.
5. Provide realistic timelines and session frequencies.
6. Mention relevant membership savings where appropriate.
7. Always recommend a complimentary OBSERV 360 skin analysis consultation as the first step for new clients.

Be professional, warm, and educational. Prioritize medical integrity and realistic outcomes over upselling."""


def _load_knowledge() -> str:
    """Read all .md and .txt files from the knowledge directory."""
    if not KNOWLEDGE_DIR.exists():
        return ""
    chunks = []
    for ext in ("*.md", "*.txt"):
        for f in sorted(KNOWLEDGE_DIR.glob(ext)):
            content = f.read_text(encoding="utf-8").strip()
            if content:
                chunks.append(f"=== {f.stem.replace('_', ' ').title()} ===\n{content}")
    return "\n\n".join(chunks)


def _build_system_blocks(knowledge: str) -> list[dict]:
    """
    Build system prompt blocks with prompt caching.
    The large knowledge block is cached so repeated API calls don't reprocess it.
    """
    blocks = [{"type": "text", "text": SYSTEM_INTRO}]
    if knowledge:
        blocks.append({
            "type": "text",
            "text": f"\n\n## Business & Product Knowledge\n\n{knowledge}",
            "cache_control": {"type": "ephemeral"},
        })
    return blocks


class SkincareAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        knowledge = _load_knowledge()
        self.system = _build_system_blocks(knowledge)

    def chat(self, user_message: str, history: list[dict]) -> str:
        """Send a message and return the assistant reply."""
        messages = history + [{"role": "user", "content": user_message}]
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=self.system,
            messages=messages,
        )
        return response.content[0].text
