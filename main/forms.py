from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ActivityType, Route


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class RouteEditForm(forms.ModelForm):
    activity_type = forms.ModelChoiceField(
        queryset=ActivityType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Route
        fields = ['name', 'activity_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
