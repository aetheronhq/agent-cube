## 🤖 The Agent Cube has become sentient!

The Agent Cube has built itself a fully functional CLI tool to orchestrate parallel LLM coding workflows:

→ **Dual Writers** (2 LLMs) code solutions independently in parallel
→ **Judge Panel** (3 LLMs) reviews and votes for the winner  
→ **Synthesis** combines best of both approaches
→ **Peer Review** validates the final solution
→ **PR Creation** for human review

**Bonus:** Optional Jira MCP use - picks up tasks, moves to In Progress, comments, and moves to Review when done

**Install:**
```bash
git clone https://github.com/aetheronhq/agent-cube.git
cd agent-cube
./install.sh
```

**Use:**
Ask Cursor to run `cube --help`, read `AGENT_CUBE.md`, and point it to your specs (works with any planning doc format, bonus points for OpenSpec.dev).

Then watch 6 agents work together to produce the best solution! 🚀

