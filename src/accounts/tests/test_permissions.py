from typing import cast
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import AnonymousUser, Group
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase
from django_htmx.middleware import HtmxDetails

from accounts.models import User
from accounts.permissions import has_role, role_required


class HasRoleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Retrieve the default Groups created by our data migration.
        cls.admin_group = Group.objects.get(name="Admin")
        cls.editor_group = Group.objects.get(name="Editor")

        # Create users for testing.
        cls.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )

        cls.editor = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password="test-password",
        )

        cls.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="test-password",
        )

        cls.custom_group_user = User.objects.create_user(
            username="custom",
            email="custom@example.com",
            password="test-password",
        )

        cls.superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@example.com",
            password="test-password",
        )

        # Assign default roles.
        cls.admin.groups.add(cls.admin_group)
        cls.editor.groups.add(cls.editor_group)

        # Assign a custom Group.
        cls.marketing_group = Group.objects.create(name="Marketing")
        cls.custom_group_user.groups.add(cls.marketing_group)

    def test_user_has_requested_role(self):
        self.assertTrue(has_role(self.admin, "Admin"))

    def test_user_has_requested_editor_role(self):
        self.assertTrue(has_role(self.editor, "Editor"))

    def test_user_does_not_have_different_role(self):
        self.assertFalse(has_role(self.editor, "Admin"))

    def test_user_without_role_returns_false(self):
        self.assertFalse(has_role(self.regular_user, "Viewer"))

    def test_anonymous_user_returns_false(self):
        self.assertFalse(has_role(AnonymousUser(), "Admin"))

    def test_custom_group_is_not_a_default_role(self):
        self.assertFalse(has_role(self.custom_group_user, "Marketing"))

    def test_superuser_without_admin_group_is_not_application_admin(self):
        self.assertTrue(self.superuser.is_superuser)
        self.assertFalse(has_role(self.superuser, "Admin"))


@role_required("Admin")
def admin_only_view(request):
    return HttpResponse("Admin content")


class HtmxRequest(HttpRequest):
    htmx: HtmxDetails


class RoleRequiredTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.get(name="Admin")
        cls.editor_group = Group.objects.get(name="Editor")

        cls.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )

        cls.editor = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password="test-password",
        )

        cls.admin.groups.add(cls.admin_group)
        cls.editor.groups.add(cls.editor_group)

    def setUp(self):
        self.factory = RequestFactory()

    def create_request(self, user):
        request = cast(HtmxRequest, self.factory.get("/protected/"))
        request.user = user

        # RequestFactory doesn't execute Django middleware.
        # Explicitly mark this as a normal HTTP request.
        request.htmx = HtmxDetails(request)

        return request

    def test_user_with_required_role_can_access_view(self):
        request = self.create_request(self.admin)

        response = admin_only_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Admin content")

    def test_user_without_required_role_receives_403(self):
        request = self.create_request(self.editor)

        response = admin_only_view(request)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        request = self.create_request(AnonymousUser())

        response = admin_only_view(request)

        self.assertEqual(response.status_code, 302)

        query = parse_qs(urlsplit(response.url).query)

        self.assertEqual(query["next"], ["/protected/"])

    def test_invalid_role_raises_value_error(self):
        with self.assertRaises(ValueError):
            role_required("InvalidRole")
