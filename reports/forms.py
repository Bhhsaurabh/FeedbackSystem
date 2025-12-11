from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import RoadFeedback, Comment

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class RoadFeedbackForm(forms.ModelForm):
    class Meta:
        model = RoadFeedback
        fields = ['road_name', 'location', 'state', 'city', 'condition', 
                 'issue_type', 'description', 'image']
        widgets = {
            'road_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'issue_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Add a public comment...'}),
        }

    def clean_text(self):
        txt = self.cleaned_data['text'].strip()
        if not txt:
            raise forms.ValidationError("Comment cannot be empty.")
        return txt
