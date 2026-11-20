# How each harness compacts

Every sample ships this file as `harness_compaction.md`. It describes, for each harness,
when compaction fires, what the compactor model receives, what is kept back from it, and
what the harness does with its reply. It names the parts of the conversation that are
sent, not their text. The sample's own harness is `harness` in `task.toml`, and how its
compaction fired is `compaction_trigger` there.

Each golden point's `gNN_before_compaction.jsonl` is the harness's own log up to that point.
It is cumulative: from round 2 on it also holds every earlier round, which this round's
compactor did not see again. Each harness section below says where in the file this round's
compactor input starts and where it ends. Do not read the whole file as the compactor's
input. In the part of the file the compactor read, each tool output is shown as the
compactor received it, cut where the harness cuts it. This round's kept tail, which the
compactor did not read, is shown in full, as the continuation keeps it. The full outputs
are in `gNN_session.tar.gz`. A natural run's `cNN_before_compaction.jsonl` is built the same
way.

Harness versions: Claude Code 2.1.278, Codex 0.155.1, Pi 0.86.1, OpenCode 1.18.30.

## Limits on a run

Every run (golden rounds, natural runs, baselines) has one limit: its task's own `[agent]
timeout_sec` in `task.toml` (5400 seconds on most bundles, 3000 on some), passed to the worker
explicitly. A task that states none gets two hours. No harness is given a turn or step cap.

## When compaction fires

`compaction_trigger` in `task.toml` is `harness_default`: each harness is told only the
window and fires at its own default, as it would in production. Each also keeps back what it
keeps in production: OpenCode keeps its own verbatim tail of recent turns (see OpenCode
below). Every golden round, natural run and re-cut of a sample fires this way.

Every run is told its window in base-10, on every harness and with every model: a 96K run is
told 96,000 tokens, a 128K run 128,000 and a 256K run 256,000. Claude Code runs no window
below its own 100,000 floor, so its bundles have no 64K or 96K window (since 2026-11-10; a 96K
run used to be given 100,000) and start at 128K. The solver and the compactor are told the same count. `golden_window_tokens` in `task.toml` gives each window's count, and
each run's `run.json` gives its own as `context_window`.

| Harness | Fires at | Settings passed |
|---|---|---|
| Claude Code | window less 33,000 (its output reserve, 20,000, and buffer, 13,000). Claude Code's smallest compaction window is 100,000, so it runs no window below that: there are no 64K or 96K Claude Code windows, and a Claude Code bundle starts at 128K. | `auto_compact_window` = the window, or 100,000 |
| Codex | nine tenths of the window | `model_context_window` = the window |
| Pi | the window less 16,384 (Pi's `reserveTokens`) | the model's context window = the window |
| OpenCode | the window less 32,000, its output cap per request (`min(limit.output, 32000)`), as a stock install fires for these models | `limit.context` = the window, `limit.output` = 64,000; no `limit.input` |

OpenCode's model entries take the shape of the solver's stock catalog entry. Kimi K3, GLM-5.3
and Claude Opus 5 have no `limit.input` there, so OpenCode fires at `limit.context` less the
request's output cap, as a stock install does. A GPT solver's stock entry sets `limit.input`;
there OpenCode would fire at the window less `min(20000, output cap)`. GPT is only a compactor
in this benchmark, and the trigger follows the solver. The compactor is given the solver's
limits, so it never moves the trigger or the kept tail. Samples cut before 2026-11-10 were
given `limit.input` equal to the window and fired at the window less 20,000; their golden
rounds' trigger metadata lacks `opencode_limit`.

OpenCode's `tail_turns` and `preserve_recent_tokens` are not set, so it keeps its own tail.

Baselines run with automatic compaction off.

## What the compactor receives

In each harness the compaction request goes to the cell's compactor model. Where the
compactor is not the solver, it is the harness's own request with the compactor named as
the model: Claude Code's and Codex's requests pass through a proxy that changes only the
model (and, for an OpenAI compactor, drops another server's encrypted reasoning); Pi calls
its own compaction with the compactor; OpenCode names it as its compaction model.

### Claude Code

- **Instruction**: Claude Code's own compaction prompt, as a user turn after the conversation.
- **System prompt and tools**: the agent's own (tool use is denied for the request).
- **Conversation**: every message since the previous compaction except the last API round.
  The previous summary, when there is one, opens it as a user turn, followed by the API
  round the previous compaction kept back.
- **Where it is in `gNN_before_compaction.jsonl`**: in the first round, from the top of the
  file. In a later round, from the file's last `compact_boundary` record: the previous
  summary is the first line after it marked `isCompactSummary`. The input also includes the lines
  that record names in `compactMetadata.preservedMessages`. Those lines sit just before the
  record. They are the API round the previous compaction kept back, which the agent carried
  on with after the summary. The input ends before the file's last API round (see Kept
  back).
- **Reasoning**: included. **Tool calls and results**: in full, as the file shows them.
- **Kept back**: the last API round (the final assistant message and its tool results). It
  stays verbatim after the summary for the continuation and the compactor does not see it.
  In `gNN_before_compaction.jsonl` it is the last API round of the file.
- **Output cap**: the solver model's default output cap.
- **Reply**: Claude Code drops the `<analysis>` block, unwraps the `<summary>`, and puts its
  "This session is being continued…" header in front.

### Codex

- **Instruction**: Codex's own compaction prompt, as a user turn after the conversation.
- **System prompt**: the agent's own. **Tools**: none.
- **Conversation**: the entire current history, including the previous summary as a user turn.
- **Where it is in `gNN_before_compaction.jsonl`**: in the first round, the whole file. In a
  later round, from the file's last `compacted` record to the end. That record holds the
  previous summary, which Codex carried on from together with the user messages it
  re-added. The lines before it are earlier rounds, which Codex replaced with that summary.
- **Reasoning**: included. **Tool results**: as held in history, after Codex's own
  truncation. The file shows them the same way. A failed or rejected `exec_command`'s
  message longer than 900 bytes is cut in the middle to at most 900 bytes, with
  `…N chars truncated…` and no warning header.
- **Kept back**: nothing. Codex re-adds the user's messages (up to 20,000 tokens) after the
  summary; the compactor saw them too.
- **Output cap**: none is sent.
- **Reply**: Codex puts its fixed handoff prefix in front of the summary.

### Pi

- **Instruction**: Pi's own compaction prompt as the system prompt; its update prompt when a
  previous summary exists. The agent's own system prompt is not sent. **Tools**: none.
- **Conversation**: the conversation since the previous compaction's first kept entry,
  serialized as one user turn, with the previous summary. Entries kept after one compaction
  are summarized by the next. When the cut falls inside a turn that a user message started,
  Pi also summarizes that turn's opening separately and adds it under **Turn Context (split
  turn)**. A round that resumed from a golden starts with a short resume line from the
  benchmark (such as "Continue the task from the compaction checkpoint."), which the
  compactor never receives, and which does not start a turn: as in a run that never
  stopped, the compactor gets one request for the whole conversation since the previous
  compaction, and the summary has no split-turn section on that account.
- **Where it is in `gNN_before_compaction.jsonl`**: in the first round, from the top of the
  file. In a later round, from the line whose `id` is the `firstKeptEntryId` of the file's
  last `compaction` record. That line sits before the record. The previous summary is the
  record's `summary`. The input ends where this round's kept-back entries start (see Kept
  back).
- **Reasoning**: included. **Tool results**: each one longer than 2,000 characters is cut
  to its first 2,000, and `[... N more characters truncated]` is added after it, N being
  the number of characters cut. The file shows every tool result the compactor read cut
  this way. The entries kept back are shown in full, as the continuation keeps them.
- **Kept back**: the most recent ~20,000 tokens, from the compaction's `firstKeptEntryId`.
  They stay verbatim for the continuation. In `gNN_before_compaction.jsonl` they are the
  lines from that entry on.
- **Output cap**: 80% of `reserveTokens` (about 13,100 tokens at `harness_default`) or the
  model's own cap, whichever is lower.
- **Reply**: Pi appends `<read-files>` and `<modified-files>` lists to the model's text.
  Every delivered Pi `gNN_compaction.md` or `cNN_compaction.md` (golden, re-cut or
  natural run) holds the model's text, and the lists Pi appended to it are beside it in
  `gNN_file_lists.md` or `cNN_file_lists.md`.
- **Length limits**: Length limits count the summary Pi's compactor model writes. Pi
  appends a list of the files read and modified after it; that list is the same for every
  compactor at a point and is not counted.

### OpenCode

- **Instruction**: OpenCode's compaction prompt and summary template, as a user turn after
  the conversation. The system prompt is OpenCode's compaction agent prompt only; the
  agent's own is not sent. **Tools**: none.
- **Conversation**: every message of the agent's own session since the previous compaction
  up to the kept tail, serialized, with the previous summary. A tail kept at one compaction
  is summarized by the next, since the model carried on with it after the summary. A
  subagent the agent starts (such as `explore`) runs in a session of its own, which is not
  sent; its result reaches the compactor as the result of the agent's `task` tool call. The
  file holds the agent's own session only.
- **Where it is in `gNN_before_compaction.jsonl`**: in the first round, from the top of the
  file. In a later round, from the file's last compaction marker, a user line with a
  `compaction` part. The previous summary is the assistant line after it marked
  `"summary": true`. Where that marker records a `tail_start_id`, the input also includes
  the tail the previous compaction kept: the lines from that message up to the marker. The
  input ends where this round's kept tail starts (see Kept back).
- **Reasoning**: included. **Tool results**: each completed tool's output, with a line
  naming each attached file after it, is cut to its first 2,000 characters when it is
  longer, and a line `[truncated]` is added after it. An output OpenCode had already
  pruned is sent as `[Old tool result content cleared]`. A failed call's error is sent in
  full. The file shows every tool output the compactor read this way. The kept tail is
  shown in full, as the continuation keeps it.
- **Kept back**: OpenCode's own tail, the most recent turns up to a
  budget of a quarter of its usable context (the window less the output cap), held between
  2,000 and 15,000 estimated tokens: about 8,000 at 64K and 15,000 from 96K up. Whole
  turns are kept newest first, and the turn that does not fit is split, so the tail usually
  starts partway through the agent's current turn. The compaction request records its first
  message as `tail_start_id`; a compaction that kept nothing records none. The tail stays
  verbatim after the summary for the continuation and the compactor does not see it. In
  `gNN_before_compaction.jsonl` it is the last lines of the file, from that message on;
  the compactor's input ends at the line before it.
- **Output cap**: OpenCode's own step cap, 32,000 tokens. The same cap applies to every
  step of the run.
- **Reply**: stored as the summary message as written.

## Re-cuts

A re-cut in `compactions/` replays one golden compaction point with another compactor under
the same harness. An open-model re-cut ships its summary (`cNN_compaction.md`), `cNN_run.json`
and `cNN_score.json`, plus `cNN_prompt.md` with the exact prompt the compactor received when
the replay recorded it; a closed-model re-cut ships only its `cNN_score.json`. A round that
resumed from a golden started with a short resume line from the
benchmark (such as "Continue the task from the compaction checkpoint."), which no compactor
receives: it is removed before a re-cut, as it was from the golden's own compaction.
An OpenCode re-cut runs with its sample's tail settings, so at `harness_default` it keeps a
tail from the same messages and sends its compactor only what comes before it.
