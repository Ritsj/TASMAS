"""storify: weave per-session transcripts into one continuous story.

Given a campaign folder whose subfolders each contain a `transcript.txt` (as
produced by the assemble step), storify walks the sessions in order and builds
a single flowing narrative in `story.md` at the campaign root.

It works incrementally: the "story so far" is carried forward as context into
each new session so the next chapter stays continuous with everything before it,
and a sidecar `story.state.json` records which sessions have already been
incorporated -- so re-running only processes sessions added since last time.
Pass rebuild=True to start the story over from scratch.
"""
import os
import re
import sys
import json

import backends

STORY_FILE = "story.md"
STATE_FILE = "story.state.json"

STORY_SYSTEM_PROMPT = (
    "You are a skilled chronicler who turns tabletop RPG session transcripts into "
    "a single, continuous, novel-style story. You write flowing narrative prose "
    "(not bullet-point summaries), and you maintain strict continuity of "
    "characters, locations, tone, and ongoing plot threads from one session to "
    "the next."
)


def _natural_key(name):
    # sort "session-2" before "session-10" by splitting out numeric runs
    return [int(tok) if tok.isdigit() else tok.lower() for tok in re.split(r'(\d+)', name)]


def find_sessions(campaign_dir):
    """Session subfolders (each containing transcript.txt), in natural order."""
    sessions = []
    for entry in sorted(os.listdir(campaign_dir), key=_natural_key):
        path = os.path.join(campaign_dir, entry)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, 'transcript.txt')):
            sessions.append((entry, path))
    return sessions


def _load_state(campaign_dir):
    state_path = os.path.join(campaign_dir, STATE_FILE)
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            return json.load(f)
    return {"sessions": []}


def _save_state(campaign_dir, state):
    with open(os.path.join(campaign_dir, STATE_FILE), 'w') as f:
        json.dump(state, f, indent=2)


def _load_story(campaign_dir):
    story_path = os.path.join(campaign_dir, STORY_FILE)
    if os.path.exists(story_path):
        with open(story_path, 'r') as f:
            return f.read()
    return ""


def build_prompt(story_so_far, session_name, transcript):
    if story_so_far.strip():
        instructions = (
            "Below is the continuous story so far, covering all previous sessions, "
            "followed by the transcript of a new session.\n\n"
            "Continue the story by writing the NEXT chapter, covering only the events "
            "of the new session transcript. Maintain continuity with everything in the "
            "story so far -- keep characters, locations, tone, and open plot threads "
            "consistent, and do not retell events already covered. Write flowing "
            "narrative prose and open with a chapter heading.\n"
        )
    else:
        instructions = (
            "Below is the transcript of the first session of a tabletop RPG campaign.\n\n"
            "Begin a continuous, novel-style story based on it. Establish the "
            "characters, setting, and tone. Write flowing narrative prose and open "
            "with a chapter heading.\n"
        )

    parts = [instructions]
    if story_so_far.strip():
        parts.append(
            "\n----- STORY SO FAR -----\n"
            f"{story_so_far.strip()}\n"
            "----- END STORY SO FAR -----\n"
        )
    parts.append(
        f"\n----- NEW SESSION TRANSCRIPT ({session_name}) -----\n"
        f"{transcript.strip()}\n"
        "----- END NEW SESSION TRANSCRIPT -----\n"
    )
    return "".join(parts)


def _generate_chapter(user_content, client, use_subscription, use_local,
                      local_model, local_host, local_context_tokens):
    if use_local:
        return backends.generate_via_ollama(STORY_SYSTEM_PROMPT, user_content, local_model, local_host, local_context_tokens)
    if use_subscription:
        return backends.generate_via_subscription(STORY_SYSTEM_PROMPT, user_content)
    return backends.generate_via_api(client, STORY_SYSTEM_PROMPT, user_content)


def storify(campaign_dir, anthropic_api_key, use_subscription=False, use_local=False,
            local_model="phi4-mini", local_host=None, local_context_tokens=32768, rebuild=False):

    if campaign_dir is None:
        print("Please provide a campaign directory.")
        return

    print()
    print("--------------------")
    print("STORIFY")
    print("--------------------")
    print()

    sessions = find_sessions(campaign_dir)
    if not sessions:
        print(f"  No session subfolders containing transcript.txt were found under {campaign_dir}.")
        print("  storify expects a campaign folder whose subfolders each hold a transcript.txt")
        print("  (run assemble on each session first).")
        return

    if rebuild:
        print("  --rebuild: regenerating the whole story from scratch.")
        state = {"sessions": []}
        story_so_far = ""
    else:
        state = _load_state(campaign_dir)
        story_so_far = _load_story(campaign_dir)

    processed = set(state.get("sessions", []))
    pending = [(name, path) for (name, path) in sessions if name not in processed]

    if not pending:
        print(f"  Story is already up to date ({len(processed)} session(s) incorporated).")
        print(f"  Pass --rebuild (or delete {STATE_FILE}) to regenerate.")
        return

    print(f"  {len(sessions)} session(s) found; {len(pending)} new to incorporate:")
    for name, _ in pending:
        print(f"   - {name}")
    print()

    client = None
    if use_local:
        pass
    elif use_subscription:
        print("  Using your Claude subscription (via the Claude Agent SDK).")
    else:
        if not anthropic_api_key:
            print("  An Anthropic API key is required (or pass --useSubscription / --useLocal).")
            sys.exit(1)
        client = backends.make_api_client(anthropic_api_key)

    story_path = os.path.join(campaign_dir, STORY_FILE)

    for name, path in pending:
        print(f"  - Session '{name}'...")
        with open(os.path.join(path, 'transcript.txt'), 'r') as f:
            transcript = f.read()

        user_content = build_prompt(story_so_far, name, transcript)

        # A failure mid-campaign shouldn't discard chapters already written;
        # each successful session is persisted before moving to the next.
        try:
            chapter = _generate_chapter(user_content, client, use_subscription, use_local,
                                        local_model, local_host, local_context_tokens)
        except Exception as ex:
            print(f"    ERROR: failed to generate a chapter for '{name}': {ex}")
            print("    Stopping here. Sessions completed so far have been saved;")
            print("    re-run to resume from this session.")
            break

        chapter = chapter.strip()
        story_so_far = (story_so_far.rstrip() + "\n\n" + chapter + "\n") if story_so_far.strip() else (chapter + "\n")
        with open(story_path, 'w') as f:
            f.write(story_so_far)

        state.setdefault("sessions", []).append(name)
        _save_state(campaign_dir, state)

        print(f"    Chapter added -- story now covers {len(state['sessions'])} session(s).")
        print(f"    Written to {story_path}")
        print()

    print("--------------------")
