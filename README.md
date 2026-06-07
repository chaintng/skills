# chaintng/ai-playbook

> ⚠️ CAUTION 
> 
> This skill is experimental. 
> 
> DO BACKUP your CapCut project before use.
> 
> Use it at your own RISK.

## Workspace

`ai-playbook` is the `monolithic wrapper`, a root knowledge and automation repo for Agentic skills, reusable workflows, and supporting resources.

To use this repository, clone this repo as a `root workspace directory`, and other of your resources into this directory and tell agentic to update how your workspace is structured.

## Working Directory 

// SAMPLE WORKING DIRECTORY
// MUST ASK AGENTIC TO UPDATE BEFORE USE

```text
my-projects/ # cloned `ai-playbook` repo (`git clone https://github.com/chaintng/ai-playbook.git`)
├── .codex/
│   └── skills/
├── vdo-contents/
│   ├── footage/
│   ├── final-videos/
│   └── temp/
├── obsidian/
│   ├── migration-tools/
│   └── plugins/
├── smarthome/
│   └── hassio-core/
├── coding/
│   ├── chillish/
│   ├── ...
├── blogs/
│   ├── content/
│   ├── ...
├── README.md
└── AGENTS.md
```

Top-level folders:
- `.codex/` stores Codex skills, playbooks, and local agent automation. Follow best practices for agent metadata and automation scripts.
- `vdo-contents/` stores video project materials, including raw footage, temp working files, and final exports.
- `obsidian/` stores the Obsidian contribution project, note vault material, plugins, and migration helpers.
- `smarthome/` stores smart home related projects, home automation, embedded devices, and configuration work.
- `coding/` stores other software side projects, experiments, utilities, and client or personal codebases.
- `blogs/` static site generated from content of my personal blog (https://chaintng.com), powered by Quartz
