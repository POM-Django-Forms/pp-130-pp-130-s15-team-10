from django import forms
from .models import Author
from book.models import Book
from django.forms import ModelForm

class CreateAuthorForm(ModelForm):
    checkbox = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        super(CreateAuthorForm, self).__init__(*args, **kwargs)
        books = [(book.id, book.name) for book in Book.objects.all()]
        self.fields['books'] = forms.ChoiceField(choices=books)

    class Meta:
        model = Author
        fields = ('name', 'surname', 'patronymic', 'books', 'checkbox')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'surname': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'books': forms.Select(attrs={'class': 'form-control form-control-lg'})
        }