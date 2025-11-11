# "The Agent Cube" - FINAL Session Flow

**Duration:** 60 minutes + Q&A  
**Format:** Quick Hook → Full Demo → Deep Explanation → Practical → Call to Action  

---

## **0:00-0:02 - THE HOOK** (30 seconds)

**You on camera, energetic:**

```
"Agent Cube.

Two AI coders compete.
Three judges pick the winner.

We shipped 15 features in 11 days for v2.
Zero bugs escaped.

Watch it plan its own web UI..."
```

**[Start screen share, slides visible]**

**Quick aside:**
```
"Oh, and these slides?
The Agent Cube built them.

I gave it session requirements.
Two writers proposed slide decks.
Three judges picked this structure.

You're experiencing the winner right now.

[Pause for reaction]

Let's see it build something else..."
```

**[Switch to terminal]**

---

## **0:02-0:15 - THE DEMO** (13 minutes)

**[Play Loom: Web UI Build]**

**Your light narration over video (fast-forwarded parts):**

**Launch (0:02-0:03):**
```
"Giving the agent requirements for a web UI..."
[Command runs]
```

**Prompter (0:03-0:04):**
```
"First, a Prompter agent reads the codebase..."
[Thinking box appears]
```

**Writers Launch (0:04-0:05):**
```
"Now two agents compete to create the best plan.
Writer A - Sonnet
Writer B - Codex"
[Dual thinking boxes appear]
```

**Writers Working (0:05-0:10 - SPEED UP 10X):**
```
"They're both creating planning docs and task breakdowns.
Different approaches emerging...
[Fast forward through most thinking]
Notice the different file structures.
Writer A: minimalist
Writer B: comprehensive"
```

**Judges (0:10-0:13 - SPEED UP 10X):**
```
"Three independent judges review both plans.
Checking completeness, feasibility, KISS compliance.
[Fast forward]
Decision coming..."
```

**Decision (0:13-0:14):**
```
"And the votes are in...
[cube decide shows]
Winner: [A/B] with score [X] vs [Y]"
```

**Result (0:14-0:15):**
```
"Complete architecture: planning/web-ui.md
Six task files: ready to execute
2,800 lines of planning
From requirements to executable plan: 30 minutes
Zero human planning time.

That's the Agent Cube."
```

**[Stop demo]**

---

## **0:15-0:20 - THE PLANNING PROCESS** (5 minutes)

**NOW explain what they just saw:**

**Slide: v2 Planning Structure**
```
planning/ (33 documents)
├── api-conventions.md
├── crud-factory.md
└── ...

Architecture-first, not feature-first
```

**Live:** Switch to v2 repo, show folders

**Explain:**
1. **Architecture meetings** (3hr) → Planning docs
2. **Orchestrator reads** planning → Proposes tasks
3. **Phases emerge** from dependency graph
4. **Iterative** - 85% accurate upfront, 15% evolves

**Key quote from your transcript:**
```
"Don't make anything up. Use only facts from repo."

This is the key. Agents read:
• 33 planning docs
• Existing code
• Proven patterns

Then propose structured plans.
```

**Show one task file from result:**
- Point out planning doc references
- Owned paths
- Clear criteria

---

## **0:20-0:25 - THE SCIENCE** (5 minutes)

**Slide: Research-Backed**

**Quick hits:**
1. Best-of-N (Anthropic) - 35% error reduction
2. LLM-as-Judge - 85% human agreement
3. Self-Refine loops - Iterative improvement
4. Multi-model ensembles - Diversity wins
5. Cursor 2.0 - Direct inspiration

**Quote:** "Not experimental. Research-backed and battle-tested."

---

## **0:25-0:27 - GIT WORKTREES** (2 minutes)

**Slide: Architecture Foundation**

```
How 18 agents run without conflicts:

Main: /aetheron-connect-v2
├── Writer A: ~/.cube/worktrees/.../writer-sonnet-task/
├── Writer B: ~/.cube/worktrees/.../writer-codex-task/
└── 6 more for other tasks

Each: Own branch, own files, own git state
Result: Zero conflicts!
```

**Live:** Show terminal, `git worktree list`

---

## **0:27-0:32 - THE 3-SPLIT** (5 minutes)

**Slide: Maximum Parallelization**

**Show screenshot of 3-split terminal:**
```
Task 1: 04-exemplar (6 agents)
Task 2: 05-feature-flags (6 agents)
Task 3: 05-rate-limit (6 agents)

18 agents simultaneously
0 conflicts
0 human time
```

**Quote:** "Building 3 features at once ⚡🔥"

---

## **0:32-0:42 - V2 RESULTS** (10 minutes)

**Slide: Model Performance**
- Sonnet: 100% frontend wins
- Codex: 88% backend wins
- Task-model matching matters!

