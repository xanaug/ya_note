from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class NoteCreateTest(TestCase):
    NOTE_TEST_TEXT = 'Тестовая заметка.'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Тестовый')
        cls.note = Note.objects.create(
            title='Заголовок', text='Тестовая заметка.', author=cls.user
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.slug = cls.note.slug
        cls.form_data = {'text': cls.NOTE_TEST_TEXT}
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        self.client.logout()
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(response.url.startswith(reverse('users:login')))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def setUp(self):
        self.client.login(username='Тестовый')

    def test_home_view(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/home.html')

    def test_note_success(self):
        response = self.auth_client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/success.html')

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/form.html')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEST_TEXT)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.user)


class NoteFormTest(TestCase):
    NOTE_TEST_TEXT = 'Тестовая заметка.'
    UPDATE_NOTE_TEST_TEXT = 'Тестовая заметка.'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Тестовый')
        cls.author = cls.user
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Левый чумба')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок', text='Тестовая заметка.', author=cls.user
        )
        cls.slug = cls.note.slug
        cls.form_data = {'text': cls.NOTE_TEST_TEXT}
        cls.edit_url = reverse('notes:edit', args=(cls.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.slug,))
        cls.form_data = {'text': cls.UPDATE_NOTE_TEST_TEXT}
        cls.success_url = reverse('notes:success')

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.UPDATE_NOTE_TEST_TEXT)

    def test_auth_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEST_TEXT)

    def test_author_can_delete_note(self):
        note_count_before_delete = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        note_count_after_delete = Note.objects.count()
        self.assertEqual(note_count_after_delete, note_count_before_delete - 1)

    def test_auth_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_notes_list_view(self):
        response = self.author_client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'notes/list.html')
        self.assertContains(response, self.note.id)
