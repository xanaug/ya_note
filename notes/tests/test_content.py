from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Заметка.', author=cls.author
        )

    def test_successful_note_creation(self):
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_note_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertContains(response, self.note.title)
        self.client.logout()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Заметка.', author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_note_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Тестовая заметка')
        self.assertContains(response, 'Заметка')
        self.client.logout()
