## 🤖 The Agent Cube has become sentient!

Built itself a CLI tool to orchestrate parallel LLM coding workflows. Here's the full cycle:

→ **Dual Writers** (2 LLMs) code solutions independently in parallel
→ **Judge Panel** (3 LLMs) reviews and votes for the winner  
→ **Synthesis** combines best of both approaches
→ **Peer Review** validates the final solution
→ **PR Creation** for human review

**Bonus:** Optional Jira integration + works with any planning docs (OpenSpec.dev format gets bonus points!)

**Install:**
```bash
git clone https://github.com/aetheronhq/agent-cube.git
cd agent-cube
./install.sh
```

**Use:**
Ask Cursor to run `cube --help`, read `AGENT_CUBE.md`, and point it to your specs. Then watch it go! 🚀

