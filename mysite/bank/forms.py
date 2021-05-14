from django import forms
from bank.models import Customers

class Trans_form(forms.Form):

    Amount = forms.FloatField(required=True)
    receiver=forms.ModelChoiceField(queryset=Customers.objects.all())




