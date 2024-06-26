from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from storage.settings import PERMISSION_CODE


class LoginUserForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('войти', 'Войти', css_class="btn btn-success mt-3"))

    username = forms.CharField(label='Логин', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('регистрация', 'Регистрация', css_class="btn btn-success mt-3"))

    username = forms.CharField(label='Логин')
    permission_code = forms.CharField(label='Код разрешения', widget=forms.PasswordInput())
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password1', 'password2']
        labels = {'email': 'E-mail',
                  'first_name': 'Имя',
                  'last_name': 'Фамилия'}
        # widgets = {'passwword1': forms.PasswordInput(attrs={'class': 'form-input'}),
        #            'passwword2': forms.PasswordInput(attrs={'class': 'form-input'}),
        #            'permission_code': forms.PasswordInput(attrs={'class': 'form-input'}),
        #            }

        # 'email': forms.TextInput(attrs={'class': 'form-input'}),
        #
        #            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
        #            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        # 'username': forms.TextInput(attrs={'class': 'form-input'})
    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Данный пользователь уже существует в базе.')
        return email

    def clean_permission_code(self):
        p_code = self.cleaned_data['permission_code']
        if p_code != PERMISSION_CODE:
            raise forms.ValidationError('Введите новый код разрешения.')
        return p_code


class ProfileUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('изменить', 'Изменить', css_class="btn btn-success mt-3"))

    username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(disabled=True, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {'first_name': 'Имя',
                  'last_name': 'Фамилия', }
        # widgets = {'first_name': forms.TextInput(attrs={'class': 'form-input'}),
        #            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        #            }


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('изменить пароль', 'Изменить пароль', css_class="btn btn-success mt-3"))

    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label='Подтверждение пароля',
                                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))
