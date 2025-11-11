# Slide Deck Outline - "The Agent Cube"

**15 slides, 60 minutes**

---

## **SLIDES 1-5: THE STORY (0:00-0:10)**

### **Slide 1: Title**
```
THE AGENT CUBE
Resistance is Futile

[Borg cube image or abstract 3D cube]

Jacob Ellis
Dev Forum Special Edition
```

### **Slide 2: The Hook**
```
WE SHIPPED 15 FEATURES IN 11 DAYS

~10,000 lines of production code
Zero bugs escaped
How? Not faster. Smarter.
```

### **Slide 3: The Metrics**
```
AETHERON CONNECT V2
Built with Agent Cube

📊 15 features completed
⚡ 11 days (Oct 31 - Nov 11)
📝 ~10k lines of code
🤖 19 AI agents (1 orchestrator, 6 writers, 9 judges, 3 prompters)
🔀 40% synthesis rate (best of both)
✅ 27% unanimous decisions
🐛 0 production bugs escaped
```

### **Slide 4: Agents³ = Cube**
```
THE NAME

Agents → Orchestrator plans workflow
  Agents → Writers implement (2 competing)
    Agents → Judges review (3 independent)

Agents³ = Cube

[3D layered cube visual]
```

### **Slide 5: The F1 Analogy**
```
F1 TEAM APPROACH TO CODING

F1 Racing                     Agent Cube
────────────                  ──────────
2 drivers (competition)   →   2 AI writers
Telemetry analysis        →   3 AI judges  
Best strategy wins        →   Best code merges

Competition drives quality
```

---

## **SLIDES 6-8: THE PLANNING (0:10-0:20)**

### **Slide 6: Planning Structure**
```
ARCHITECTURE-FIRST PLANNING

planning/
├── api-conventions.md      (errors, pagination, headers)
├── crud-factory.md         (resource patterns)
├── db-conventions.md       (schemas, IDs, RLS)
├── rbac.md                 (roles, permissions)
└── ...33 documents total

Inspired by OpenSpec.dev
Format-agnostic (any structure works!)
```

### **Slide 7: From Planning to Tasks**
```
THE FLOW

1. Architecture meetings (3hr) → Miro boards
2. Create planning docs (1-2 days)
3. Orchestrator reads & proposes tasks
4. Human reviews & refines
5. Implementation begins
6. Plans evolve as we learn (Agile!)

[Flowchart with feedback loop]
```

### **Slide 8: Phases Emerge**
```
PHASES DISCOVERED, NOT DICTATED

Started: "Need auth, CRUD, SDK"

Orchestrator analyzed dependencies:
→ Phase 00: Scaffold
→ Phase 01: Foundation  
→ Phase 02: Core (9 tasks in parallel!)
→ Phase 03: Contracts
→ ...Phases 05-10 emerged organically

Result: 10 phases, 60+ tasks, optimal parallelization
```

---

## **SLIDE 9: THE SCIENCE (0:20-0:25)**

### **Slide 9: Research-Backed**
```
THE SCIENCE BEHIND THE CUBE

1️⃣ Best-of-N Sampling
   Anthropic Constitutional AI (2022)
   N=2 → 35% error reduction

2️⃣ LLM-as-Judge
   Zheng et al. (2023)
   85% agreement with human reviewers

3️⃣ Self-Refine Loops
   Madaan et al. (2023)
   Iterative improvement through critique

4️⃣ Multi-Model Ensembles
   ML principle: Diversity reduces variance

5️⃣ Cursor 2.0 Multi-Agent
   Direct inspiration, proven approach

Not experimental - research-backed!
```

---

## **SLIDE 10: META MOMENT (0:25-0:26)**

### **Slide 10: Inception**
```
EVEN THIS SESSION WAS PLANNED BY THE CUBE

[Screenshot of terminal]
cube auto session-planning-task.md

Two AI writers proposed outlines
Three AI judges picked the best

[Loom video thumbnail]
Click to watch →
```

---

## **SLIDES 11-12: THE DEMO (0:26-0:41)**

### **Slide 11: Demo - Web UI Build**
```
LIVE DEMO
Building Agent Cube Web UI

Task: 01-project-scaffold
Goal: Vite + React + TypeScript foundation

[Video player embedded]

Watch: Dual writers → Judges → Synthesis → PR
Time-lapse: 30min → 5min
```

