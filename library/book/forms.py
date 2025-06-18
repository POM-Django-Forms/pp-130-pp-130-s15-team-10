from .models import Book
from django import forms
from author.models import Author
from django.forms import ModelForm


class CreateBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'description', 'count', 'title', 'publication_year', 'date_of_issue', 'authors']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year of Publication'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class BookFilterForm(forms.Form):
    QUERY_CHOICES = [
        ('user', 'User ID'),
        ('', 'Select'),
        ('name', 'Name'),
        ('count', 'Count'),
        ('author', 'Author')
    ]

    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search...'}),
        label="Search",
    )
    filter_by = forms.ChoiceField(
        choices=QUERY_CHOICES,
        required=False,
        label="Filter By",
        initial='name',
    )

class CreateBookForm(ModelForm):
    checkbox = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        super(CreateBookForm, self).__init__(*args, **kwargs)
        authors = [(author.id, author.name) for author in Author.objects.all()]
        self.fields['authors'] = forms.ChoiceField(choices=authors)

    class Meta:
        model = Book
        fields = ('name', 'description', 'count', 'photo')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-lg'}),
            'count': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'photo': forms.FileInput(attrs={'class': 'form-control form-control-lg'})
        }


class SearchBookForm(forms.Form):
    choices = [(0, 'Filter by'), (1, 'Author'), (2, 'Title'), (3, 'Description')]
    selector = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'form-control form-control-lg'}))
    input = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control me-2", 'type': "search", 'placeholder': "Search", 'aria-label': "Search"}))
