"""
AI Changelog Generator — the core engine.
Uses DeepSeek/OpenAI-compatible API to turn raw git commits into user-facing changelog entries.
"""
import json
from openai import AsyncOpenAI
from app.config import settings

# System prompt — the secret sauce. Carefully engineered to produce
# changelogs that sound like a human product manager wrote them.
SYSTEM_PROMPT = """You are a professional product changelog writer for SaaS products.

Your job: transform a list of git commits into a polished, user-facing changelog entry.

RULES:
1. Group changes into categories: 🚀 New Features, ✨ Improvements, 🐛 Bug Fixes, 🔒 Security
2. Write for END USERS, not developers. Never mention "commit", "PR", "refactor", "merge", "dependency", "bump"
3. Each entry should be 1-2 sentences describing what changed from the user's perspective
4. If a change is purely internal (lint fixes, CI changes, typo fixes), omit it
5. Be concise and use simple language
6. Add emoji to each category header
7. If there are no meaningful user-facing changes, say "Minor improvements and stability updates."
8. Output ONLY valid JSON, no markdown fences, no extra text

Output format:
{
  "title": "A short, catchy title summarizing this release (e.g. 'Faster Exports & Dark Mode')",
  "categories": [
    {
      "name": "🚀 New Features",
      "items": ["Item 1", "Item 2"]
    },
    {
      "name": "✨ Improvements",
      "items": ["Item 1"]
    }
  ]
}"""


async def generate_changelog(commits: list[dict], version: str = None) -> dict:
    """
    Generate a changelog entry from a list of git commits.

    Args:
        commits: list of commit dicts with keys: sha, message, author, date
        version: optional version tag (e.g. "v1.2.0")

    Returns:
        dict with title, categories, and raw markdown
    """
    if not commits:
        return {
            "title": "Maintenance Release",
            "categories": [{"name": "🔧 Maintenance", "items": ["Routine maintenance and optimizations."]}],
            "markdown": "## 🔧 Maintenance\n\n- Routine maintenance and optimizations.\n"
        }

    # Build a compact representation of commits for the AI
    commit_summary = []
    for c in commits:
        msg = c.get("message", "").split("\n")[0][:120]  # First line only, truncated
        commit_summary.append(f"[{c['sha'][:7]}] {msg}")

    commit_text = "\n".join(commit_summary)

    client = AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url
    )

    response = await client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate a changelog from these commits:\n\n{commit_text}"}
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    raw = response.choices[0].message.content.strip()

    # Parse the JSON response
    try:
        # Sometimes the model wraps in ```json blocks
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
            if raw.endswith("```"):
                raw = raw[:-3].strip()
            raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: use raw text as content
        data = {
            "title": f"Release{' ' + version if version else ''}".strip(),
            "categories": [{"name": "📝 Updates", "items": [line.strip("- ") for line in raw.split("\n") if line.strip()]}]
        }

    # Build markdown
    parts = []
    for cat in data.get("categories", []):
        parts.append(f"## {cat['name']}\n")
        for item in cat["items"]:
            parts.append(f"- {item}\n")
        parts.append("\n")

    data["markdown"] = "".join(parts).strip()

    return data
