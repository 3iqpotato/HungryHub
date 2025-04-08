from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account


class AccountRegistrationForm(UserCreationForm):
    type = forms.ChoiceField(choices=Account.ACCOUNT_TYPES)

    class Meta:
        model = Account
        fields = ('email', 'password1', 'password2', 'type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['username'].required = False  # username не е задължителен