# TASMAS (*Transcribe And Summarize Multiple Audio Stems*)

This is an automatic interleaving transcriber and summarizer for file-per-speaker audio recordings, such as Discord calls recorded by [`Craig`](https://craig.chat/) or a similar bot.

You point it at a folder that contains audio files,  
![image](https://github.com/KaddaOK/TASMAS/assets/151568451/1ce0e427-9670-4d2a-a877-d1175cd2c8d9)  
and it will generate transcripts of each file timestamped at the word level,  
![image](https://github.com/KaddaOK/TASMAS/assets/151568451/77d2e0b8-96bf-4b16-8c91-23f43e16d0bb)![image](https://github.com/KaddaOK/TASMAS/assets/151568451/3b5bf487-4a72-45e6-b5a9-b6fd784e0a16)  
then braid each phrase from the files into a single coherent attributed transcript, 
 ![image](https://github.com/KaddaOK/TASMAS/assets/151568451/d4add246-f1dc-4c9b-b098-c48ea3100cbb)  
and optionally get summaries of that transcript as well.
 ![image](https://github.com/KaddaOK/TASMAS/assets/151568451/38d00f66-5400-42ec-a9c0-756766a2afee)  
 (Okay yes that's not a "real" automatic summary output, but you get the point, I just wanted to highlight how the transcript looks when people are talking over each other)


# Operating Modes
TASMAS has 3 operating modes, each of which can be executed independently,  
as well as a `SEMIAUTO` mode which executes the first two modes in sequence (this is the recommended initial run),  
and a `FULLAUTO` mode which executes all 3 (not recommended, as manual fix-up after stage 2 is usually a good idea).

## `RECOGNIZE`:

*Given a file path that contains a number of separate audio files, 
transcribe each file down to word-level timestamps, saving each as `{filename}.words.json`.*

### File formats
As designed and tested, this operates on `.ogg` files recorded using the [`Craig`](https://craig.chat/) bot for Discord, but it could theoretically be any audio file that `whisper` can handle if you specify the `--extension` switch.

### Models and options
This mode uses `whisper_timestamped` to transcribe the files, using the `small` model, with disfluency detection enabled and the Auditok VAD mode, and using the beam and temp etc parameters described as "accurate".

(As of right now there's a configuration switch `--fast` which causes it to use the `"tiny"` model instead and not use the "accurate" parameters, but honestly it's not usable and I'm going to just take it out entirely in a subsequent release.)

Personally I didn't get any more meaningful results out of using larger models, and in fact `small` seemed to work the best anyway, so I didn't follow through on model selection options.

## `ASSEMBLE`:

*Given a file path that contains a bunch of separate `.words.json` files, sort and interleave these into one coherent human-readable transcript, saved as `transcript.txt`.*

### Speaker Identification
As TASMAS is intended for recordings that have a separate file for each different speaker, the filename is used to identify the speaker.  

After any formatting idiomatic to `Craig` (a leading `n-` and trailing `_0`) is stripped out, the rest will be compared to the contents of `--names` if specified, or used directly as the speaker name if nothing is found. (See below under Usage)  

If a `names.json` file is found in the input path or its containing folder, it will be used for `--names` automatically, allowing you to set up this information once and have it be continually re-used for other recordings with the same speakers.

TASMAS will also interrogate the user during the PRE-CHECK phase to verify any speakers it encounters whose names were not specified by `--names` or a `names.json`.

### Punctuation-based Interleaving
TASMAS sorts all the words by timestamp and assembles sentences sequentially, only allowing the current speaker to change when a word ends with a punctuation mark (`.`, `,`, `!`, `?`, `-`).  
This allows cross-talk to be inserted in as accurate and followable an order as possible without each word being split up. 

Note that this is therefore only possible when all of the audio files are synchronized to start at the same moment, even if that speaker was not yet present.  `Craig` does this automatically, but if your source does not, you may need to edit your audio files accordingly.

### Anticipate Corrections/Replacements
TASMAS will replace words and phrases that are likely mishears in the output if `--corrections` data is provided.  (See below under Usage)  
This is particularly useful for TTRPG recordings, as many proper names and phrases will never be interpreted correctly.  
As with names, TASMAS will automatically pick up a `corrections.json` file if present in the input path or its parent folder, so you can build up these replacements over time.

### Out-of-sync Warning
At the end of this operation, TASMAS will detect any phrases with start times that are more than 5 seconds out of sync with their neighbors, and will automatically run them through a punctuation model to try to improve results (as adding punctuation will allow these phrases to split at those words, which may allow other speakers to interject improving the overall sync).  
After doing so, remaining phrases that are still more than 5 seconds out of sync will be output to the screen and to `outOfSyncItems.txt`.  
Manually adding a punctuation mark directly to an individual word in the corresponding `.words.json` file and re-executing the ASSEMBLE operation will improve these results.


## `SUMMARIZE`:
 
*Given an Anthropic API key, appropriate prompts, and a file path that contains a `transcript.txt`, ask Claude to summarize the transcript.*

### Summary Prompts
When executing the SUMMARIZE operation, `--promptType` is required, which will be used to attempt to locate text files in a `prompts/{promptType}/*.txt` folder, in the input path, its parent folder, or with TASMAS itself. (The older flat `prompt_{promptType}_*.txt` naming is still supported as a fallback if no `prompts/{promptType}/` folder is found, so any custom prompt files you already have keep working.)

TASMAS ships with prompt sets for a few systems, each tuned to what that system actually tracks:
 - `--promptType generic`: system-agnostic, works for any tabletop RPG.
 - `--promptType dnd`: Dungeons & Dragons (HP, inventory, quest progress, DM/NPC dialogue).
 - `--promptType coc`: Call of Cthulhu (Sanity, Mythos knowledge, clues, phobias/manias).
 - `--promptType blades`: Blades in the Dark (Stress/Trauma, Heat, Coin, Scores, Entanglements).
 - `--promptType mutant`: Mutant – Undergångens Arvtagare (Swedish post-apocalyptic RPG; kp/kritisk/dödlig skada, strålning/zonröta, mutationer & psi-mutationer/resonans, rykte, fynd/pålitlighet). Expects a Swedish-language transcript and writes the summary in Swedish. See `prompts/mutant/rules_reference.md` for the terminology this prompt set was built from.

To add support for another system, add a `prompts/{yourSystem}/` folder (in your recordings folder, its parent, or alongside TASMAS itself) containing one or more `.txt` prompt files written the same way as the built-in ones.

Also, `--anthropicApiKey` is required in this mode, because:

### Why does summarize need to call a paid API?
For each prompt file found, the Claude API is called (model `claude-opus-4-8`), which handles the full length of a typical D&D session transcript (usually 30,000-60,000 tokens) in a single call.  
So yes, it's not free, but it's usage-based and typically inexpensive per prompt.  
(And you don't ever have to use the SUMMARIZE workload at all if you don't want anyway. 😁)

### Using your Claude subscription instead of an API key
If you already pay for Claude Pro, Max, or Team, you can use that instead of paying per-token: pass `--useSubscription` in place of `--anthropicApiKey`. This routes the summarize call through the Claude Agent SDK, authenticated the same way Claude Code is (subscription usage, not metered API billing) — subject to your subscription's usage limits rather than a per-token cost.

Requires:
1. `pip install claude-agent-sdk`
2. The Claude Code CLI installed and logged in — run `claude setup-token` once (or just be logged in via `claude login`).

```bash
tasmas summarize /mnt/c/recordings/2024-04-04 --promptType dnd --useSubscription
```

### Using a local model instead (no cloud, no cost)
Pass `--useLocal` to summarize with a locally-running [Ollama](https://ollama.com) model instead of the Claude API or your subscription — nothing leaves your machine, and there's no per-call cost.

Requires:
1. `pip install ollama`
2. A local Ollama server running (`ollama serve`) with the model already pulled (e.g. `ollama pull phi4-mini`)

```bash
tasmas summarize /mnt/c/recordings/2024-04-04 --promptType dnd --useLocal
```

By default this uses the `phi4-mini` model (128K context window, ~2.5GB, small enough to run on CPU). Ollama itself defaults to a much smaller context window regardless of what the model supports (often just 4096 tokens — check what yours reports on startup), and **silently truncates** input that doesn't fit rather than erroring, so TASMAS explicitly requests a larger one via `--localContextTokens` (default `32768`). D&D session transcripts typically run 30,000-60,000 tokens, so:
 - Raise `--localContextTokens` if you have the RAM for it (context cache size scales with this value — on a CPU-only or memory-constrained machine, this is the main thing that can go wrong; TASMAS will print a warning if your transcript looks like it's close to or over the configured window).
 - Use `--localModel` to pick a different Ollama model, provided it's already pulled and supports enough context for your transcript.
 - Use `--localHost` if your Ollama server isn't at the default `http://127.0.0.1:11434`.

Expect this to be noticeably slower than the API or subscription paths, especially on CPU-only hardware — there's no timeout, but a 30-60K token summarization pass can take a while.

# Usage

To run TASMAS, you must provide at minimum:
 1. an operation mode (`recognize`, `assemble`, `summarize`, `semiauto` which does the first 2, or `fullauto` which does all 3) and 
 2. a folder path to process.
```bash
tasmas semiauto /mnt/c/recordings/2024-04-04
```
If your recordings aren't in `.ogg` (and to be fair, why would they be, unless you were using `Craig`, but that's the use case I wrote this for so it's the default), you'll have to add `--extension "wav"` or whatever they are.  
I haven't even tested that, I just assume it works; if not plz open a bug 🤣

But yeah, here are some additional things you can add:

### Names
Specifying a `--names` value allows you to set how the filenames should translate into speaker names in the transcript.  
It can either be a path to a `.json` file, or the JSON itself inline if you're feeling like making things harder for yourself.    
For example, to produce the transcript from our example at the top, this might be the contents of a `names.json` file:
```json
{
	"JohnTheJester": "John",
	"EmiLovesCats": "Emily",
	"RoboBert": "Robert",
	"JessInWonderland": "Jessica",
	"SassySarah": "Sarah"
}
```
We could pass that to tasmas like this:
```bash
tasmas --names /mnt/c/recordings/names.json semiauto /mnt/c/recordings/2024-04-04
```
but in this case we don't even have to specify `--names`, because that `names.json` is in the parent folder of the folder we're processing, so if we say nothing about names it'll pick it up automatically.
![image](https://github.com/KaddaOK/TASMAS/assets/151568451/7bc9cedc-8605-492b-a20e-d059380559f7)

If you run TASMAS without any names input, it'll prompt you for the name for each speaker file it detects.  (I'm realizing as I'm writing this that it'd be a good feature to ask you after doing so if you want to save a `names.json` for future use, so I'll add that to the backlog I guess.)  
It also gives you the option to skip a speaker entirely, which is useful for files that are music bots or whatnot.  (Don't specify speaker names for such files, or you won't be prompted if you'd like to skip them!)
![image](https://github.com/KaddaOK/TASMAS/assets/151568451/0ae8c997-16cf-4a32-b8d3-9807af20f407)

### Corrections
Specifying a `--corrections` value allows you to replace all the occurrences of a word or phrase that you know is an incorrect interpretation with the correct value.  

Similarly to `names`, this can either be a path to a `.json` file, or the JSON itself inline.  

However, the format is the opposite:  
instead of the `"wrongValue":"correctValue"` of names,  
corrections are presented  
`"correctValue": ["wrongValue", "wrongValue", wrongValue"]`  
in order to allow you to list many incorrect possibilities for a single correct possibility.  

For example, here's just a few items from a real `corrections.json` file I use, in which you can see why it needs to be done this way: because of weird made up names that get interpreted in many random ways.
```json
{
	"Dagstorp": [
		"Dexter",
		"Digstorpe",
		"Dagster",
		"Dagstrup",
		"Dagsorp",
		"Dag Swarp"
	],
	"Elsalor": [
		"El Soler",
		"El Solor",
		"Else Laura",
		"else the Lord",
		"I'll solar"
	],
	"Jeltra": [
		"Gelter",
		"Delta",
		"Geltro",
		"Gelja",
		"Jeldra",
		"Jelter"
	]
}
```
Anyway, yeah. They don't have to be a single word to replace, either, you could put anything you want in those quotes; another real world example is `"Shield of Faith": ["shield a faith"]`, which had the added bonus of capitalizing that spell name (corrections are case-insensitive for detection, but will insert the replacement value as capitalized).

### Other stuff
There are some other finer-tuning options, but they're pretty well-summarized in the actual software if you do `tasmas --help`.  
You won't generally need to mess with them (other than `--showTimestamps`, which pretty self-explanatorily includes timestamps in the `transcript.txt` output), unless you feel like `assemble`ing numerous transcripts and comparing them line by line to see how they differ.  As with all things, YMMV.


# Installation

### Docker
Maybe the easiest, or at least most foolproof, way to use TASMAS (especially on Windows, which always seems to make a mess of python stuff) is via [`Docker`](https://www.docker.com/), which creates a lightweight virtual container with everything already set up for you. 

A TASMAS image is available on Docker Hub tagged `kaddaok/tasmas`,  
or the `dockerfile` is a part of this repo if you want to build the image yourself.  

You just want to make sure that you include `--gpus all`, so that the model can use your GPU if present,  
and that you map something as a volume (easiest way is `-v {src}:{dest}` ) so you have access to what you want to process.    

For instance, I put all the recordings I need to transcribe on my N: drive,  
and my docker is running in linux so I can access N: from `/mnt/n` in my docker host, and I'll just put it in the same place in the container's file system,  
so my docker command looks like this:
```bash
docker run -it -v /mnt/n:/mnt/n --gpus all kaddaok/tasmas:latest
```
Running that gives me a new prompt at `/usr/src/tasmas` in the running container and I can just say `tasmas` straight from there:
```bash
tasmas semiauto /mnt/n/dnd/icespire/2024-03-17
```
and when I'm done using the Docker container, I just type 
```bash
exit
```
and I'm back at the regular prompt.

### Python
If you're already comfortable with python environments (or optimistically think that it might be easier than setting up docker), you can just run it directly.   

I haven't put this on PyPI yet (and probably need to reorganize it a bit in order to do so) which means you can't yet just say `pip install tasmas`. ❌   

What you can do, though, is clone or download the contents of this repo, cd to it and then say `pip install . `.  That should allow you to use the `tasmas` command.  

You can also just say `python tasmas.py` instead though, if you feel like it.

#### Python Requirements and Setup
TASMAS requires **Python 3.11** and several dependencies. Here's how to set it up:

1. **Ensure Python 3.11 is installed** on your system
2. **Create a virtual environment** (recommended):
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install TASMAS**:
   ```bash
   pip install .
   ```
5. **Run TASMAS**:
   ```bash
   tasmas semiauto /path/to/your/recordings
   ```

**Note**: If you prefer not to install TASMAS as a package, you can run it directly with:
```bash
python tasmas.py semiauto /path/to/your/recordings
```