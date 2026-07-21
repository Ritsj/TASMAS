import os
import sys
import asyncio
import textwrap
import anthropic

MODEL = "claude-opus-4-8"
SYSTEM_PROMPT = "You are a chatbot which can summarize long transcripts."

def do_summary(transcript, client, prompt_file):
    with open(prompt_file, 'r') as file:
        prompt = file.read()

    with client.messages.stream(
        model=MODEL,
        max_tokens=64000,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f'{prompt}{transcript}'},
        ],
    ) as stream:
        message = stream.get_final_message()

    return next(block.text for block in message.content if block.type == "text")

def do_summary_via_subscription(transcript, prompt_file):
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
    except ImportError:
        print("  The claude-agent-sdk package is required for --useSubscription.")
        print("  Install it with: pip install claude-agent-sdk")
        print("  (Also requires the Claude Code CLI to be installed and logged in --")
        print("   run `claude setup-token`, or just be logged in via `claude login`.)")
        sys.exit(1)

    with open(prompt_file, 'r') as file:
        prompt = file.read()

    async def run():
        options = ClaudeAgentOptions(
            model=MODEL,
            system_prompt=SYSTEM_PROMPT,
            tools=[],
            max_turns=1,
        )
        text_parts = []
        async for message in query(prompt=f'{prompt}{transcript}', options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
        return ''.join(text_parts)

    return asyncio.run(run())

def do_summary_via_ollama(transcript, prompt_file, local_model, local_host, local_context_tokens):
    try:
        from ollama import Client
    except ImportError:
        print("  The ollama package is required for --useLocal.")
        print("  Install it with: pip install ollama")
        print("  (Also requires a local Ollama server -- `ollama serve` -- with the")
        print(f"   model pulled: `ollama pull {local_model}`.)")
        sys.exit(1)

    with open(prompt_file, 'r') as file:
        prompt = file.read()

    # Rough token estimate: word count alone underestimates tokens (English
    # runs ~1.3 tokens/word), so scale it up. Ollama truncates input that
    # doesn't fit num_ctx rather than raising an error, so warn early instead
    # of silently summarizing a truncated transcript.
    word_count = len((prompt + transcript).split())
    approx_tokens = int(word_count * 1.3)
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
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'{prompt}{transcript}'},
        ],
        options={"num_ctx": local_context_tokens},
    )

    return response.message.content

def summarize(input_dir, prompt_files, anthropic_api_key, use_subscription=False, use_local=False, local_model="phi4-mini", local_host=None, local_context_tokens=32768):

    if input_dir is None:
        print("Please provide an input directory.")
        return

    print()
    print("--------------------")
    print("SUMMARIZE")
    print("--------------------")
    print()

    transcript_path = os.path.join(input_dir, 'transcript.txt')
    if not os.path.exists(transcript_path):
        print("transcript.txt not found in the input directory.")
        sys.exit(1)

    with open(transcript_path, 'r') as file:
        transcript = file.read()

    if not prompt_files:
        print("  No prompts to use to summarize.")
        return

    if use_subscription:
        print("  Using your Claude subscription (via the Claude Agent SDK) instead of the API key.")
    elif not use_local:
        client = anthropic.Anthropic(api_key=anthropic_api_key)

    for prompt_file in prompt_files:
        # Call your command here
        print()
        print(f"  - Prompt {prompt_file}...")

        if use_local:
            summary = do_summary_via_ollama(transcript, prompt_file, local_model, local_host, local_context_tokens)
        elif use_subscription:
            summary = do_summary_via_subscription(transcript, prompt_file)
        else:
            summary = do_summary(transcript, client, prompt_file)

        filename = os.path.splitext(os.path.basename(prompt_file))[0].replace("prompt_", "")
        filename = f"summary_{filename}.txt"
        output_path = os.path.join(input_dir, filename)
        with open(output_path, 'w') as file:
            file.write(summary)
        print()
        print("    Result:")
        print("    ---------")
        terminal_width = os.get_terminal_size().columns
        # Split the summary into lines, then indent and wrap each line
        summary_lines = summary.split('\n')
        wrapped_summary = '\n'.join('\n'.join(textwrap.wrap(line, width=terminal_width, initial_indent='     ', subsequent_indent='     ')) for line in summary_lines)
        print(wrapped_summary)
        print("    ---------")
        print(f"    Written to {output_path}.")
        print()
        print()


