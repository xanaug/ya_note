from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель')

    def assertRouteStatus(self, route_name, args=None,
                          expected_status=HTTPStatus.OK):
        url = reverse(route_name, args=args)
        response = self.client.get(url)
        self.assertEqual(response.status_code, expected_status)

    def assertRedirectForAnonymous(self, route_name, args=None):
        url = reverse(route_name, args=args)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)

    def test_pages_availability(self):
        route_names = [
            ('notes:home', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        ]
        for route_name, args in route_names:
            with self.subTest(route_name=route_name):
                url = reverse(route_name, args=args)
                response = self.client.get(url)
                login_url = reverse('users:login')
                if response.status_code == HTTPStatus.FOUND:
                    redirect_url = f'{login_url}?next={url}'
                    self.assertRedirects(
                        response, redirect_url, status_code=HTTPStatus.FOUND
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = [
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        ]
        route_names = ['notes:edit', 'notes:delete', 'notes:detail']
        for user, status in users_statuses:
            self.client.force_login(user)
            for route_name in route_names:
                with self.subTest(route_name=route_name, user=user):
                    self.assertRouteStatus(
                        route_name,
                        args=(self.note.slug,),
                        expected_status=status)

    def test_redirect_for_anonymous_client(self):
        route_names = ['notes:edit', 'notes:delete', 'notes:detail']
        for route_name in route_names:
            with self.subTest(route_name=route_name):
                self.assertRedirectForAnonymous(
                    route_name, args=(self.note.slug,)
                )
