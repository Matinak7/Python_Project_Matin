from django.forms import ModelForm

from products.models import Product


class ProductForm(forms.Form):
    name = forms.CharField()

    #class Meta:
    #    model = Product
    #    fields = '__all__'