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
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(is_deleted=False),
        label="Select Book",
        empty_label="Please choose a book",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    term = forms.IntegerField(
        min_value=1,
        max_value=14,
        label="Order Duration (days)",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter number of days', 'class': 'form-control'})
    )

    def clean_term(self):
        term = self.cleaned_data.get('term')
        if term < 1 or term > 14:
            raise forms.ValidationError("Term must be between 1 and 14 days.")
        return term
