from django import forms
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re
from .models import Author
from book.models import Book
from utils.cleaning import clean_str_field


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

        name = clean_str_field(cleaned_data.get('name'))
        surname = clean_str_field(cleaned_data.get('surname'))
        patronymic = clean_str_field(cleaned_data.get('patronymic'))
        author_url = clean_str_field(cleaned_data.get('source_url'))

        if not (name or surname or patronymic):
            raise ValidationError("Please fill at least one of the fields: name, surname, or patronymic.")

        for value, field in [(name, 'name'), (surname, 'surname'), (patronymic, 'patronymic')]:
            if value and re.search(r'\d', value):
                self.add_error(field, "This field cannot contain digits.")

        for value, field in [(name, 'name'), (surname, 'surname'), (patronymic, 'patronymic')]:
            if value and len(value) > 20:
                self.add_error(field, 'Maximum length is 20 characters.')

        if author_url:
            parsed = urlparse(author_url)
            if parsed.scheme not in ['http', 'https'] or not parsed.netloc:
                self.add_error('source_url', 'Invalid author URL.')
            elif len(author_url) > 255:
                self.add_error('source_url', 'URL is too long.')

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

        cleaned_data['name'] = name.capitalize()
        cleaned_data['surname'] = surname.capitalize()
        cleaned_data['patronymic'] = patronymic.capitalize()

        return cleaned_data


class AuthorSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, surname or patronymic',
            'class': 'form-control me-2',
            'aria-describedby': 'searchHelp',
        })
    )


class DeleteAuthorForm(forms.Form):
    author = forms.ModelChoiceField(
        queryset=Author.objects.filter(is_deleted=False),
        empty_label="-- Please choose an author --",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select custom-select-lg',
            'style': 'min-height: 48px;'
        }),
        label='Author',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].label_from_instance = lambda obj: f"{obj.name} {obj.surname} {obj.patronymic}"
