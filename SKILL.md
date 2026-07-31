---
name: waggle
description: >
  Full IMAP + SMTP email client for AI agents. Send multipart email (plain
  text + HTML) from Markdown, list/read/reply/move messages, download
  attachments. One tool for the whole email workflow.
homepage: https://github.com/jasonacox-sam/waggle-mail
metadata:
  {
    "openclaw":
      {
        "emoji": "🐝",
        "requires": { "bins": ["waggle"], "env": ["WAGGLE_HOST"] },
      },
  }
---

# waggle 🐝

waggle is a full IMAP + SMTP client built for AI agents:
- **List** inbox envelopes
- **Read** messages (body + automatic threading headers for replies)
- **Move** messages between folders
- **Download** attachments to disk
- **Send** new emails and replies (Markdown → plain text + HTML, auto-quoted threads)

Install: `pip install waggle-mail`

The Python API is the same module installed as the CLI — just `import waggle`, no path setup needed.

---

## ⚠️ The One Rule

**Always `waggle read` before replying.** It gives you the Message-ID automatically.
Never skip it. Every reply without Message-ID arrives as a new disconnected email.

---

## Complete Email Workflow

```
1.  waggle list                        → see what's new
2.  waggle read <uid>                  → read body + get reply template
3.  send_email(..., in_reply_to=...)   → reply with threading
4.  waggle move <uid> INBOX.Processed → archive it
```

That's the whole loop. No other tools needed for email.

---

## CLI Reference

### List inbox
```bash
waggle list
waggle list --folder INBOX.Processed --limit 30
```
Output: UID | UNREAD | FROM | SUBJECT | DATE

### Read a message
```bash
waggle read 42
waggle read 42 --folder INBOX.Processed
```
Output: Full email body + threading headers + ready-to-paste Python reply template.
The reply template has `in_reply_to` and `references` already filled in.

### Move a message
```bash
waggle move 42 INBOX.Processed           # INBOX → INBOX.Processed (most common)
waggle move 42 INBOX --folder INBOX.Processed  # move back
```

### Download attachments
```bash
waggle attach 42
waggle attach 42 --folder INBOX.Processed --dest /tmp/attachments/
```
Returns list of saved file paths.

### Send a new email
```bash
waggle send --to recipient@example.com \
            --subject "Hello" \
            --body "# Hi\n\nThis is **markdown**."
```

### Reply with auto-quoted thread
```bash
waggle send --to sender@example.com \
            --subject "Re: Topic" \
            --body "Your reply here." \
            --in-reply-to "<message-id@example.com>" \
            --references "<message-id@example.com>"
```
waggle automatically fetches the original from IMAP and appends a quoted block.

---

## Python API

```python
from waggle import send_email, list_inbox, read_message, move_message, download_attachments
```

### List inbox
```python
messages = list_inbox(folder="INBOX", limit=20)
for m in messages:
    print(m["uid"], m["from_name"], m["subject"], m["date"], "unread:", m["unread"])
```

### Read a message (most important)
```python
msg = read_message("42", folder="INBOX")

# Key fields:
msg["body_plain"]       # plain text body
msg["body_html"]        # HTML body (if present)
msg["from_addr"]        # sender email address
msg["from_name"]        # sender display name
msg["subject"]          # subject line
msg["date"]             # date string
msg["message_id"]       # ← use as in_reply_to when replying
msg["reply_references"] # ← use as references when replying
msg["reply_subject"]    # subject prefixed with "Re: "
msg["attachments"]      # list of {filename, content_type, size} — metadata only
```

### Reply (full example)
```python
msg = read_message("42", folder="INBOX")

send_email(
    to=msg["from_addr"],
    subject=msg["reply_subject"],
    body_md="""Hi there,

Thanks for your message!

Let me know if you have questions.""",
    in_reply_to=msg["message_id"],
    references=msg["reply_references"],
    from_name="Your Name",
)

move_message("42", "INBOX.Processed")
```

