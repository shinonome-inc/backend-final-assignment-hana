from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView, TemplateView

from tweets.models import Tweet

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


class UserProfileView(LoginRequiredMixin, ListView):
    template_name = "accounts/profile.html"
    model = Tweet
    context_object_name = "tweets_list"

    def get_queryset(self):
        return Tweet.objects.select_related("user").filter(user__username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        context = super().get_context_data(**kwargs)
        context["username"] = user.username
        context["followers_numbers"] = FriendShip.objects.filter(following=self.object.user).count()
        context["following_numbers"] = FriendShip.objects.filter(follower=self.object.user).count()
        context["isfollowing"] = self.request.user.following.filter(
            username=user.username,
        ).exists()
        return context


class FollowView(LoginRequiredMixin, RedirectView):
    pass
    """ url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        if target_user == self.request.user:
            messages.add_message(request, messages.ERROR, "自分自身をフォローすることはできません。")
            return HttpResponseBadRequest("you cannnot follow yourself.")
        elif self.request.user.following.filter(username=target_user.username).exists():
            messages.add_message(request, messages.INFO, "既にフォローしています。")
        else:
            self.request.user.following.add(target_user)
            messages.add_message(request, messages.SUCCESS, "フォローしました。")
        return super().post(request, *args, **kwargs) """


class UnFollowView(LoginRequiredMixin, RedirectView):
    pass
    """  url = reverse_lazy("tweets:home")

    def post(self, request, *args, **kwargs):
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        if target_user == self.request.user:
            messages.add_message(request, messages.ERROR, "自分自身をフォロー解除することはできません。")
            return HttpResponseBadRequest("you cannot unfollow yourself.")
        elif self.request.user.following.filter(username=target_user.username).exists():
            self.request.user.following.remove(target_user)
            messages.add_message(request, messages.SUCCESS, "フォロー解除しました。")
        else:
            messages.add_message(request, messages.INFO, "このユーザーをフォローしていません。")
        return super().post(request, *args, **kwargs)"""


class FollowingListView(LoginRequiredMixin, TemplateView):
    pass
    """ template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        target_user = get_object_or_404(
            User,
            username=self.kwargs.get("username"),
        )
        context = super().get_context_data(**kwargs)
        context["following_list"] = target_user.follower.order_by("-created_at")
        return context
 """


class FollowerListView(LoginRequiredMixin, TemplateView):
    pass
    """ template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        target_user = get_object_or_404(
            User,
            username=self.kwargs.get("username"),
        )
        context = super().get_context_data(**kwargs)
        context["follower_list"] = target_user.following.order_by("-created_at")
        return context
 """
