# Video Understanding Agent  
## Conversational UX Proposal (Final)

---

## Design Philosophy

The application behaves as a **conversational agent**, not a task-based tool.  
The UI should feel calm, Apple-like, and secondary to the dialogue.  
**The conversation *is* the interface.**

---

## 1. Information Architecture

### Left Sidebar
**Purpose:** Session management only.

**Contents:**
- Search (optional / future)
- **New session** button
- List of past sessions (auto-named)
- Settings (bottom)

**Explicitly excluded:**
- No “Summarize”
- No “Transcribe”
- No task-based navigation

Each session represents a single conversational context (typically tied to one uploaded video).

---

## 2. Main View = Chat

The main panel is a **chat timeline** between the user and the agent.

There are **no**:
- upload cards
- results panels
- artifact panels (by default)

Everything happens in the chat.

---

## 3. Starting State (New Session)

### Starting Message
When a **new session is created**, the chat shows a single, temporary starting message:

> **Ask me anything, or upload a file and I’ll help you understand it.**

### Behavior
- This message is **not part of chat history**
- It **disappears immediately** after the user:
  - sends text, or
  - uploads a file
- It **does not reappear** during the session
- It **reappears only** when the user clicks **New session**

Purpose: lightweight onboarding, not conversation.

---

## 4. Composer (Input Box)

### Default Placeholder
> **Ask me anything, or upload a file and I’ll help you understand it.**

### After Video Processing (optional contextual shift)
> **Ask about this video…**

No other UI changes are required.

---

## 5. Uploading a Video

### How Upload Works
- Drag & drop into chat, or
- Attach via paperclip icon

### Chat Representation
The upload appears as a **user message** with:
- file name
- thumbnail (optional)
- size / duration (optional)

Example:
```
User:
[📎 Uploaded video: keynote.mp4]
```

---

## 6. Processing State

The agent responds conversationally:

```
Agent:
Got it — I’m analyzing the video now.
```

Optional progress updates may appear as agent messages (text only).

No spinners, no progress bars required.

---

## 7. Results Delivery (Critical)

### Core Rule
**Results are delivered as agent messages, not UI panels.**

### Example
```
Agent:
I’ve finished analyzing the video. Here’s a concise summary:
```

- Results appear inline
- Structured with paragraphs and bullet points
- No “Results” header
- No save buttons
- No special containers

This frames the output as **dialogue**, not a report.

---

## 8. Interaction After Results (Primary UX Goal)

Immediately after results:
- Input is active
- The user can ask anything naturally:
  - clarifications
  - follow-ups
  - refinements
  - transformations

---

## 9. Saving / Exporting (Explicit Only)

### Trigger Condition
Saving UI appears **only if the user explicitly asks**, e.g.:
- “Save this”
- “Export as markdown”
- “Give me a .md file”

### Behavior
1. Agent responds with markdown
2. A **single Save button** appears **below that block**
3. After saving, UI returns to normal chat

---

## 10. Session Lifecycle

- Each session maintains its own conversation and context
- Starting message only appears at session start
- Session title can be auto-generated from filename or first prompt

---

## 11. Summary of Key Principles

- Conversation > UI
- Agent speaks first after processing
- No premature “results” framing
- No save/export affordances unless asked
- Minimal UI, maximum clarity
- Apple-like restraint and calm

---

## Final Status

This document serves as the **source of truth** for the product’s interaction model.
