from django import forms
from django.forms import modelformset_factory

from .models import Book
from author.models import Author


class AddBookForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Book
        fields = ['name', 'publication_year', 'count', 'source_url', 'date_of_issue']
        widgets = {
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
            'source_url': forms.URLInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name field cannot be empty.")
        return name

    def save(self, commit=True):
        book = super().save(commit=False)
        if commit:
            book.save()
        authors = self.cleaned_data.get('authors')
        if authors:
            book.authors.set(authors)
        if commit:
            self.save_m2m()
        return book


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
