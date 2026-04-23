from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Enter post title..."}),
            "content": forms.Textarea(
                attrs={
                    "placeholder": "Write your post content here...",
                }
            ),
        }
