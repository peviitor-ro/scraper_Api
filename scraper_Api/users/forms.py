from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'company', 'scraper',
                  'is_active', 'is_staff', 'is_superuser']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()  # Nu setează parolă
        if commit:
            user.save()
            self.save_m2m()  # Salvează relațiile ManyToMany
        return user
