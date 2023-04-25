from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import HttpResponseRedirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, RedirectView

from tweets.models import Like, Tweet

from .forms import LoginForm, SignUpForm
from .models import FriendShip

User = get_user_model()


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


class LogoutView(auth_views.LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "accounts/profile.html"
    model = User
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user).order_by("-created_at")
        context["is_following"] = FriendShip.objects.filter(following=user, follower=self.request.user).exists()
        context["followings_num"] = FriendShip.objects.filter(follower=user).count()
        context["followers_num"] = FriendShip.objects.filter(following=user).count()
        user_like_list = (
            Like.objects.select_related("tweet").filter(user=self.request.user).values_list("tweet", flat=True)
        )
        context["user_liked_list"] = user_like_list
        return context


class FollowView(LoginRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])
        follower = request.user

        if following == follower:
            messages.warning(request, "自分自身はフォローできません。")
            return HttpResponseBadRequest(render(request, "error/400.html"))

        if FriendShip.objects.filter(following=following, follower=follower).exists():
            messages.warning(request, "すでにフォローしています。")
            return HttpResponseBadRequest(render(request, "error/400.html"))

        FriendShip.objects.create(following=following, follower=follower)
        return HttpResponseRedirect(reverse("tweets:home"))


class UnFollowView(LoginRequiredMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])
        follower = request.user
        unfollow = FriendShip.objects.filter(following=following, follower=follower)

        if following == follower:
            messages.warning(request, "自分自身を対象には出来ません。")
            return HttpResponseBadRequest(render(request, "error/400.html"))

        elif unfollow.exists():
            unfollow.delete()
            return HttpResponseRedirect(reverse("tweets:home"))
        else:
            messages.warning(request, "無効な操作です。")
            return HttpResponseBadRequest(render(request, "error/400.html"))


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "accounts/following_list.html"
    context_object_name = "following_list"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return FriendShip.objects.select_related("following").filter(follower=user).order_by("-created_at")


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "accounts/follower_list.html"
    context_object_name = "follower_list"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return FriendShip.objects.select_related("follower").filter(following=user).order_by("-created_at")
