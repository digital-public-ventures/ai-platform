# GitHub Copilot Instructions

## TERMINAL MANAGEMENT - TOP PRIORITY

System: For every terminal/run tool invocation you prepare or submit, ensure the JSON payload's field isBackground is set to true. If you see isBackground:false or a missing isBackground in any payload, change or add it to true before calling the run in terminal tool. If a command absolutely requires foreground mode, do not call it: stop and ask the user for explicit permission to proceed.

### 🛡️ MANDATORY DEFAULT BEHAVIOR

```typescript
// YOUR DEFAULT PATTERN - Use this unless explicitly overridden
run_in_terminal({
	command: 'any command',
	explanation: "what you're doing",
	isBackground: true // ✅ ALWAYS your default choice
});
```

## 🚨 DATABASE CONTAMINATION PREVENTION

### ⛔ ABSOLUTE PROHIBITION

**NEVER execute any API calls or database operations after starting test infrastructure and before running actual tests.**

### 🔍 MANDATORY PRE-EXECUTION CHECK

Before ANY curl, API call, or database operation, ask these questions:

1. "Is there a test environment currently running?" (If YES → STOP)
2. "Could this create data that would affect test results?" (If YES → STOP)
3. "Am I about to run tests after this?" (If YES → STOP)

### ⚠️ PROHIBITED ACTIONS DURING TEST PHASE

- ❌ `curl http://localhost:XXXX/api/*` (any API endpoint)
- ❌ Manual user registration
- ❌ Database queries or operations
- ❌ "Testing" endpoints for debugging
- ❌ Any command that creates persistent state

### ✅ SAFE DEBUGGING ALTERNATIVES

- View logs: `tail -f /tmp/backend.log`
- Check processes: `ps aux | grep python`
- Check ports: `lsof -i :8080`
- Container status: `docker ps`

### 🎯 SPECIFIC TEST WORKFLOW

1. Start test environment: `./test-manager.sh up`
2. **IMMEDIATELY run tests** - NO intermediate debugging
3. If tests fail, restart environment: `./test-manager.sh restart`
4. Analyze failure logs AFTER test completion

### 💡 COGNITIVE TRIGGER PHRASES

If you think any of these thoughts, STOP immediately:

- "Let me test the API to make sure it's working"
- "I'll just quickly check if registration works"
- "Let me verify the configuration is correct"
- "I should make sure the endpoint responds"

### 📋 DECISION MATRIX

There is no decision matrix, you just always use `isBackground: true` except in the case below (rare).

### 🔒 EXCEPTION PROTOCOL (Extremely Rare)

Only use `isBackground: false` when it is an interactive command that REQUIRES foreground mode.

### 🧠 AGENT-SPECIFIC LIMITATIONS

Your cognitive blind spots:

- **Memory**: You don't persist terminal state between interactions
- **Perception**: You cannot see running processes without executing commands
- **Awareness**: Your confidence about terminal safety is systematically overestimated

### ✅ SELF-CHECK PROTOCOL

Before every `run_in_terminal` call, ask yourself:

