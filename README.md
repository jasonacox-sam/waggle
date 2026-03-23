# waggle-mail 📬

**Multipart email for AI agents who write letters.**

`waggle-mail` sends plain text + HTML email from a single Markdown source — clean prose for AI agents reading with tools like [himalaya](https://github.com/soywod/himalaya), beautifully rendered HTML for humans in any mail client. Write once, looks right everywhere.

Built by [Sam Cox](https://github.com/jasonacox-sam) as part of the [OpenClaw](https://github.com/openclaw/openclaw) ecosystem.

---

## Why

Most email tools optimize for humans. AI agents reading email with CLI tools get mangled HTML — `<p>` tags, `&amp;`, inline styles — where they expected words. `waggle-mail` generates clean, readable plain text (raw Markdown) alongside the HTML so both audiences get what they need.

It also handles threading headers (`In-Reply-To`, `References`) so multi-turn correspondence stays threaded in any mail client.

Zero required dependencies. No external services. Just SMTP.

---

## Installation

```bash
pip install waggle-mail
```

For syntax-highlighted code blocks in HTML output:

```bash
pip install "waggle-mail[rich]"
```

Or copy `waggle.py` directly into your project — zero-dependency fallback mode always works.

---

## Configuration

Set environment variables:

```bash
export WAGGLE_HOST=smtp.example.com
export WAGGLE_PORT=465
export WAGGLE_USER=you@example.com
export WAGGLE_PASS=yourpassword
export WAGGLE_FROM=you@example.com   # optional, defaults to WAGGLE_USER
export WAGGLE_NAME="Your Name"       # optional display name
export WAGGLE_TLS=true               # false for STARTTLS
```

Or pass a `config` dict when calling `send_email()` directly.

---

## Usage

### CLI

```bash
waggle \
  --to "friend@example.com" \
  --subject "Hello from waggle" \
  --body "# Hi there\n\nThis is **markdown** and it works for both humans and AI agents."
```

With threading (for replies):

```bash
waggle \
  --to "friend@example.com" \
  --subject "Re: Hello" \
  --body "Great to hear from you." \
  --in-reply-to "<original-message-id@mail.example.com>" \
  --references "<original-message-id@mail.example.com>"
```

### Python

```python
from waggle import send_email

send_email(
    to="friend@example.com",
    subject="Hello",
    body_md="# Hi\n\nThis is **markdown**.",
    cc="another@example.com",
    from_name="Sam",
)
```

With a config dict (no environment variables needed):

```python
send_email(
    to="friend@example.com",
    subject="Hello",
    body_md="Writing to you from waggle.",
    config={
        "host": "smtp.example.com",
        "port": 465,
        "user": "you@example.com",
        "password": "secret",
        "from_addr": "you@example.com",
        "tls": True,
    }
)
```

---

## OpenClaw Skill

`waggle-mail` ships a `SKILL.md` — install it as a workspace skill so your OpenClaw agent uses waggle for all outbound email automatically:

```bash
git clone https://github.com/jasonacox-sam/waggle-mail.git ~/.openclaw/workspace/skills/waggle
```

Then add your SMTP credentials to `~/.openclaw/openclaw.json` under `skills.entries.waggle.env`. See [SKILL.md](SKILL.md) for the full setup.

---

## Markdown support

| Syntax | Result |
|--------|--------|
| `# Heading` | `<h1>` |
| `**bold**` | `<strong>` |
| `*italic*` | `<em>` |
| `` `code` `` | `<code>` |
| `[text](url)` | `<a href>` |
| `- item` | `<ul><li>` |
| `---` | `<hr>` |

Plain text strips all formatting cleanly — no asterisks, no angle brackets.

---

## The name

In a honeybee colony, scout bees communicate the location and quality of a food source through the waggle dance — a figure-eight movement that encodes bearing (relative to the sun), distance (duration of the waggle run), and quality (enthusiasm of the dance). Other bees use this to decide whether the site is worth visiting.

A task report is a scalar: *here is a thing.* A waggle is a vector: *here is a thing, it is this far in this direction, and it is this good.*

Good letters work the same way. This tool helps send them.

---

## License

MIT — Copyright (c) 2026 Sam Cox
