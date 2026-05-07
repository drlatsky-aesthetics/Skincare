import os
import anthropic
from dotenv import load_dotenv
from knowledge_loader import load_knowledge

load_dotenv()

MODEL = "claude-sonnet-4-6"

SYSTEM_INTRO = """You are the Treasury Aesthetics treatment advisor — warm, enthusiastic, and evidence-based. You work for Dr. Jason Latsky's physician-led medical aesthetics clinic in Toronto (treasuryhealth.ca).

Your full clinical knowledge base is provided below. Follow it precisely. Key rules:
- Only recommend Noon Aesthetics, Epicutis, and Pavise — never outside brands
- Pavise DiamondCore SPF is always the final morning step and always Day 1 post-procedure
- Epicutis recovery always precedes Noon actives post-procedure
- RF + Laser minimum 6-week gap
- Always start new patients with a complimentary OBSERV 360 consultation
- End every recommendation with a full morning + evening skincare regimen
- Note whether Dr. Latsky or Tammy Hundt, RN can perform each treatment"""


def _build_system_blocks(knowledge: str) -> list[dict]:
    """
    Build system prompt blocks with prompt caching on the large knowledge base
    so repeated API calls don't reprocess it.
    """
    blocks = [{"type": "text", "text": SYSTEM_INTRO}]
    if knowledge:
        blocks.append({
            "type": "text",
            "text": f"\n\n## Full Clinical Knowledge Base\n\n{knowledge}",
            "cache_control": {"type": "ephemeral"},
        })
    return blocks


class SkincareAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables.")
        self.client = anthropic.Anthropic(api_key=api_key)
        knowledge = load_knowledge()
        self.system = _build_system_blocks(knowledge)

    def chat(self, user_message: str, history: list[dict]) -> str:
        messages = history + [{"role": "user", "content": user_message}]
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=self.system,
            messages=messages,
        )
        return response.content[0].text
