from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        data = {
            "email": "test@example.com",
            "username": "test",
            "password1": "goodpassword",
            "password2": "goodpassword",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        data_with_empty_form = {
            "email": "",
            "username": "",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, data_with_empty_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_username(self):
        data_with_empty_username = {
            "email": "test@example",
            "username": "",
            "password1": "goodpassword",
            "password2": "goodpassword",
        }
        response = self.client.post(self.url, data_with_empty_username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_email(self):
        data_with_empty_email = {
            "email": "",
            "username": "test",
            "password1": "goodpassword",
            "password2": "goodpassword",
        }
        response = self.client.post(self.url, data_with_empty_email)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "このフィールドは必須です。")

    def test_failure_post_with_empty_password(self):
        data_with_empty_password = {
            "email": "test@example",
            "username": "test",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, data_with_empty_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password1"][0], "このフィールドは必須です。")
        self.assertEqual(form.errors["password2"][0], "このフィールドは必須です。")

    def test_failure_post_with_duplicated_user(self):
        data_with_duplicated_user = {
            "email": "test@example",
            "username": "test",
            "password1": "goodpassword",
            "password2": "goodpassword",
        }
        User.objects.create_user(username="test", password="goodpassword")
        response = self.client.post(self.url, data_with_duplicated_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        data_invalid_email = {
            "email": "test@example",
            "username": "test",
            "password1": "goodpassword",
            "password2": "goodpassword",
        }
        response = self.client.post(self.url, data_invalid_email)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        data_too_short_password = {
            "email": "test@example",
            "username": "test",
            "password1": "good",
            "password2": "good",
        }
        response = self.client.post(self.url, data_too_short_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        data_similar_to_username = {
            "email": "test@example",
            "username": "testtest",
            "password1": "testtesta",
            "password2": "testtesta",
        }

        response = self.client.post(self.url, data_similar_to_username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        data_number_password = {
            "email": "test@example",
            "username": "test",
            "password1": "1111111111",
            "password2": "1111111111",
        }
        response = self.client.post(self.url, data_number_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        data_mismatch_password = {
            "email": "test@example",
            "username": "test",
            "password1": "goodpassword",
            "password2": "goodpasswood",
        }
        response = self.client.post(self.url, data_mismatch_password)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_user(self):
        pass

    def test_failure_post_with_self(self):
        pass


class TestUnfollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowingListView(TestCase):
    def test_success_get(self):
        pass


class TestFollowerListView(TestCase):
    def test_success_get(self):
        pass
