from django.http import JsonResponse
from products.forms import ProductForm
from products.models import Products
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_products(request):
    if request.method == 'GET':
        return JsonResponse(list(Products.objects.all().values('name','price')),safe=False)
    elif request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
             form.save()
        return JsonResponse({'result':'okay'})
    return JsonResponse({'error': 'not okay'})
