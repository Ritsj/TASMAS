"""Shared text-generation backends.

Each generator takes a system prompt and a fully-composed user message and
returns the model's text response. Three backends are supported, matching the
CLI flags:
  - Anthropic API      (default; pay-per-token)
  - Claude subscription (--useSubscription, via the Claude Agent SDK)
  - local Ollama model  (--useLocal)

Both `summarize` and `storify` build on these so the backend logic lives in one
place.
"""
import sys
import asyncio

DEFAULT_MODEL = "claude-opus-4-8"


def make_api_client(api_key):
    # imported lazily so --useSubscription / --useLocal runs don't need it loaded
    import anthropic
    return anthropic.Anthropic(api_key=api_key)


def estimate_tokens(text):
    # Rough estimate: word count alone underestimates tokens (English runs
    # ~1.3 tokens/word), so scale it up.
    return int(len(text.split()) * 1.3)


def generate_via_api(client, system_prompt, user_content, model=DEFAULT_MODEL):
    with client.messages.stream(
        model=model,
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_content},
        ],
    ) as stream:
        message = stream.get_final_message()

    return next(block.text for block in message.content if block.type == "text")


def generate_via_subscription(system_prompt, user_content, model=DEFAULT_MODEL):
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
    except ImportError:
        print("  The claude-agent-sdk package is required for --useSubscription.")
        print("  Install it with: pip install claude-agent-sdk")
        print("  (Also requires the Claude Code CLI to be installed and logged in --")
        print("   run `claude setup-token`, or just be logged in via `claude login`.)")
        sys.exit(1)

    async def run():
        options = ClaudeAgentOptions(
            model=model,
            system_prompt=system_prompt,
            tools=[],
            max_turns=1,
        )
        text_parts = []
        async for message in query(prompt=user_content, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
        return ''.join(text_parts)

    return asyncio.run(run())


def generate_via_ollama(system_prompt, user_content, local_model, local_host, local_context_tokens):
    try:
        from ollama import Client
    except ImportError:
        print("  The ollama package is required for --useLocal.")
        print("  Install it with: pip install ollama")
        print("  (Also requires a local Ollama server -- `ollama serve` -- with the")
        print(f"   model pulled: `ollama pull {local_model}`.)")
        sys.exit(1)

    # Ollama truncates input that doesn't fit num_ctx rather than raising an
    # error, so warn early instead of silently generating from a truncated input.
    approx_tokens = estimate_tokens(system_prompt + user_content)
    if approx_tokens > local_context_tokens * 0.75:
        print(f"  WARNING: this prompt is roughly {approx_tokens} tokens, close to or over the")
        print(f"  configured context window ({local_context_tokens} tokens, --localContextTokens).")
        print("  Ollama silently truncates input that doesn't fit rather than erroring --")
        print("  consider raising --localContextTokens (memory permitting).")

    print(f"  Generating with local Ollama model '{local_model}' -- this can be slow on CPU-only hardware.")

    client = Client(host=local_host) if local_host else Client()

    response = client.chat(
        model=local_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        options={"num_ctx": local_context_tokens},
    )

    return response.message.content
