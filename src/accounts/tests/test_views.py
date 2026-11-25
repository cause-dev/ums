from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="test-password",
            first_name="Alice",
        )

        cls.other_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="test-password",
            first_name="Bob",
        )

        cls.staff = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="test-password",
            is_staff=True,
        )

        cls.other_staff = User.objects.create_user(
            username="otherstaff",
            email="otherstaff@example.com",
            password="test-password",
            is_staff=True,
        )

        cls.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )

    def field_url(self, view_name, target, field_name):
        return reverse(
            view_name,
            args=[target, field_name],
        )

    # --------------------------------------------------
    # ProfileView
    # --------------------------------------------------

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 302)

    def test_user_can_view_own_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.user)

    # --------------------------------------------------
    # UserListView
    # --------------------------------------------------

    def test_regular_user_only_sees_themselves(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("user_list"))

        self.assertEqual(response.status_code, 200)

        user_ids = set(response.context["users"].values_list("pk", flat=True))

        self.assertEqual(user_ids, {self.user.pk})

    def test_staff_sees_themselves_and_regular_users(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("user_list"))

        self.assertEqual(response.status_code, 200)

        user_ids = set(response.context["users"].values_list("pk", flat=True))

        self.assertEqual(
            user_ids,
            {
                self.staff.pk,
                self.user.pk,
                self.other_user.pk,
            },
        )

    # --------------------------------------------------
    # UserFieldView
    # --------------------------------------------------

    def test_user_can_view_own_field(self):
        self.client.force_login(self.user)

        response = self.client.get(
            self.field_url(
                "user_view_field",
                self.user.pk,
                "first_name",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["field_value"], "Alice")

    def test_user_cannot_view_another_users_field(self):
        self.client.force_login(self.user)

        response = self.client.get(
            self.field_url(
                "user_view_field",
                self.other_user.pk,
                "first_name",
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_view_regular_users_field(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            self.field_url(
                "user_view_field",
                self.user.pk,
                "first_name",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["field_value"], "Alice")

    # --------------------------------------------------
    # UserFieldInputView
    # --------------------------------------------------

    def test_user_can_request_own_field_input(self):
        self.client.force_login(self.user)

        response = self.client.get(
            self.field_url(
                "user_input_field",
                self.user.pk,
                "first_name",
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["field_name"], "first_name")

    def test_user_cannot_request_active_field_input(self):
        self.client.force_login(self.user)

        response = self.client.get(
            self.field_url(
                "user_input_field",
                self.user.pk,
                "is_active",
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_request_active_field_for_regular_user(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            self.field_url(
                "user_input_field",
                self.user.pk,
                "is_active",
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_request_other_regular_fields(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            self.field_url(
                "user_input_field",
                self.user.pk,
                "first_name",
            )
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # UserFieldUpdateView
    # --------------------------------------------------

    def test_user_can_update_own_first_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.user.pk,
                "first_name",
            ),
            {"value": "Updated"},
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "Updated")

    def test_user_cannot_update_own_is_active(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.user.pk,
                "is_active",
            ),
            {"value": "false"},
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_update_another_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.other_user.pk,
                "first_name",
            ),
            {"value": "Updated"},
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_update_own_first_name(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.staff.pk,
                "first_name",
            ),
            {"value": "Updated"},
        )

        self.assertEqual(response.status_code, 200)

        self.staff.refresh_from_db()

        self.assertEqual(self.staff.first_name, "Updated")

    def test_staff_cannot_update_own_is_active(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.staff.pk,
                "is_active",
            ),
            {"value": "false"},
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_activate_regular_user(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.user.pk,
                "is_active",
            ),
            {"value": "on"},
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertTrue(self.user.is_active)

    def test_staff_can_deactivate_regular_user(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.user.pk,
                "is_active",
            ),
            {},
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)

    def test_staff_cannot_update_regular_users_other_fields(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.user.pk,
                "first_name",
            ),
            {"value": "Updated"},
        )

        self.assertEqual(response.status_code, 404)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "Alice")

    def test_staff_cannot_update_other_staff(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.other_staff.pk,
                "is_active",
            ),
            {"value": "false"},
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_cannot_update_superuser(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.superuser.pk,
                "is_active",
            ),
            {"value": "false"},
        )

        self.assertEqual(response.status_code, 404)

    def test_invalid_email_is_not_saved(self):
        self.client.force_login(self.user)

        original_email = self.user.email

        response = self.client.post(
            self.field_url(
                "user_update_field",
                self.user.pk,
                "email",
            ),
            {"value": "not-an-email"},
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.email, original_email)
