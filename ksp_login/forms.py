from django.contrib.auth.forms import (UserCreationForm,
    PasswordChangeForm as AuthPasswordChangeForm)
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.utils.translation import string_concat, ugettext_lazy as _
from social_auth.utils import setting

from ksp_login import SOCIAL_AUTH_PARTIAL_PIPELINE_KEY


class KspUserCreationForm(UserCreationForm):
    """
    A custom user creation form that can make the password fields
    optional.
    """
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        try:
            request = kwargs['request']
            del kwargs['request']
        except KeyError:
            raise TypeError("Argument 'request' missing.")
        try:
            pipeline_state = request.session[setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
                                                     SOCIAL_AUTH_PARTIAL_PIPELINE_KEY)]
            pipeline_state = pipeline_state['kwargs']
            self.password_required = False
        except KeyError:
            self.password_required = True
            pipeline_state = None
        if not args and 'initial' not in kwargs:
            kwargs['initial'] = self.get_initial_from_pipeline(pipeline_state)

        super(KspUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['password1'].help_text = _(
            "We recommend choosing a strong passphrase but we don't "
            "enforce any ridiculous constraints on your passwords."
        )

        if not self.password_required:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = string_concat(_(
                "Since you're logging in using an external provider, "
                "this field is optional; however, by supplying it, you "
                "will be able to log in using a password. "
            ), self.fields['password1'].help_text)

    def get_initial_from_pipeline(self, pipeline_state):
        """
        Returns a dictionary with initial field values extracted from the
        social_auth pipeline state.
        """
        return None if not pipeline_state else {
            'username': pipeline_state['username'],
            'first_name': pipeline_state['details']['first_name'],
            'last_name': pipeline_state['details']['last_name'],
            'email': pipeline_state['details']['email'],
        }

    def clean_password2(self):
        """
        We need to validate the submitted passwords if they are required
        or either has been submitted, otherwise the user account will be
        passwordless.
        """
        if (self.password_required or self.cleaned_data.get('password1') or
                self.cleaned_data.get('password2')):
            return super(KspUserCreationForm, self).clean_password2()
        return None

    def save(self, commit=True):
        """
        If a password was provided or is required, just delegate to the
        parent's save, otherwise explicitly set an unusable password.
        """
        user = super(KspUserCreationForm, self).save(commit=False)
        if not (self.cleaned_data.get('password1') or
                self.password_required):
            user.set_unusable_password()
        if commit:
            user.save()
        return user


class PasswordChangeForm(AuthPasswordChangeForm):
    """
    A form that lets a user change or optionally remove their password
    after entering their current password.
    """
    def __init__(self, password_required=True, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.password_required = password_required

        if not password_required:
            self.fields['new_password1'].required = False
            self.fields['new_password2'].required = False
            self.fields['new_password1'].help_text = _(
                "Leave this field empty to disable password-based access "
                "to your account."
            )

    def clean_new_password2(self):
        """
        We need to validate the submitted passwords if they are required
        or either has been submitted, otherwise the user account will be
        passwordless.
        """
        if (self.password_required or self.cleaned_data.get('new_password1') or
                self.cleaned_data.get('new_password2')):
            return super(PasswordChangeForm, self).clean_new_password2()
        return None

    def save(self, commit=True):
        """
        If a password was provided or is required, just delegate to the
        parent's save, otherwise explicitly set an unusable password.
        """
        user = super(PasswordChangeForm, self).save(commit=False)
        if not (self.cleaned_data.get('new_password1') or
                self.password_required):
            user.set_unusable_password()
        if commit:
            user.save()
        return user