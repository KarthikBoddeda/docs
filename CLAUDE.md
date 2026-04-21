# docs

Internal documentation repository. Reference only — do not modify without explicit request.

## General Rules (apply to all tasks in workspaces using this docs repo)

### 1. When to ABORT and Ask for Clarification

When running a long list of tasks or subtasks:
- If user input is vague or ambiguous — ABORT and ask for more details
- If unsure whether to proceed to the next step — ABORT and confirm with user
- If prerequisites are missing or unclear — ABORT and ask for inputs
- If the task outcome is uncertain — ABORT and verify expected behavior

Never assume. When in doubt, ask.

### 2. File Path References in Documentation

When referring to a file or document in any documentation:
- Always use the complete path relative to the workspace root
- Use absolute paths starting from the repo root (e.g., `/docs/projects/payment-pages-decomp/_index.md`)
- Never use relative paths like `../` or `./` in documentation

### 3. Updating References When Renaming/Moving Files

When a file path, file name, or folder name is updated:
1. Search for all references to the old path across the workspace
2. Update every file that references the old path
3. Verify no broken links remain

### 4. DANGEROUS SCRIPTS - NEVER EXECUTE

| Script | Location | Reason |
|--------|----------|--------|
| `delete_by_ids.py` | `/pythonscripts/decomp-scripts/migration/DANGER_never_run_with_agent/` | DELETES payment page data permanently from NCA database |

Rules:
- NEVER run `python delete_by_ids.py` or any variation
- NEVER set `DRY_RUN = False` in the script
- NEVER execute the delete API endpoint directly via curl
- You MAY read, edit, or explain the script
- You MAY run with `DRY_RUN = True` (default) to preview

If user asks to run the delete script:
1. ABORT and remind them this must be done manually
2. Provide the command: `cd /pythonscripts/decomp-scripts/migration/DANGER_never_run_with_agent && python3 delete_by_ids.py`
3. Remind them to verify `DRY_RUN = True` first, then set to `False` when ready

## Slack Messaging Guidelines

When sending messages via `slack_send_message` or `slack_send_dm`:

### Before Sending
1. Always confirm with the user — channel, who to tag, and key points before posting.
2. Search for the channel first if you only have the name — use `slack_get_channels`.
3. Find user IDs for @mentions — use `slack_get_users`. Format: `<@U1234567890>`.

### Message Formatting (Slack mrkdwn, NOT standard markdown)
- Bold: `*text*` (not `**text**`)
- Italic: `_text_` (not `*text*`)
- Code: `` `code` `` or ` ```code block``` `
- Links: `<https://url.com|display text>`
- User mention: `<@USER_ID>`
- Channel mention: `<#CHANNEL_ID>`
- Keep messages concise and scannable. Use emojis sparingly (standard Slack emoji names only).

### Do NOT
- Send messages without user confirmation of content and target channel.
- Include sensitive data (API keys, passwords, PII) in messages.
- Send to public channels without explicit user request.

## Learnings Repo — Knowledge Gardener

Apply when editing or adding to `learnings/`.

Structure:
- Root: `learnings/` (under docs)
- Questions: `learnings/{category}/{sub_category}/questions/`
- Topics: `learnings/{category}/{sub_category}/topics/`
- Naming: `snake_case.md`, 8-15 words max

For a new learning thread:
1. Create one `.md` in the right `questions/` folder.
2. Frontmatter: `tags`, `status: In Progress | Answered`, links to related topic files.
3. Sections: `## The Core Question` and `## The Learning Log` (chronological).

When correcting a wrong assumption, append to the Learning Log:
- `### Refinement: [Short Title]`
- **My Misconception:** one sentence.
- **The Correction:** concise reality.
- **Key Insight:** one "aha" takeaway.

When a new concept is explained in depth: create or link `topics/{topic_name}.md` and update the sub_category `_index.md`.

Do NOT add new queries or sections to `coralogix-queries.md` unless explicitly asked.
