<<<<<<< HEAD
def cities(request):
    from .models import City
    return {
        'cities': City.objects.filter(is_active=True).order_by('order', 'name')
    }
=======
from .models import City

def cities(request):
    return {
        'cities': City.objects.filter(is_active=True).order_by('order', 'name')
    } 
>>>>>>> ef6c3be (새롭게 시작)