### **Slide 12: Key Demo Moments**
```
WHAT TO NOTICE

1. Different Approaches
   Sonnet: Minimalist config
   Codex: Full-featured setup

2. Judge Perspectives  
   Judge 1: Simplicity
   Judge 2: Completeness
   Judge 3: Production-readiness

3. Synthesis
   Best config + Best tests = Winner

Result: PR #123 ready to merge
```

---

## **SLIDES 13-14: RESULTS & USE (0:41-0:50)**

### **Slide 13: Model Performance**
```
TASK-MODEL MATCHING MATTERS

Sonnet 4.5 Wins:
✅ UI/Frontend (3-0 record)
✅ Documentation
✅ Simple solutions

Codex High Wins:
✅ Backend complexity
✅ Type-heavy code
✅ Security features
✅ Integration tests

Grok: Best judge
Fast + balanced + accurate

Insight: Match model to task type
```

### **Slide 14: The Audit Trail - Data Goldmine**
```
EVERYTHING IS PRESERVED

📊 Panel decisions (JSON)
   → Every vote, score, blocker

🔄 Peer reviews (JSON)
   → Iteration tracking

📝 Agent logs (~2MB each)
   → Every thought, every tool call

💾 Workflow state
   → Resume from any point

THE GOLDMINE

Analyze:
• Which models excel at what
• Quality trends over time
• Cost per feature
• Synthesis patterns

Learn:
• Improve prompts
• Better planning
• Model selection
• Pattern library

"Not just automation - institutional knowledge"

Storage: ~2MB per feature (tiny!)
Value: Compounding forever
```

### **Slide 15: The 5 Commands**
```
GETTING STARTED

# 1. Run autonomous workflow
cube auto task.md

# 2. Check progress
cube status 05-feature-flags

# 3. See decisions
cube decide 05-feature-flags

# 4. Intervene if needed
cube resume judge-2 task "message"

# 5. Clean up
cube clean task

[Cheat sheet QR code]
```

---

## **SLIDE 15: FUTURE & CALL TO ACTION (0:50-1:00)**

### **Slide 15: The Future**
```
WHAT'S NEXT

This Week:
✅ Web UI (watch it being built!)
✅ Integration tests
✅ More CLI adapters

This Month:
• Cost tracking
• Model comparison analytics
• Learning system (which model for what)
• Team collaboration

This Quarter:
• Direct API support (no CLI dependency)
• Auto-decision system
• Workflow templates
• SaaS offering?

YOUR TURN

1. Try ONE task this week
2. Raise GitHub issues (Cube fixes them!)
3. Slack me feedback anytime

github.com/aetheronhq/agent-cube
```

---

## **VISUAL STYLE**

**Color Scheme:**
- Background: Dark (#1a1a1a)
- Text: Light (#e0e0e0)
- Accent: Cyan/Electric blue (#00d9ff)
- Code: Monospace, syntax highlighted

**Fonts:**
- Heading: SF Pro Display Bold
- Body: SF Pro Text
- Code: JetBrains Mono

**Visuals:**
- Terminal screenshots (actual thinking boxes)
- Flowcharts (Mermaid-generated)
- Metrics as big numbers
- Minimal text, maximum impact

**Animations:**
- Fade ins only
- No distracting transitions
- Code appears typed (for effect)

---

## **BACKUP MATERIALS**

**If demo fails:**
- Pre-recorded full workflow ready
- Screenshots of each phase
- Can narrate from stills

**If questions about:**
- Jira integration → Show MCP screenshot
- Costs → Rough estimates ready
- Other models → Config file ready

**Extended Q&A topics:**
- Technical deep-dive on state management
- Planning doc workshop
- Office hours schedule
- Contributing guidelines

---

## **POST-SESSION SHARE**

**Slack post template:**
```
🎲 Agent Cube Session - Resources

📊 Slides: [link]
🎥 Recordings: [Loom 1] [Loom 2]  
📚 Docs: github.com/aetheronhq/agent-cube
🚀 Quick Start: docs/QUICK_START.md

Try it:
cube auto <your-task>.md

Issues:
github.com/aetheronhq/agent-cube/issues

Questions: DM me anytime!

#agent-cube #ai-development
```

---

**READY TO BUILD SLIDES IN GAMMA/KEYNOTE!** 🎨

