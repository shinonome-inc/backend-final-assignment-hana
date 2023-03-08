# from django import forms
from django.forms import ModelForm

from .models import Tweet


class TweetForm(ModelForm):
    class Meta:
        model = Tweet
        fields = ("content",)

    # content = forms.CharField(
    # max_length=140,
    # widget=forms.Textarea(attrs={"rows": 5, "cols": 40, "placeholder": "いまなにしてる？"}),
    # )

    # class Meta:
    # model = Tweet
    # fields = ("content",)
