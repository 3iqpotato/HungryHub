from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account
from django.contrib.auth.forms import AuthenticationForm

class AccountRegistrationForm(UserCreationForm):
    type = forms.ChoiceField(choices=Account.ACCOUNT_TYPES)

    class Meta:
        model = Account
        fields = ('email', 'password1', 'password2', 'type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['username'].required = False  # username не е задължителен





class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # Променяме label да е Email, ако използваме email като username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Вашият email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Вашата парола'})