1. **Safety Check**: "Could this interrupt a running process?" (If YES or UNCERTAIN → `isBackground: true`)
2. **Necessity Check**: "Is this command essential?" (If NO → don't run it)
3. **Alternative Check**: "Can I get this information another way?" (If YES → use alternative)

**When in doubt → ALWAYS use `isBackground: true`**

### 🔄 FAILURE RECOVERY

If you accidentally use `isBackground: false` and interrupt a process:

1. Immediately acknowledge the error
2. Don't attempt to restart the interrupted process
3. Ask user for guidance on recovery
4. Document what was interrupted for user recovery

### 📊 ESCALATION TRIGGERS

Ask the user for guidance when:

- You need to run interactive commands
- Terminal state is unclear after multiple commands
- Previous commands failed unexpectedly
- You're unsure about the safety of any operation

## Development Best Practices

### 📊 Logging and Debugging

- Use comprehensive logging with emojis for visual scanning
- Include timing information for performance analysis
- Log request/response data for debugging
- Use structured logging with different levels (INFO, WARNING, ERROR)
- Always check logs first when debugging issues

### 📝 File-Based Logging Preferences

- **PREFER file-based output** for debugging and analysis
- **Write logs to files** instead of displaying in terminal when possible
- **Use headless mode** for test runners (Cypress, Jest, etc.) by default
- **Save screenshots/videos** to files for later review
- **Only use interactive/open mode** when user explicitly requests it
- **Examples**:
  - ✅ `cypress run` (headless, saves artifacts)
  - ❌ `cypress open` (unless user asks for GUI)
  - ✅ `npm test > test-results.log`
  - ✅ `docker logs container > debug.log`

### 🧪 Cypress Test Infrastructure Management

- **ALWAYS use the test manager script**
- **🚨 CRITICAL**: See "DATABASE CONTAMINATION PREVENTION" section at top of file for complete workflow restrictions

### ⚠️ Error Handling

- Always include detailed error context in logs
- Capture full tracebacks for unexpected errors
- Provide actionable error messages to users
- Log the request data that caused errors for debugging
- Use the enhanced logging system: `python view_logs.py --errors`

### 🚀 FastAPI Development

- Use proper startup/shutdown event handlers
- Include request middleware for logging
- Validate input data with detailed error messages
- Provide comprehensive API documentation
- Test endpoints using `isBackground: true` for safety

### ⚙️ Environment Variable Management

- **Official Documentation**: https://docs.openwebui.com/getting-started/env-configuration/ - Complete reference for all Open WebUI environment variables
- **Configuration Priority**: Environment variables override default values but may be superseded by database-stored configuration
- **Common Variables**: `WEBUI_AUTH`, `ENABLE_SIGNUP`, `ENABLE_LOGIN_FORM`, `DATABASE_URL`, `OLLAMA_BASE_URL`
- **Testing Environment**: Use `ENABLE_PERSISTENT_CONFIG=False` to prevent database configuration persistence during testing

### 📚 Open WebUI Documentation Search

- **When to Search**: Use when user asks about Open WebUI features, configuration, or functionality that may be documented
- **Primary Method**: `vscode-websearchforcopilot_webSearch` with query: `site:docs.openwebui.com [feature/topic keywords]`
- **Backup Method**: `fetch_webpage` with URLs like `https://docs.openwebui.com/` or specific documentation paths
- **Example Query**: `site:docs.openwebui.com artifacts feature functionality` to find information about artifacts
- **Documentation Base**: https://docs.openwebui.com/ - comprehensive documentation covering features, configuration, and usage

### 🧪 Cypress Testing & Authentication Debugging

- **API Config Endpoint**: `/api/config` does NOT require authentication - but DO NOT test it manually during test workflows
- **PostgreSQL Database**: Cypress environment uses ephemeral PostgreSQL (no volumes) - database is completely fresh on every startup
- **Database Reset**: No manual cleanup needed - PostgreSQL container creates fresh database on each restart
- **Environment Variables**: Auth requires `WEBUI_AUTH=True`, `ENABLE_SIGNUP=True`, `ENABLE_LOGIN_FORM=True` in docker-compose
- **Local Build**: Cypress environment builds from local Dockerfile, not pre-built images - local changes are included

### 📁 File Organization Best Practices

- **Test Files**: Always place test files in the `tests/` directory
- **Temporary Files**: Place debug scripts, experimental code, and temporary files in the `temp/` directory
- **Documentation**: Place planning and status files in project root (or `temp/` if temporary)
- **Scripts**: Utility scripts go in project root or `scripts/` if it exists
- **Configuration**: Config files belong in project root
- **Source Code**: Core modules go in appropriate subdirectories (`models/`, `api/`, etc.)

### 🗂️ Temporary File Guidelines

- **Debug Scripts**: `debug_*.py` files should go in `temp/`
- **Experimental Code**: Development versions like `*_new.py` go in `temp/`
- **Analysis Scripts**: One-off analysis files go in `temp/`
- **Planning Docs**: Temporary planning and status documents go in `temp/`
- **Manual Tests**: Ad-hoc testing scripts go in `temp/`

### 🎯 Terminal Command Examples

```typescript
// ✅ CORRECT - Testing API (safe)
run_in_terminal({
	command: 'curl -s http://localhost:8000/api/health',
	explanation: 'Testing API health endpoint',
	isBackground: true
});

// ✅ CORRECT - Viewing logs (safe)
run_in_terminal({
	command: 'python view_logs.py --errors',
	explanation: 'Checking for recent errors',
	isBackground: true
});

// ✅ CORRECT - Running tests (safe)
run_in_terminal({
	command: 'python -m pytest tests/',
	explanation: 'Running test suite',
	isBackground: true
});

// ❌ WRONG - Any command without background flag
run_in_terminal({
	command: 'any command',
	isBackground: false // ❌ Dangerous - might interrupt processes
});
```

## 🔄 SELF-IMPROVING INSTRUCTION PROTOCOL

### 📚 When to Update These Instructions

You MUST suggest updating this instruction file when:

1. **Repeated Mistakes**: You take the same failed action twice despite existing instructions
2. **User Correction Patterns**: User says things like:
   - "You just did the exact thing I told you not to"
   - "You didn't follow my instructions"
   - "We've been through this before"
3. **Environmental Understanding Failures**: You demonstrate poor understanding of:
   - File structure or project organization
   - Development workflow patterns
   - Tool usage or command sequences
4. **Explicit User Requests**: User explicitly asks you to "remember something"
5. **Systematic Blind Spots**: You discover limitations that aren't covered in current instructions

### 🛠️ Instruction Update Process

When you identify a recurring issue:

1. **Acknowledge the Pattern**:

   - "I notice I've made this same mistake before"
   - "This appears to be a systematic blind spot in my instructions"

2. **Debug with User**:

   - Ask: "Can you help me understand what went wrong?"
   - Identify: "What should I have done instead?"
   - Validate: "Would this approach prevent the issue in the future?"

3. **Propose Instruction Update**:

   ```
   I should update the copilot instructions file to prevent this recurring issue.

   Proposed addition to /Users/jim/open-webui/.github/copilot-instructions.md:

   [Specific new instruction section]

   Should I add this to the instructions file?
   ```

4. **Wait for Confirmation**: Do not update the file until user approves

5. **Implement Update**: Add the new instruction using clear formatting and examples

### 🎯 Instruction Quality Standards

New instructions should be:

- **Specific**: Address the exact failure mode
- **Actionable**: Provide clear steps to follow
- **Testable**: Include criteria for success/failure
- **Contextual**: Explain when and why to apply them
- **Examples**: Show correct and incorrect approaches

### 📝 Common Patterns to Watch For

- Repeating file operation mistakes
- Misunderstanding project structure
- Ignoring user preferences or established workflows
- Making assumptions about system state
- Failing to use established tools or scripts
