"""Tests for _html_to_plain() and the HTML-only email fallback in _parse_message."""

import email.message
import waggle
from waggle import _html_to_plain


def _single_part_html_raw(body_html):
    """Build a minimal single-part text/html raw message."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Test"
    msg["Message-Id"] = "<html-only@example.com>"
    msg.set_content(body_html, subtype="html")
    return msg.as_bytes()


def _multipart_html_only_raw(body_html):
    """Build a multipart/alternative with only an HTML part (no text/plain)."""
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart("alternative")
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Test"
    msg["Message-Id"] = "<mp-html-only@example.com>"
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    return msg.as_bytes()


class TestHtmlToPlain:
    def test_style_block_stripped(self):
        result = _html_to_plain('<style>body{font-family:-apple-system}</style><p>Hello</p>')
        assert 'font-family' not in result
        assert 'body{' not in result
        assert 'Hello' in result

    def test_script_block_stripped(self):
        result = _html_to_plain('<script>alert("xss")</script><p>Safe</p>')
        assert 'alert' not in result
        assert 'Safe' in result

    def test_div_per_line_ios_mail(self):
        """iOS Mail composes one <div> per line — must not collapse into run-on text."""
        result = _html_to_plain('<div>Hi Jason,</div><div>Can you check the deploy?</div><div>Thanks — Sam</div>')
        assert 'Hi Jason,' in result
        assert 'Can you check the deploy?' in result
        assert 'Thanks' in result
        # Lines must be separated, not run together
        assert 'Hi Jason,Can' not in result

    def test_block_elements_produce_newlines(self):
        for tag in ['h1', 'h2', 'h3', 'blockquote', 'tr']:
            result = _html_to_plain(f'<{tag}>First</{tag}><{tag}>Second</{tag}>')
            assert 'FirstSecond' not in result, f"<{tag}> did not produce line break"

    def test_smart_quotes_decoded(self):
        """iOS autocorrect emits smart quotes — must decode to readable characters."""
        result = _html_to_plain('<p>It&#8217;s working &#8212; great&#8230;</p>')
        assert '’' in result  # right single quotation mark
        assert '—' in result  # em dash
        assert '&#8217;' not in result
        assert '&#8212;' not in result

    def test_named_entities_decoded(self):
        result = _html_to_plain('<p>Hello &amp; world &mdash; done</p>')
        assert '&' in result
        assert '&amp;' not in result
        assert '—' in result  # &mdash;

    def test_nbsp_decoded(self):
        result = _html_to_plain('<p>Hello&nbsp;World</p>')
        assert '&nbsp;' not in result
        assert 'Hello' in result and 'World' in result

    def test_list_items(self):
        result = _html_to_plain('<ul><li>One</li><li>Two</li></ul>')
        assert '• One' in result
        assert '• Two' in result

    def test_hr_becomes_separator(self):
        result = _html_to_plain('<p>Above</p><hr><p>Below</p>')
        assert '---' in result

    def test_excessive_newlines_collapsed(self):
        result = _html_to_plain('<p>A</p><p></p><p></p><p>B</p>')
        assert '\n\n\n' not in result

    def test_plain_text_content_preserved(self):
        result = _html_to_plain('<p>Hello, Mema. I am thinking of you.</p>')
        assert 'Hello, Mema. I am thinking of you.' in result


class TestParseMessageHtmlFallback:
    def test_single_part_html_populates_body_html(self):
        """Single-part text/html message must set body_html, not body_plain."""
        raw = _single_part_html_raw('<html><body><div>Hello</div></body></html>')
        result = waggle._parse_message(raw)
        assert result['body_html'] is not None
        assert '<html>' not in (result['body_plain'] or '')

    def test_single_part_html_derives_body_plain(self):
        """body_plain must be derived from HTML, not contain raw markup."""
        raw = _single_part_html_raw('<div>Hi Jason,</div><div>Thanks &#8212; Sam</div>')
        result = waggle._parse_message(raw)
        assert result['body_plain'] is not None
        assert '<div>' not in result['body_plain']
        assert 'Hi Jason,' in result['body_plain']
        assert '—' in result['body_plain']  # em dash decoded

    def test_multipart_html_only_derives_body_plain(self):
        """multipart/alternative with no text/plain must derive body_plain from HTML."""
        raw = _multipart_html_only_raw('<p>My cat Newman passed away.</p>')
        result = waggle._parse_message(raw)
        assert result['body_plain'] is not None
        assert 'Newman' in result['body_plain']
        assert '<p>' not in result['body_plain']

    def test_plain_text_message_unaffected(self):
        """Plain-text messages must be completely unaffected by this change."""
        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Test"
        msg["Message-Id"] = "<plain@example.com>"
        msg.set_content("Just plain text.", subtype="plain")
        result = waggle._parse_message(msg.as_bytes())
        assert result['body_plain'] is not None
        assert 'Just plain text.' in result['body_plain']
