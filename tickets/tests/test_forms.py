from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from tickets.forms import TicketCreateForm
from tickets.models import Category, Ticket, Feedback
from users.forms import UserRegistrationForm


class UserRegistrationFormTests(TestCase):
    def test_student_email_must_be_cuea_student_format(self):
        form = UserRegistrationForm({
            'first_name': 'Jane',
            'last_name': 'Student',
            'email': '1049528@cuea.edu',
            'role': 'student',
            'department': 'ICT',
            'phone': '+254700000000',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_staff_email_must_be_cuea_staff_format(self):
        form = UserRegistrationForm({
            'first_name': 'Sharon',
            'last_name': 'Bossy',
            'email': 'Sharonbossy@cuea.edu',
            'role': 'staff',
            'department': 'ICT',
            'phone': '+254700000000',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_non_cuea_email_is_rejected(self):
        form = UserRegistrationForm({
            'first_name': 'Jane',
            'last_name': 'Student',
            'email': 'jane@gmail.com',
            'role': 'student',
            'department': 'ICT',
            'phone': '+254700000000',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class TicketFormTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='Software')

    def test_valid_ticket_form(self):
        form = TicketCreateForm({
            'title': 'Printer not working',
            'description': 'Printer fails to print documents from student lab',
            'category': self.cat.id,
            'priority': 'high',
        })
        self.assertTrue(form.is_valid())

    def test_short_title_invalid(self):
        form = TicketCreateForm({
            'title': 'Bad',
            'description': 'Description is long enough to be valid here.',
            'category': self.cat.id,
            'priority': 'low',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_short_description_invalid(self):
        form = TicketCreateForm({
            'title': 'Printer problem',
            'description': 'too short',
            'category': self.cat.id,
            'priority': 'low',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_feedback_submission_saves_feedback(self):
        User = get_user_model()
        user = User.objects.create_user(username='feedback_user', password='password123', role='student')
        ticket = Ticket.objects.create(
            title='Printer issue',
            description='The printer stopped working after a system update and needs review.',
            created_by=user,
            category=self.cat,
            status='resolved',
        )

        self.client.force_login(user)
        response = self.client.post(
            f'/tickets/{ticket.pk}/',
            {'feedback_submit': '1', 'rating': '5', 'comment': 'Great service'},
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        feedback = Feedback.objects.get(ticket=ticket)
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.comment, 'Great service')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_resolved_ticket_shows_visible_feedback_form(self):
        User = get_user_model()
        user = User.objects.create_user(username='feedback_viewer', password='password123', role='student')
        ticket = Ticket.objects.create(
            title='Keyboard issue',
            description='Some keys do not type and the issue needs follow-up.',
            created_by=user,
            category=self.cat,
            status='resolved',
        )

        self.client.force_login(user)
        response = self.client.get(f'/tickets/{ticket.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Share your experience')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_staff_can_add_resolution_note_and_it_is_visible_to_requester(self):
        User = get_user_model()
        staff = User.objects.create_user(username='staff_resolver', password='password123', role='staff')
        student = User.objects.create_user(username='student_requester', password='password123', role='student')
        ticket = Ticket.objects.create(
            title='Network issue',
            description='The campus Wi-Fi disconnects intermittently and needs follow-up.',
            created_by=student,
            category=self.cat,
            status='open',
        )

        self.client.force_login(staff)
        response = self.client.post(
            f'/tickets/{ticket.pk}/',
            {
                'status_submit': '1',
                'status': 'resolved',
                'resolution_note': 'The router was rebooted and the network issue was resolved.',
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'resolved')
        self.assertEqual(ticket.resolution_note, 'The router was rebooted and the network issue was resolved.')

        self.client.force_login(student)
        response = self.client.get(f'/tickets/{ticket.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resolution update')
        self.assertContains(response, 'The router was rebooted and the network issue was resolved.')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_status_update_response_shows_the_submitted_resolution_note(self):
        User = get_user_model()
        staff = User.objects.create_user(username='staff_note_viewer', password='password123', role='staff')
        student = User.objects.create_user(username='student_note_viewer', password='password123', role='student')
        ticket = Ticket.objects.create(
            title='Display note issue',
            description='The resolution note should be shown immediately after submission.',
            created_by=student,
            category=self.cat,
            status='open',
        )

        self.client.force_login(staff)
        response = self.client.post(
            f'/tickets/{ticket.pk}/',
            {
                'status_submit': '1',
                'status': 'resolved',
                'resolution_note': 'This is the note I typed.',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is the note I typed.')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_my_ticket_list_can_filter_by_status(self):
        User = get_user_model()
        student = User.objects.create_user(username='list_filter_student', password='password123', role='student')
        Ticket.objects.create(
            title='Open ticket',
            description='This should be visible in open filter.',
            created_by=student,
            category=self.cat,
            status='open',
        )
        Ticket.objects.create(
            title='Resolved ticket',
            description='This should be visible in resolved filter.',
            created_by=student,
            category=self.cat,
            status='resolved',
        )

        self.client.force_login(student)

        response = self.client.get('/tickets/?status=open')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Open ticket')
        self.assertNotContains(response, 'Resolved ticket')

        response = self.client.get('/tickets/?status=resolved')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resolved ticket')
        self.assertNotContains(response, 'Open ticket')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_close_ticket_action_saves_resolution_note(self):
        User = get_user_model()
        staff = User.objects.create_user(username='staff_closer', password='password123', role='staff')
        student = User.objects.create_user(username='student_closer', password='password123', role='student')
        ticket = Ticket.objects.create(
            title='Printer issue',
            description='The printer in the lab keeps jamming and needs follow-up.',
            created_by=student,
            category=self.cat,
            status='open',
        )

        self.client.force_login(staff)
        response = self.client.post(
            f'/tickets/{ticket.pk}/',
            {
                'close_ticket': '1',
                'resolution_note': 'The printer was serviced and the issue is now resolved.',
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'closed')
        self.assertEqual(ticket.resolution_note, 'The printer was serviced and the issue is now resolved.')

    @override_settings(ALLOWED_HOSTS=['testserver'])
    def test_closed_ticket_cannot_be_reopened(self):
        User = get_user_model()
        student = User.objects.create_user(username='student_closed_ticket_user', password='password123', role='student')
        ticket = Ticket.objects.create(
            title='Closed ticket should stay closed',
            description='This ticket was closed and should not be reopened by the requester.',
            created_by=student,
            category=self.cat,
            status='closed',
        )

        self.client.force_login(student)
        response = self.client.post(
            f'/tickets/{ticket.pk}/',
            {'reopen_ticket': '1'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'closed')
        self.assertContains(response, 'Closed tickets cannot be reopened.')