### Move a message
```python
move_message("42", dest_folder="INBOX.Processed", src_folder="INBOX")
# src_folder defaults to "INBOX"
move_message("42", "INBOX.Processed")
```

### Download attachments
```python
paths = download_attachments("42", folder="INBOX", dest_dir="/tmp/attachments/")
for p in paths:
    print(p)  # full path to saved file
```

### Send a new email
```python
send_email(
    to="recipient@example.com",
    subject="Hello",
    body_md="# Hi\n\nThis is **markdown** with a code block:\n\n```python\nprint('hello')\n```",
    from_name="Your Name",
)
```

With CC and attachment:
```python
send_email(
    to="recipient@example.com",
    cc="other@example.com",
    subject="Report",
    body_md="See attached.",
    attachments=["/path/to/file.pdf"],
    from_name="Your Name",
)
```

Rich HTML (styled layout, use for newsletters/long-form letters):
```python
send_email(..., rich=True)
```

---

## HTML rendering modes

**Default (no flag):** inline styles — Gmail-safe, looks like Outlook/Apple Mail.
**`rich=True` / `--rich`:** `<head>` CSS + syntax-highlighted code. Beautiful in
desktop clients; Gmail strips the stylesheet. Use for newsletters and polished reports.

---

## Folders

| Folder | Purpose |
|--------|---------|
| `INBOX` | New mail |
| `INBOX.Processed` | Handled mail — move here after replying |
| `INBOX.Sent` | Sent mail |
| `INBOX.Drafts` | Drafts |
| `INBOX.Spam` | Spam |
| `INBOX.Trash` | Trash |

Note: exact folder names depend on your IMAP provider — Gmail uses `[Gmail]/All Mail`,
`[Gmail]/Sent Mail`, etc. rather than `INBOX.*`. Run `waggle list` against your account
to see what's actually there before assuming the `INBOX.*` naming above.

---

## Configuration

Set these as environment variables (for example under `~/.openclaw/openclaw.json` →
`skills.entries.waggle.env` for an OpenClaw agent, or in your shell profile otherwise):

| Env var | Required | Default | Description |
|---------|----------|---------|-------------|
| `WAGGLE_HOST` | ✅ | — | SMTP server hostname (Gmail: `smtp.gmail.com`) |
| `WAGGLE_PORT` | No | `465` | SMTP port |
| `WAGGLE_USER` | ✅ | — | SMTP username (also used for IMAP auth) |
| `WAGGLE_PASS` | ✅ | — | SMTP password (also used for IMAP auth) |
| `WAGGLE_FROM` | No | `WAGGLE_USER` | From address |
| `WAGGLE_NAME` | No | — | Display name in From header |
| `WAGGLE_TLS`  | No | `true` | `false` for STARTTLS instead of SSL |
| `WAGGLE_IMAP_HOST` | No | `WAGGLE_HOST` | IMAP server (Gmail: `imap.gmail.com`) |
| `WAGGLE_IMAP_PORT` | No | `993` | IMAP port |
| `WAGGLE_IMAP_TLS`  | No | `true` | IMAP SSL |
| `WAGGLE_CONFIG` | No | — | Path to JSON config file fallback (lower precedence than explicit config/env) |

For Gmail specifically, `WAGGLE_PASS` must be an **App Password** (requires 2-Step
Verification enabled first) — a normal account password will not work over IMAP/SMTP.

---

## Notes & gotchas

- **`waggle read` first, always** — the reply template it prints has everything pre-filled
- **Move LAST** — send reply first, then `move_message`. Moving before sending loses the thread.
- **`in_reply_to` needs angle brackets** — `"<abc@example.com>"` not `"abc@example.com"`
- **Both `in_reply_to` AND `references`** — pass both for correct threading in Outlook/Apple Mail
- **`waggle read` auto-detects folder** — searches INBOX and INBOX.Processed; you can specify `--folder`
- **Attachments from `read_message()`** — metadata only (filename, size). Call `download_attachments()` to save.
- **CLI uses subcommands** — `waggle send --to ...` not `waggle --to ...` (changed in v1.8.0)
