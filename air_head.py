import json
import requests
from heart_cuda import HexGridNode, Token

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

def parse_natural_language_to_token(user_text: str) -> Token:
    """Uses the local LLM to translate English into thermodynamic variables."""

    system_prompt = """You are a fast, strict JSON data extractor. 
Analyze the user's text and output ONLY valid JSON. 
DO NOT think out loud. DO NOT explain. Output the JSON immediately.

You must return exactly these four keys:
- "concept": Identify the main subject/entity the user is talking about. Prefer short, consistent names. Three words maximum. Do not invent new strings.
- "valence": number from -1.0 to 1.0 (-1.0 is extreme negative/hate, 1.0 is extreme positive/love)
- "energy": number from 1.0 to 15.0
- "structural_value": number from 1.0 to 10.0

Examples:
User: "Odysseus is the greatest thing ever."
Output: {"concept": "odysseus", "valence": 0.9, "energy": 8.0, "structural_value": 7.0}

User: "I absolutely despise Odysseus."
Output: {"concept": "odysseus", "valence": -0.9, "energy": 12.0, "structural_value": 8.0}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\nUser Input: \"{user_text}\"\nJSON Output:",
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Optional wiretap (you can comment this out later)
        thinking_text = data.get("thinking", "")
        if thinking_text:
            print(f"\n[OSIRIS WIRETAP] Model thought briefly...")

        raw_text = data.get("response", "").strip()

        if not raw_text:
            print("[GLITCH] LLM returned empty response.")
            return None

        # Clean markdown if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        token_data = json.loads(raw_text)

        return Token(
            concept=token_data.get("concept", "unknown"),
            valence=float(token_data.get("valence", 0.0)),
            energy=float(token_data.get("energy", 5.0)),
            structural_value=float(token_data.get("structural_value", 3.0))
        )

    except Exception as e:
        print(f"[GLITCH] Failed to parse: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "="*55)
    print(" HEART CUDA ENGINE ONLINE ")
    print(" Air-Head (Ollama) + Interpretation Audit Connected")
    print("="*55 + "\n")

    from transference import audit_token   # <-- Import the auditor

    node = HexGridNode("living_engram_01", c_max=100.0)

    print("Type anything. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You >> ").strip()
        except KeyboardInterrupt:
            print("\nShutting down Heart CUDA...")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("Shutting down...")
            break

        if not user_input:
            continue

        print("... Parsing ...")
        token = parse_natural_language_to_token(user_input)

        if token:
            # === NEW: Run the Interpretation Audit ===
            audit = audit_token(token, user_input)

            if audit.mixed_valence_detected:
                print(f"[AUDIT] {audit.reason}")
                print(f"Confidence: {audit.confidence:.2f}")

            # Use the (possibly adjusted) token
            final_token = audit.primary_token
            print(f"[Token] {final_token}")

            result = node.process_state_change(final_token)
            print(f"[Decision] {result['decision']}")

            if result.get("reason"):
                print(f"Reason: {result['reason']}")

            print("-" * 50)