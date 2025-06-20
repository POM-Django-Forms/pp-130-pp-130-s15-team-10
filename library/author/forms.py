from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re

from django.forms import formset_factory

from .models import Author
from book.models import Book


class CreateOrUpdateAuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'surname', 'patronymic', 'source_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'source_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'First Name',
            'surname': 'Last Name',
            'patronymic': 'Patronymic',
            'source_url': 'Author Source URL',
        }

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get('name', '').strip()
        surname = cleaned_data.get('surname', '').strip()
        patronymic = cleaned_data.get('patronymic', '').strip()
        author_url = cleaned_data.get('source_url', '').strip()

        if not (name or surname or patronymic):
            raise ValidationError("Please fill at least one of the fields: name, surname, or patronymic.")

        for value, field in [(name, 'name'), (surname, 'surname'), (patronymic, 'patronymic')]:
            if value and re.search(r'\d', value):
                self.add_error(field, "This field cannot contain digits.")

        cleaned_data['name'] = name.capitalize()
        cleaned_data['surname'] = surname.capitalize()
        cleaned_data['patronymic'] = patronymic.capitalize()

        for value, field in [(name, 'name'), (surname, 'surname'), (patronymic, 'patronymic')]:
            if value and len(value) > 20:
                self.add_error(field, 'Maximum length is 20 characters.')

        if author_url:
            parsed = urlparse(author_url)
            if parsed.scheme not in ['http', 'https'] or not parsed.netloc:
                self.add_error('source_url', 'Invalid author URL.')

        if name and surname:
            existing = Author.objects.filter(
                name__iexact=name,
                surname__iexact=surname,
                patronymic__iexact=patronymic or None
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error(None, "Author with the same name, surname, and patronymic already exists.")

        return cleaned_data


class AuthorBookForm(forms.Form):
    title = forms.CharField(
        required=True,
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title'})
    )
    source_url = forms.URLField(
        required=False,
        max_length=255,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Book Source URL'})
    )

    def clean_source_url(self):
        title = self.cleaned_data.get('title', '').strip()
        url = self.cleaned_data.get('source_url', '').strip()

        if url and not title:
            self.add_error('title', 'Book title is required when book source URL is provided.')

        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https'] or not parsed.netloc:
                raise forms.ValidationError('Invalid book URL.')
        return url


AuthorBookFormSet = formset_factory(AuthorBookForm, extra=1)