**Slide: Synthesis Power**
- 40% of tasks improved
- Best of both worlds
- Examples

**Slide: The Human Catch**
```
API Client Task:
Panel: 3/3 APPROVED ✅
Peer: 3/3 APPROVED ✅
Human: REJECTED ❌

All judges missed: Wrong architecture

Lesson: AI assistance, not replacement
```

**Slide: Audit Trail**
- Everything preserved
- Data goldmine
- Learning compounds

---

## **0:42-0:52 - PRACTICAL USE** (10 minutes)

**Slide: The 5 Commands**
```bash
cube auto task.md          # Autonomous workflow
cube status task           # Check progress
cube decide task           # See decisions
cube resume agent task msg # Intervene
cube clean task            # Cleanup
```

**Live terminal demo:** Show quick commands

**Slide: Config File**
- Show `python/cube.yaml`
- Customize any model
- Pluggable architecture

**Slide: When to Use**
- ✅ Good for: New features, refactoring, complex bugs
- ❌ Not for: Tiny changes, emergencies, experiments

---

## **0:52-0:57 - THE FUTURE** (5 minutes)

**Slide: Roadmap**
```
This Week: Web UI (you just saw it planned!)
This Month: Integration tests, more CLIs
This Quarter: Learning system, cost tracking

Limitations (honest):
• Gemini quirks
• Setup requires cursor-agent
• Judge decision filing (improving!)
```

**Slide: The Ask**
```
1. Try ONE task this week
2. Raise GitHub issues (Cube fixes them!)
3. Slack me feedback

github.com/aetheronhq/agent-cube
```

---

## **0:57-1:00 - CLOSE & Q&A SETUP** (3 minutes)

**Wrap up:**
```
"The Agent Cube isn't just a tool.
It's a new way of building software.

Competitive development.
Judicial review.
Continuous synthesis.

It works. V2 proves it.

Your turn to try it.

Questions?"
```

**[Open for Q&A - can extend past 1:00]**

---

## 🎯 **WHY QUICK CONTEXT → DEMO WORKS**

**Hook in 30 seconds:**
- Gets attention FAST
- Visual within 2 minutes
- Can't look away

**Demo while fresh:**
- Attention span highest at start
- Action is more engaging than talking
- Creates questions (answered later)

**Explain after investment:**
- They've seen it work (credible!)
- They want to know how (motivated!)
- Deep dive lands better (context established)

**Ends with action:**
- Commands (they can use!)
- Config (they can customize!)
- Terminal demo (hands-on!)

---

## ⚡ **TIMING PERFECT**

```
Hook:       0.5min  (attention!)
Demo:      13min    (amaze!)
Planning:   5min    (understand!)
Science:    5min    (believe!)
Worktrees:  2min    (foundation!)
3-Split:    5min    (wow!)
Results:   10min    (proof!)
Practical: 10min    (use!)
Future:     5min    (roadmap!)
Close:      3min    (ask!)
────────────────
Total:     58.5min
Buffer:     1.5min
```

**Perfect pacing!**

---

## 🎬 **THE OPENING (EXACTLY)**

**On camera, energetic, 30 seconds:**

```
"Good morning!

[Pause]

Agent Cube.

Two AI developers compete on the same task.
Three AI judges pick the best solution.
We used this to build Aetheron Connect v2.

15 production features.
11 days.
Zero bugs escaped.

Today, I'm going to show you how it works.

Watch the Cube plan its own web UI..."

[Screen share, terminal visible]
[Start demo]
```

**That's it. Hook set. Demo rolls.**

---

## ✅ **LOCKED IN!**

**This is the format:**
1. Ultra-fast context (30sec)
2. Full demo with narration (13min)
3. Deep explanations (planning, science, results)
4. Practical how-to
5. Future + ask

**Start with action. Explain with context. End with adoption.**

**This will CRUSH!** 🚀🔥

Updating all plans now...

<function_calls>
<invoke name="run_terminal_cmd">
<parameter name="command">cd /Users/jacob/dev/agent-cube && git add -A && git commit -m "docs: FINAL session flow - Quick Hook → Demo → Deep Explanation

LOCKED IN APPROACH:
- 0:00-0:02 Ultra-fast hook (30sec)
- 0:02-0:15 Full demo with light narration (13min)
- 0:15-0:60 Deep explanations, practical, future

Why this works:
- Hook in 30 seconds (attention!)
- Demo while fresh (visual engagement)
- Explain after investment (they want to know!)
- End with action (commands, config, try it!)

Perfect pacing: 58.5min with 1.5min buffer

Updated SESSION_OUTLINE_FINAL.md with exact flow
Includes opening script, narration cues, timing

READY FOR TUESDAY RECORDING!" && git push origin main
