import os
import sys
import textwrap
import backends

SYSTEM_PROMPT = "You are a chatbot which can summarize long transcripts."

def _read_prompt(prompt_file):
    with open(prompt_file, 'r') as file:
        return file.read()

def do_summary(transcript, client, prompt_file):
    return backends.generate_via_api(client, SYSTEM_PROMPT, f'{_read_prompt(prompt_file)}{transcript}')

def do_summary_via_subscription(transcript, prompt_file):
    return backends.generate_via_subscription(SYSTEM_PROMPT, f'{_read_prompt(prompt_file)}{transcript}')

def do_summary_via_ollama(transcript, prompt_file, local_model, local_host, local_context_tokens):
    return backends.generate_via_ollama(SYSTEM_PROMPT, f'{_read_prompt(prompt_file)}{transcript}', local_model, local_host, local_context_tokens)

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
        client = backends.make_api_client(anthropic_api_key)

    failures = []
    for prompt_file in prompt_files:
        # Call your command here
        print()
        print(f"  - Prompt {prompt_file}...")

        # A single prompt failing (API error, timeout, model issue) shouldn't
        # discard the summaries already produced -- report it and keep going.
        # (SystemExit from the backend import checks intentionally propagates.)
        try:
            if use_local:
                summary = do_summary_via_ollama(transcript, prompt_file, local_model, local_host, local_context_tokens)
            elif use_subscription:
                summary = do_summary_via_subscription(transcript, prompt_file)
            else:
                summary = do_summary(transcript, client, prompt_file)
        except Exception as ex:
            print(f"    ERROR: failed to summarize with {prompt_file}: {ex}")
            print("    Skipping this prompt and continuing.")
            failures.append(prompt_file)
            continue

        filename = os.path.splitext(os.path.basename(prompt_file))[0].replace("prompt_", "")
        filename = f"summary_{filename}.txt"
        output_path = os.path.join(input_dir, filename)
        with open(output_path, 'w') as file:
            file.write(summary)
        print()
        print("    Result:")
        print("    ---------")
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            # no tty attached (e.g. running non-interactively) -- fall back to a sane default
            terminal_width = 100
        # Split the summary into lines, then indent and wrap each line
        summary_lines = summary.split('\n')
        wrapped_summary = '\n'.join('\n'.join(textwrap.wrap(line, width=terminal_width, initial_indent='     ', subsequent_indent='     ')) for line in summary_lines)
        print(wrapped_summary)
        print("    ---------")
        print(f"    Written to {output_path}.")
        print()
        print()

    if failures:
        print(f"  {len(failures)} of {len(prompt_files)} prompt{'s' if len(prompt_files) > 1 else ''} failed:")
        for prompt_file in failures:
            print(f"    - {prompt_file}")
        print()
