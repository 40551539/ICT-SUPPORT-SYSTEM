from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def _html_wrap(title, preheader, body_html):
    """Wrap content in a branded HTML email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f7;font-family:'Segoe UI',Arial,sans-serif;">
<span style="display:none;max-height:0;overflow:hidden;">{preheader}</span>

<!-- Wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:40px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

      <!-- Header -->
      <tr>
        <td style="background:#ce1126;border-radius:12px 12px 0 0;padding:28px 40px;text-align:center;">
          <p style="margin:0;color:rgba(255,255,255,0.7);font-size:11px;letter-spacing:2px;text-transform:uppercase;">Catholic University of Eastern Africa</p>
          <h1 style="margin:6px 0 0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-0.3px;">
            🎧 ICT Help Desk
          </h1>
        </td>
      </tr>

      <!-- Body -->
      <tr>
        <td style="background:#ffffff;padding:40px;border-left:1px solid #e8e8ec;border-right:1px solid #e8e8ec;">
          {body_html}
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="background:#f9f9fb;border:1px solid #e8e8ec;border-top:none;border-radius:0 0 12px 12px;padding:20px 40px;text-align:center;">
          <p style="margin:0;font-size:12px;color:#9ca3af;">
            This is an automated message from the CUEA ICT Help Desk.<br>
            <a href="https://tickets.innbucks.org" style="color:#ce1126;text-decoration:none;">tickets.innbucks.org</a>
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def _btn(url, label):
    return f"""
<p style="text-align:center;margin:28px 0 0;">
  <a href="{url}" style="display:inline-block;background:#ce1126;color:#ffffff;text-decoration:none;font-weight:600;font-size:14px;padding:13px 32px;border-radius:8px;">
    {label} →
  </a>
</p>"""


def _badge(label, color, text_color='#ffffff'):
    return f'<span style="display:inline-block;background:{color};color:{text_color};font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.5px;">{label.upper()}</span>'


PRIORITY_COLORS = {
    'low': ('#2f6fed', '#ffffff'),
    'medium': ('#fcd116', '#1f2937'),
    'high': ('#ce1126', '#ffffff'),
    'critical': ('#ce1126', '#ffffff'),
}

STATUS_COLORS = {
    'open': ('#2f6fed', '#ffffff'),
    'in_progress': ('#fcd116', '#1f2937'),
    'resolved': ('#1cc88a', '#ffffff'),
    'closed': ('#6c757d', '#ffffff'),
}


def send_ticket_email(subject, plain_message, recipients, ticket=None, extra_html='', cta_url=None, cta_label='View Ticket'):
    from users.models import User
    admin_emails = list(
        User.objects.filter(role='admin', is_active=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )
    all_recipients = list({e for e in list(recipients) + admin_emails if e})
    if not all_recipients:
        return

    # Build ticket info block
    ticket_block = ''
    if ticket:
        p_color, p_text = PRIORITY_COLORS.get(ticket.priority, ('#6c757d', '#fff'))
        s_color, s_text = STATUS_COLORS.get(ticket.status, ('#6c757d', '#fff'))
        ticket_block = f"""
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fa;border-radius:8px;padding:0;margin:20px 0;">
  <tr>
    <td style="padding:20px 24px;">
      <p style="margin:0 0 12px;font-size:13px;color:#6b7280;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Ticket Details</p>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="padding:4px 0;font-size:13px;color:#6b7280;width:110px;">Ticket</td>
          <td style="padding:4px 0;font-size:13px;color:#111827;font-weight:600;">#{ticket.id} — {ticket.title}</td>
        </tr>
        <tr>
          <td style="padding:4px 0;font-size:13px;color:#6b7280;">Priority</td>
          <td style="padding:4px 0;">{_badge(ticket.get_priority_display(), p_color, p_text)}</td>
        </tr>
        <tr>
          <td style="padding:4px 0;font-size:13px;color:#6b7280;">Status</td>
          <td style="padding:4px 0;">{_badge(ticket.get_status_display(), s_color, s_text)}</td>
        </tr>
        <tr>
          <td style="padding:4px 0;font-size:13px;color:#6b7280;">Category</td>
          <td style="padding:4px 0;font-size:13px;color:#111827;">{ticket.category or 'Uncategorised'}</td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""

    cta_block = _btn(cta_url, cta_label) if cta_url else ''

    body_html = f"""
{extra_html}
{ticket_block}
{cta_block}"""

    html = _html_wrap(subject, plain_message[:90], body_html)

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=all_recipients,
    )
    email.attach_alternative(html, 'text/html')
    email.send(fail_silently=True)
