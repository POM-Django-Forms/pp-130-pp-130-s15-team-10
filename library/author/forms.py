from book.models import Book
from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import Author


class CreateAuthorForm(forms.ModelForm):
    book_title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    book_source_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Author
        fields = ('name', 'surname', 'patronymic', 'author_source_url')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter author's name"}),
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter surname"}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter patronymic"}),
            'author_source_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name', '').strip()
        surname = cleaned_data.get('surname', '').strip()
        patronymic = cleaned_data.get('patronymic', '').strip()

        if not (name or surname or patronymic):
            raise ValidationError("Please fill at least one of the fields: name, surname, or patronymic.")

        book_title = cleaned_data.get('book_title', '').strip()
        book_url = cleaned_data.get('book_source_url', '').strip()

        if book_url and not book_title:
            self.add_error('book_title', 'Book title is required when book source URL is provided.')

        return cleaned_data



class EditAuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'surname', 'patronymic', 'author_source_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
            }),
            'patronymic': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
            }),
            'author_source_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'First Name',
            'surname': 'Last Name',
            'patronymic': 'Patronymic',
        }

    def clean_name(self):
        return self.instance.name

    def clean_surname(self):
        return self.instance.surname

    def clean_patronymic(self):
        return self.instance.patronymic


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['date_of_issue']
        widgets = {
            'date_of_issue': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'date_of_issue': 'Publication Date',
        }


BookFormSet = modelformset_factory(
    Book,
    form=BookForm,
    fields=['date_of_issue'],
    extra=0,
    can_delete=False
)
