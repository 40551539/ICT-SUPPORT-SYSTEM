from django import forms
from .models import Ticket, Comment, Feedback, InternalNote
from users.models import User


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category']

    def clean_title(self):
        t = (self.cleaned_data.get('title') or '').strip()
        if len(t) < 5:
            raise forms.ValidationError('Title must be at least 5 characters')
        return t

    def clean_description(self):
        d = (self.cleaned_data.get('description') or '').strip()
        if len(d) < 15:
            raise forms.ValidationError('Description must be more detailed (>=15 chars)')
        return d


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'status', 'assigned_to', 'is_escalated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow assigning to technicians/staff/admins
        self.fields['assigned_to'].queryset = User.objects.filter(role__in=[
            User.Role.TECHNICIAN,
            User.Role.STAFF,
            User.Role.ADMIN,
        ])

    def clean_title(self):
        t = (self.cleaned_data.get('title') or '').strip()
        if len(t) < 5:
            raise forms.ValidationError('Title must be at least 5 characters')
        return t

    def clean_description(self):
        d = (self.cleaned_data.get('description') or '').strip()
        if len(d) < 15:
            raise forms.ValidationError('Description must be more detailed (>=15 chars)')
        return d


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any other feedback?'}),
            'rating': forms.RadioSelect(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]),
        }


class InternalNoteForm(forms.ModelForm):
    class Meta:
        model = InternalNote
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a private note for staff...'}),
        }
