## 🤖 The Agent Cube has become sentient!

The Agent Cube has built itself a fully functional CLI tool to orchestrate the complete parallel LLM coding workflow:

**The Full Cycle:**

- **Orchestrator** chooses the task based on dependency analysis
- **Dual Writers** (2 LLMs) implement solutions independently and in parallel
- **Judge Panel** (3 LLMs) reviews both solutions and votes for the winner
- **Synthesis** the writer combines the best of both approaches as recommended by the panel
- **Peer Review** validates the final solution
- **PR Creation** for human review

**Bonus Features:**

- Optional Jira integration to update tickets, pick tasks from backlog, and auto-move to "Review"
- Works with any planning doc format (bonus points for OpenSpec.dev, but not mandatory)

**To Install:**

```bash
git clone https://github.com/aetheronhq/agent-cube.git
cd agent-cube
./install.sh
```

**To Use:**

Just ask Cursor to:

1. Run `cube --help`
2. Read `AGENT_CUBE.md`
3. Point it to your specs/planning documents

Then watch the agents work in parallel! 🚀

