from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.db.utils import OperationalError
import time
from django.conf import settings
from django.core.mail import send_mail
from .models import Ticket, InternalNote, _notify
from users.models import User
from .forms import TicketCreateForm, TicketUpdateForm, CommentForm, FeedbackForm, InternalNoteForm


def build_ticket_detail_context(request, ticket, is_staff_user, comment_form, feedback_form, internal_note_form, resolution_note_display=''):
    feedback = getattr(ticket, 'feedback', None)
    internal_notes = ticket.internal_notes.select_related('user').order_by('-created_at')
    recommended_solutions = []
    suggestion = ticket.suggested_solution()
    if suggestion:
        recommended_solutions.append(suggestion)
    if not recommended_solutions:
        recommended_solutions = [
            'Check known outage notices in the ICT updates.',
            'Restart the affected device and confirm network access.',
            'Verify account permissions and retry the action.',
        ]

    return {
        'ticket': ticket,
        'resolution_note_display': resolution_note_display or ticket.resolution_note or '',
        'comment_form': comment_form,
        'feedback_form': feedback_form,
        'feedback': feedback,
        'internal_note_form': internal_note_form,
        'internal_notes': internal_notes,
        'recommended_solutions': recommended_solutions,
        'is_staff_user': is_staff_user,
        'status_choices': Ticket.STATUS_CHOICES,
        'attachments': ticket.attachments.select_related('uploaded_by').order_by('-uploaded_at'),
        'possible_assignees': User.objects.filter(role__in=[User.Role.TECHNICIAN, User.Role.STAFF, User.Role.ADMIN]).order_by('first_name', 'last_name'),
    }


