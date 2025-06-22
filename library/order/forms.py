from django import forms
from .models import Order


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'created_at': forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                              attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'plated_end_at': forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                 attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_at': forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                          attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


class OrderSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by Order ID, Date, Book, Author, User Email or Name',
            'class': 'form-control me-2',
            'aria-describedby': 'searchHelp',
        }),
    )


class CloseOrdersForm(forms.Form):
    selected_orders = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    page = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    q = forms.CharField(widget=forms.HiddenInput(), required=False)
