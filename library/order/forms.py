from django import forms
from .models import Order
from authentication.models import CustomUser
from book.models import Book
from django.forms import ModelForm

class DateInputWidget(forms.DateTimeInput):
    input_type = 'datetime-local'

class CreateOrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)
        user = [(user_item.id, user_item.first_name) for user_item in CustomUser.objects.all()]
        self.fields['user'] = forms.ChoiceField(choices=user)
        book = [(book_item.id, book_item.name) for book_item in Book.objects.all()]
        self.fields['book'] = forms.ChoiceField(choices=book)

    class Meta:
        model = Order
        fields = ('book', 'user', 'plated_end_at')
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'user': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'plated_end_at': DateInputWidget()
        }


class SearchOrderForm(forms.Form):
    input = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control me-2", 'type': "search", 'placeholder': "Search", 'aria-label': "Search"}))