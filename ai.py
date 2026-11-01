import os

def summarize_with_claude(headlines):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "Claude AI is not configured. Add ANTHROPIC_API_KEY to your cloud environment variables."
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        text = "\n".join(f"- {x.get('title','')}" for x in headlines[:30])
        response = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-latest"),
            max_tokens=900,
            messages=[{"role":"user","content":
                "Analyze these Indian market headlines for factual themes. Group affected companies/sectors if explicitly identifiable. Separate confirmed headline facts from possible implications. Do not invent tickers, prices, or trade recommendations. Mention uncertainty.\n\n" + text}]
        )
        return "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    except Exception as exc:
        return f"Claude request failed: {exc}"
