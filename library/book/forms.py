from datetime import datetime
from urllib.parse import urlparse
from author.models import Author
from django import forms
from .models import Book
from django.forms import formset_factory
from utils.cleaning import clean_str_field


class BookSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control me-2',
            'placeholder': 'Search by title, author or count'
        })
    )


class BookLimitedUpdateForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['count', 'source_url', 'date_of_issue']
        widgets = {
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
            'source_url': forms.URLInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'count': 'Count',
            'source_url': 'Source URL',
            'date_of_issue': 'Date of Issue',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class CreateOrUpdateBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'description', 'count', 'publication_year', 'source_url', 'date_of_issue']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'required': True}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1947, 'required': True}),
            'source_url': forms.URLInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': 'Book Title',
            'description': 'Description',
            'count': 'Available Count',
            'publication_year': 'Year of Publication',
            'source_url': 'Book Source URL',
            'date_of_issue': 'Date of Issue',
        }

    def clean(self):
        cleaned_data = super().clean()

        name = clean_str_field(cleaned_data.get('name'))
        source_url = clean_str_field(cleaned_data.get('source_url'))

        if len(name) > 128:
            self.add_error('name', "Maximum length is 128 characters.")

        count = cleaned_data.get('count')
        if count is not None and count < 1:
            self.add_error('count', "Count must be more or equal 1.")

        if source_url:
            parsed = urlparse(source_url)
            if parsed.scheme not in ['http', 'https'] or not parsed.netloc:
                self.add_error('source_url', 'Invalid source URL.')
            elif len(source_url) > 255:
                self.add_error('source_url', 'URL is too long.')

        pub_year = cleaned_data.get('publication_year')
        if pub_year and pub_year > datetime.now().year:
            self.add_error('publication_year', "Publication year can't be in the future.")

        date_of_issue = cleaned_data.get('date_of_issue')
        if date_of_issue and date_of_issue > datetime.now().date():
            self.add_error('date_of_issue', "Date of issue can't be in the future.")

        cleaned_data['name'] = name.capitalize()

        return cleaned_data


class DeleteBookForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(is_deleted=False),
        empty_label="-- Please choose a book --",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select custom-select-lg',
            'style': 'min-height: 48px;'
        }),
        label='Book',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book'].label_from_instance = lambda \
                obj: f"{obj.name} ({', '.join(a.surname for a in obj.authors.all())})"


class AuthorForm(forms.Form):
    author = forms.ModelChoiceField(
        queryset=Author.objects.filter(is_deleted=False),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select d-inline-block', 'style': 'width: calc(100% - 40px);'}),
        label=''
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].label_from_instance = lambda obj: f"{obj.name} {obj.surname} {obj.patronymic}"


AuthorFormSet = formset_factory(AuthorForm, extra=1, can_delete=True)