@login_required
def ticket_list(request):
    tickets = Ticket.objects.all()
    status = request.GET.get('status')
    query = request.GET.get('q')

    if query:
        tickets = tickets.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(id__icontains=query)
        )

    # Filter by user role
    if request.user.role == 'student':
        tickets = tickets.filter(created_by=request.user)
    elif request.user.role == 'technician':
        # Technicians see all, or only assigned? Usually all but highlighted assigned.
        pass

    valid_statuses = {value for value, _ in Ticket.STATUS_CHOICES}
    if status in valid_statuses:
        tickets = tickets.filter(status=status)

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'selected_status': status or 'all',
        'status_choices': Ticket.STATUS_CHOICES,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Permission check (simple)
    if request.user.role == 'student' and ticket.created_by != request.user:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('tickets:list')

    is_staff_user = request.user.role in ['technician', 'staff', 'admin']

    comment_form = CommentForm()
    feedback_form = FeedbackForm()
    internal_note_form = InternalNoteForm()
    resolution_note_display = ''

    if request.method == 'POST':
        resolution_note = request.POST.get('resolution_note', '').strip()
        resolution_note_display = resolution_note or ticket.resolution_note or ''
        if is_staff_user and resolution_note:
            ticket.resolution_note = resolution_note
            ticket.save(update_fields=['resolution_note'])
            ticket.refresh_from_db()

        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.user = request.user
                comment.save()
                # Notify the other party (submitter gets notified of staff reply and vice versa)
                ticket_url = f'http://localhost:8000/tickets/{ticket.pk}/'

                recipients = {ticket.created_by.email}
                if ticket.assigned_to:
                    recipients.add(ticket.assigned_to.email)
                recipients.discard(request.user.email)
                commenter = request.user.get_full_name() or request.user.username
                extra_html = (
                    f'<h2 style="margin:0 0 8px;font-size:20px;color:#111827;">New Comment on Your Ticket</h2>'
                    f'<p style="margin:0 0 16px;color:#4b5563;font-size:15px;">'
                    f'<strong>{commenter}</strong> left a comment on ticket #{ticket.id}.</p>'
                    f'<div style="background:#f8f9fa;border-left:4px solid #fcd116;border-radius:4px;padding:14px 18px;">'
                    f'<p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">{comment.text}</p>'
                    f'</div>'
                )
                _notify(
                    f'[Ticket #{ticket.id}] New comment: {ticket.title}',
                    f'{commenter} commented on ticket #{ticket.id}: {comment.text}',
                    list(recipients - {None, ''}),
                    ticket=ticket, cta_url=ticket_url, cta_label='View & Reply', extra_html=extra_html,
                )
                messages.success(request, 'Comment added.')
                return redirect('tickets:detail', pk=pk)
        elif 'feedback_submit' in request.POST:
            # Support creating or updating feedback robustly
            existing_feedback = getattr(ticket, 'feedback', None)
            feedback_form = FeedbackForm(request.POST, instance=existing_feedback)
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.ticket = ticket
                feedback.save()
                messages.success(request, 'Thank you for your feedback!')
                return redirect('tickets:detail', pk=pk)
        elif 'internal_note_submit' in request.POST and is_staff_user:
            internal_note_form = InternalNoteForm(request.POST)
            if internal_note_form.is_valid():
                note = internal_note_form.save(commit=False)
                note.ticket = ticket
                note.user = request.user
                note.save()
                messages.success(request, 'Internal note saved.')
                return redirect('tickets:detail', pk=pk)
        elif 'status_submit' in request.POST and is_staff_user:
            new_status = request.POST.get('status')
            if new_status in dict(Ticket.STATUS_CHOICES):
                ticket.status = new_status
                ticket.resolution_note = request.POST.get('resolution_note', '').strip()
                ticket.save()
                ticket.refresh_from_db()
                messages.success(request, 'Ticket status updated.')
        elif 'assign_submit' in request.POST and is_staff_user:
            assignee_id = request.POST.get('assigned_to')
            if assignee_id:
                assignee = User.objects.filter(
                    id=assignee_id,
                    role__in=[User.Role.TECHNICIAN, User.Role.STAFF, User.Role.ADMIN]
                ).first()
                if assignee:
                    ticket.assigned_to = assignee
                    ticket.save()
                    messages.success(request, f'Ticket assigned to {assignee.get_full_name() or assignee.username}.')
                else:
                    messages.error(request, 'Selected assignee is not valid.')
            else:
                messages.error(request, 'Please select a user to assign the ticket to.')
            return redirect('tickets:detail', pk=pk)
        elif 'assign_to_me' in request.POST and is_staff_user:
            ticket.assigned_to = request.user
            ticket.save()
            messages.success(request, 'Ticket assigned to you.')
            return redirect('tickets:detail', pk=pk)
        elif 'close_ticket' in request.POST and is_staff_user:
            ticket.status = 'closed'
            ticket.resolution_note = request.POST.get('resolution_note', '').strip()
            ticket.save()
            ticket.refresh_from_db()
            messages.success(request, 'Ticket closed.')
        elif 'escalate_ticket' in request.POST and is_staff_user:
            ticket.is_escalated = True
            # Try assigning to an admin user when escalating
            admin_user = User.objects.filter(role='admin').first()
            if admin_user:
                ticket.assigned_to = admin_user
            ticket.save()
            # Add an internal note recording the escalation
            try:
                InternalNote.objects.create(
                    ticket=ticket,
                    user=request.user,
                    text=f"Escalated by {request.user.get_full_name()} to {admin_user.get_full_name() if admin_user else 'senior staff'}"
                )
            except Exception:
                # Do not block the main flow if note creation fails
                pass
            messages.success(request, 'Ticket escalated.')
            return redirect('tickets:detail', pk=pk)
        elif 'reopen_ticket' in request.POST and request.user == ticket.created_by:
            if ticket.status == 'closed':
                messages.error(request, 'Closed tickets cannot be reopened.')
                return redirect('tickets:detail', pk=pk)
            ticket.status = 'open'
            ticket.is_escalated = False
            # Clear closed timestamp when reopening
            ticket.closed_at = None
            ticket.save()
            messages.success(request, 'Ticket reopened.')
            return redirect('tickets:detail', pk=pk)

    return render(request, 'tickets/ticket_detail.html', build_ticket_detail_context(
        request,
        ticket,
        is_staff_user,
        comment_form,
        feedback_form,
        internal_note_form,
        resolution_note_display if request.method == 'POST' else '',
    ))


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            
            # Check for AI suggestion
            suggestion = ticket.suggested_solution()
            if suggestion:
                messages.info(request, f"AI Suggestion: {suggestion}")

            messages.success(request, 'Ticket created successfully.')
            return redirect('tickets:detail', pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Create Ticket'})


@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.user.role == 'student' and ticket.created_by != request.user:
        messages.error(request, "You do not have permission to edit this ticket.")
        return redirect('tickets:detail', pk=pk)

    FormClass = TicketCreateForm if request.user.role == 'student' else TicketUpdateForm

    if request.method == 'POST':
        form = FormClass(request.POST, instance=ticket)
        if form.is_valid():
            # Save within a DB transaction and retry on transient SQLite locks
            max_attempts = 5
            for attempt in range(1, max_attempts + 1):
                try:
                    with transaction.atomic():
                        form.save()
                    break
                except OperationalError:
                    if attempt == max_attempts:
                        messages.error(request, 'Database is locked; please try again in a moment.')
                        return redirect('tickets:detail', pk=pk)
                    time.sleep(0.3 * attempt)

            messages.success(request, 'Ticket updated.')
            return redirect('tickets:detail', pk=pk)
    else:
        form = FormClass(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'title': 'Update Ticket'})


@login_required
def kanban_board(request):
    # Only for technicians/staff/admin
    if request.user.role == 'student':
         messages.error(request, "Access denied.")
         return redirect('tickets:list')

    tickets = Ticket.objects.all()
    return render(request, 'tickets/kanban.html', {
        'open_tickets': tickets.filter(status='open'),
        'in_progress_tickets': tickets.filter(status='in_progress'),
        'resolved_tickets': tickets.filter(status='resolved'),
        'closed_tickets': tickets.filter(status='closed'),
    })
