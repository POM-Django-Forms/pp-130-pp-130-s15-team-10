from django import forms
from .models import Order
from book.models import Book

class OrderSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control me-2 flex-grow-1',
            'type': 'search',
            'name': 'q',
            'placeholder': 'Search by Order ID, Date, Book, Author, User Email or Name',
            'aria-describedby': 'searchHelp',
        })
    )


class CloseOrdersForm(forms.Form):
    selected_orders = forms.MultipleChoiceField(
        required=False,
        widget=forms.MultipleHiddenInput()
    )


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['book', 'term']

    user = forms.CharField(widget=forms.HiddenInput(), initial='')
    book = forms.ModelChoiceField(queryset=Book.objects.all(), label="Select Book", empty_label="Please choose a book")
    term = forms.IntegerField(min_value=1, label="Order Duration (days)", widget=forms.NumberInput(attrs={'placeholder': 'Enter number of days'}))

    def clean_term(self):
        term = self.cleaned_data.get('term')
        if term <= 0:
            raise forms.ValidationError("Term must be greater than 0.")
        return term
