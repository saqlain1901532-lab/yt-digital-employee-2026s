# Digital AI Employee Project

## Project Overview

This repository contains a **Personal AI Employee** (also called "Digital FTE" - Full-Time Equivalent) - an autonomous AI agent system that manages personal and business affairs 24/7. Built for the "Personal AI Employee Hackathon 2026", this project transforms Qwen Code from a reactive chatbot into a proactive business partner.

**Core Concept:** A local-first, agent-driven system with human-in-the-loop oversight that:
- Monitors communications (Gmail, WhatsApp, LinkedIn)
- Manages tasks and projects
- Handles accounting and payment tracking
- Generates proactive "Monday Morning CEO Briefings"
- Posts to social media platforms
- Integrates with business tools (Odoo, etc.)

## Architecture

### The Brain: Qwen Code
- Acts as the reasoning engine
- Uses **Ralph Wiggum pattern** (Stop hook) for autonomous multi-step task completion
- All AI functionality implemented as Agent Skills

### The Memory/GUI: Obsidian
- Local Markdown vault serves as dashboard and long-term memory
- Key files:
  - `Dashboard.md` - Real-time summary
  - `Company_Handbook.md` - Rules of engagement
  - `Business_Goals.md` - Objectives and metrics
  - `/Needs_Action/` - Pending tasks
  - `/Done/` - Completed tasks

### The Senses: Watchers (Python Scripts)
Lightweight background scripts that monitor inputs:
- **Gmail Watcher** - Monitors unread/important emails
- **WhatsApp Watcher** - Uses Playwright for WhatsApp Web automation
- **File System Watcher** - Monitors drop folders

### The Hands: MCP Servers
Model Context Protocol servers for external actions:
- **Playwright MCP** - Browser automation (port 8808)
- **Email MCP** - Send/draft emails
- **Filesystem MCP** - Built-in file operations
- **Calendar MCP** - Scheduling
- **Odoo MCP** - Accounting integration

## Project Structure

```
yt-digital-employee-2026/
├── .agents/
│   └── skills/
│       └── browsing-with-playwright/  # Playwright MCP skill
│           ├── SKILL.md               # Skill documentation
│           ├── references/
│           │   └── playwright-tools.md
│           └── scripts/
│               ├── mcp-client.py      # MCP client for tool calls
│               ├── start-server.sh    # Start Playwright server
│               ├── stop-server.sh     # Stop Playwright server
│               └── verify.py          # Server verification
├── .claude/
│   └── skills/                        # Claude skills directory
├── skills-lock.json                   # Installed skills registry
└── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main documentation
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Qwen Code | Active subscription | Reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Hardware Requirements
- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended:** 16GB RAM, 8-core CPU, SSD storage

### Key Commands

#### Playwright MCP Server
```bash
# Start the browser automation server
bash .agents/skills/browsing-with-playwright/scripts/start-server.sh

# Stop the server (closes browser first)
bash .agents/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify server is running
python .agents/skills/browsing-with-playwright/scripts/verify.py
```

#### MCP Client Usage
```bash
# Navigate to URL
python scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take accessibility snapshot
python scripts/mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# Click element
python scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'
```

#### Ralph Wiggum Loop (Persistence)
```bash
# Start autonomous task loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Conventions

### Agent Skills
- All AI functionality must be implemented as **Agent Skills**
- Skills are stored in `.agents/skills/` directory
- Each skill has `SKILL.md` with usage documentation
- Skills registry maintained in `skills-lock.json`

### Human-in-the-Loop Pattern
For sensitive actions, Qwen writes approval request files instead of acting directly:
1. Create `/Pending_Approval/ACTION_description.md`
2. User reviews and moves to `/Approved/` or `/Rejected/`
3. Orchestrator triggers actual action when approved

### Watcher Architecture
All watchers follow the `BaseWatcher` pattern:
- Continuous monitoring with configurable intervals
- Create `.md` files in `/Needs_Action/` when triggered
- Log errors gracefully without stopping

### Vault Organization
```
Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Tasks requiring attention
├── In_Progress/<agent>/ # Tasks claimed by specific agents
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Approved actions ready to execute
├── Done/               # Completed tasks
├── Plans/              # Generated plans (Plan.md)
├── Briefings/          # CEO briefings
└── Accounting/         # Financial records
```

## Tiered Achievement Levels

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Obsidian vault, 1 watcher, Claude reading/writing |
| **Silver** | 20-30 hrs | Multiple watchers, MCP server, HITL workflow |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, Ralph Wiggum loop |
| **Platinum** | 60+ hrs | Cloud deployment, Cloud/Local split, A2A messaging |

## Key Features

### Monday Morning CEO Briefing
Autonomous weekly audit that reports:
- Revenue earned this week
- Completed tasks
- Bottlenecks identified
- Proactive suggestions (e.g., unused subscriptions)

### Claim-by-Move Rule
Prevents double-work in multi-agent setups:
- First agent to move item from `/Needs_Action/` to `/In_Progress/<agent>/` owns it
- Other agents must ignore claimed items

### Subscription Audit
Automatically flags subscriptions for review if:
- No login in 30 days
- Cost increased >20%
- Duplicate functionality detected

## Troubleshooting

### Playwright MCP Server Issues
```bash
# Check if server is running
pgrep -f "@playwright/mcp"

# Restart server
bash scripts/stop-server.sh && bash scripts/start-server.sh
```

### Element Interaction Fails
1. Run `browser_snapshot` first to get current element refs
2. Try `browser_hover` before clicking
3. Increase wait time with `browser_wait_for`

## Resources

- [Wednesday Research Meetings](https://www.youtube.com/@panaversity) - Wednesdays 10:00 PM PKT
- [Playwright MCP Tools](.agents/skills/browsing-with-playwright/references/playwright-tools.md)
