# InjectRAG project guidance

At the first user message of every new session in this repository, use the `orient` skill before answering substantively or making changes. Read and follow [.agents/skills/orient/SKILL.md](.agents/skills/orient/SKILL.md), even if it has not appeared in the skill selector. This is the project's startup orientation instruction; the user does not need to request it again.

Run orientation once per session, then refresh relevant sources when they change or context is missing. Continue the user's actual request after reading; orientation alone does not authorize implementation. An explicit user instruction to skip or narrow orientation takes precedence.

The skill routes to the maintained documentation and plan. Keep project decisions in [documentation/decisions.md](documentation/decisions.md), not separate ADR files. Do not duplicate changing project status or design choices here.
