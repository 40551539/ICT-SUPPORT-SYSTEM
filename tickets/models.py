from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail


def _notify(subject, message, recipients, ticket=None, cta_url=None, cta_label='View Ticket', extra_html=''):
    from tickets.email_utils import send_ticket_email
    send_ticket_email(subject, message, recipients, ticket=ticket, extra_html=extra_html, cta_url=cta_url, cta_label=cta_label)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_categories'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    is_escalated = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        # Track previous status/assignee for change notifications
        prev_status = None
        prev_assigned = None
        if not is_new:
            try:
                old = Ticket.objects.get(pk=self.pk)
                prev_status = old.status
                prev_assigned = old.assigned_to_id
            except Ticket.DoesNotExist:
                pass

        if is_new:
            # Auto-categorization
            description_lower = self.description.lower()
            if not self.category:
                if 'wifi' in description_lower or 'internet' in description_lower:
                    try:
                        self.category = Category.objects.get(name='Network')
                    except Category.DoesNotExist:
                        pass
                elif 'printer' in description_lower:
                    try:
                        self.category = Category.objects.get(name='Hardware')
                    except Category.DoesNotExist:
                        pass

            # Auto-assignment
            if self.category and self.category.default_technician and not self.assigned_to:
                self.assigned_to = self.category.default_technician

        if self.status in ['resolved', 'closed'] and not self.closed_at:
            self.closed_at = timezone.now()

        super().save(*args, **kwargs)

        
        ticket_url = f'/tickets/{self.id}/'

        submitter = self.created_by.email
        technician = self.assigned_to.email if self.assigned_to else None

        if is_new:
            extra = (
                f'<h2 style="margin:0 0 8px;font-size:20px;color:#111827;">New Support Ticket</h2>'
                f'<p style="margin:0 0 16px;color:#4b5563;font-size:15px;">A new ticket has been submitted and is awaiting attention.</p>'
                f'<div style="background:#fff8f8;border-left:4px solid #ce1126;border-radius:4px;padding:14px 18px;margin:0 0 4px;">'
                f'<p style="margin:0;font-size:14px;color:#374151;line-height:1.6;"><strong>Description:</strong><br>{self.description}</p>'
                f'</div>'
            )
            _notify(
                f'[Ticket #{self.id}] New ticket: {self.title}',
                f'A new support ticket #{self.id} has been submitted: {self.title}',
                list({submitter, technician} - {None}),
                ticket=self, cta_url=ticket_url, cta_label='View Ticket', extra_html=extra,
            )

        elif prev_status and prev_status != self.status:
            prev_label = dict(self.STATUS_CHOICES).get(prev_status, prev_status)
            extra = (
                f'<h2 style="margin:0 0 8px;font-size:20px;color:#111827;">Ticket Status Updated</h2>'
                f'<p style="margin:0 0 4px;color:#4b5563;font-size:15px;">The status of your ticket has changed.</p>'
                f'<p style="margin:12px 0 0;font-size:14px;color:#374151;">'
                f'<strong>{prev_label}</strong> &nbsp;→&nbsp; <strong>{self.get_status_display()}</strong></p>'
            )
            _notify(
                f'[Ticket #{self.id}] Status updated: {self.get_status_display()}',
                f'Ticket #{self.id} status changed to {self.get_status_display()}.',
                list({submitter, technician} - {None}),
                ticket=self, cta_url=ticket_url, cta_label='View Ticket', extra_html=extra,
            )

        elif prev_assigned != self.assigned_to_id and self.assigned_to:
            name = self.assigned_to.get_full_name() or self.assigned_to.username
            extra = (
                f'<h2 style="margin:0 0 8px;font-size:20px;color:#111827;">Ticket Assigned to You</h2>'
                f'<p style="margin:0 0 4px;color:#4b5563;font-size:15px;">Hi {name}, this ticket has been assigned to you.</p>'
            )
            _notify(
                f'[Ticket #{self.id}] Assigned to you: {self.title}',
                f'Ticket #{self.id} has been assigned to you.',
                [self.assigned_to.email],
                ticket=self, cta_url=ticket_url, cta_label='View Ticket', extra_html=extra,
            )

    def suggested_solution(self):
        """Knowledge Base "AI" Suggestion"""
        desc = self.description.lower()
        if 'wifi' in desc or 'internet' in desc:
            return "Try restarting your router or checking if the cable is plugged in."
        elif 'printer' in desc:
            return "Check if the printer has paper and toner."
        elif 'password' in desc:
            return "You can reset your password at the login page."
        return None

    def __str__(self):
        return f"#{self.id} - {self.title}"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on #{self.ticket.id}"


class InternalNote(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='internal_notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Internal note by {self.user} on #{self.ticket.id}"


class Attachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for #{self.ticket.id}"


class Feedback(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for #{self.ticket.id} - {self.rating} Stars"
