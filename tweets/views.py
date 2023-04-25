from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .forms import TweetForm
from .models import Like, Tweet

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    ordering = "-created_at"
    queryset = model.objects.select_related("user").prefetch_related("likes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_like_list = (
            Like.objects.select_related("tweet").filter(user=self.request.user).values_list("tweet", flat=True)
        )
        context["user_liked_list"] = user_like_list
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/create.html"
    model = Tweet
    form_class = TweetForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    template_name = "tweets/detail.html"
    model = Tweet
    queryset = model.objects.select_related("user")


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "tweets/delete.html"
    model = Tweet
    success_url = reverse_lazy("tweets:home")
    queryset = model.objects.select_related("user")

    def test_func(self, **kwargs):
        tweet = self.get_object()
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *arg, **kwargs):
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        user = request.user
        Like.objects.get_or_create(user=user, tweet=tweet)
        like_count = tweet.likes.count()
        context = {
            "liked_count": like_count,
        }

        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *arg, **kwargs):
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        user = request.user
        like = Like.objects.filter(user=user, tweet=tweet)

        if like.exists():
            like.delete()

        like_count = tweet.likes.count()

        context = {
            "liked_count": like_count,
        }
        return JsonResponse(context)


# Create your views here.
