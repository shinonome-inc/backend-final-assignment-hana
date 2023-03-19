from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import FriendShip
from tweets.models import Tweet

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
            reverse(settings.LOGIN_REDIRECT_URL),
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
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])

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
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])

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
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。", "このパスワードは一般的すぎます。"])

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
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])

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
        self.assertEqual(form.errors["password2"], ["このパスワードは一般的すぎます。", "このパスワードは数字しか使われていません。"])

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
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test",
            email="testemail@gmail.com",
            password="password1",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "test",
            "password": "password1",
        }

        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(
            User.objects.filter(
                username=valid_data["username"],
                email=valid_data["password"],
            ).exists()
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        not_exists_user_data = {
            "username": "nottest",
            "password": "password1",
        }
        response = self.client.post(self.url, not_exists_user_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                username=not_exists_user_data["username"],
                password=not_exists_user_data["password"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"],
            ["正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        empty_password_data = {
            "username": "test",
            "password": "",
        }
        response = self.client.post(self.url, empty_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=empty_password_data["password"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password"], ["このフィールドは必須です。"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = {
            "username": "test",
            "password": "password1",
        }
        self.client.login(username="test", password="password1")

    def test_success_get(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test1",
            email="test@example.com",
            password="password1",
        )
        self.client.login(username="test1", password="password1")
        self.post = Tweet.objects.create(user=self.user1, content="aiueo")
        self.url = reverse("accounts:user_profile", kwargs={"username": self.user1.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertQuerysetEqual(context["tweet_list"], Tweet.objects.filter(user=self.user1), ordered=False)

        ct_follower = FriendShip.objects.filter(following__exact=self.user1).count()
        self.assertEqual(context["followers_num"], ct_follower)
        ct_following = FriendShip.objects.filter(follower__exact=self.user1).count()
        self.assertEqual(context["followings_num"], ct_following)


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
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test",
            email="test@expample",
            password="password1",
        )
        self.user2 = User.objects.create_user(
            username="test2",
            email="test2@example",
            password="password2",
        )
        self.client.login(username="test", password="password1")

    def test_success_post(self):
        url = reverse("accounts:follow", kwargs={"username": self.user2.username})
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(FriendShip.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_failure_post_with_not_exist_user(self):
        url = reverse("accounts:follow", kwargs={"username": "unknown"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_self(self):
        url = reverse("accounts:follow", kwargs={"username": self.user1.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(FriendShip.objects.exists())


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test1",
            email="test@example",
            password="password1",
        )
        self.user2 = User.objects.create_user(
            username="test2",
            email="test2@example",
            password="password2",
        )
        self.client.login(username="test1", password="password1")
        FriendShip.objects.create(follower=self.user1, following=self.user2)

    def test_success_post(self):
        url = reverse("accounts:unfollow", kwargs={"username": self.user2.username})
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_not_exist_user(self):
        url = reverse("accounts:follow", kwargs={"username": "unknown"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(FriendShip.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_failure_post_with_self(self):
        url = reverse("accounts:unfollow", kwargs={"username": self.user1.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test1",
            email="test1@example",
            password="password1",
        )
        self.user2 = User.objects.create_user(
            username="test2",
            email="test2@example",
            password="password2",
        )
        self.client.login(username="test1", password="password1")
        FriendShip.objects.create(follower=self.user2, following=self.user1)
        self.url = reverse("accounts:following_list", kwargs={"username": self.user1.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/following_list.html")


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="test1@test.com",
            password="testpassword1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@test.com",
            password="testpassword2",
        )
        self.client.login(username="testuser1", password="testpassword1")
        FriendShip.objects.create(follower=self.user1, following=self.user2)
        self.url = reverse("accounts:follower_list", kwargs={"username": self.user1.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/follower_list.html")
