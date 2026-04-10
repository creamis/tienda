from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    return render(request, 'ventas/home.html')

@login_required
def particular(request):
    return render(request, 'ventas/particular.html')

@login_required
def empresa(request):
    return render(request, 'ventas/empresa.html')

@login_required
def fibra_movil(request):
    # Datos de ejemplo para tarifas de fibra + móvil sin televisión.
    # En una aplicación real, estos datos provendrían de una base de datos,
    # una API externa o un archivo de configuración.
    # He excluido las tarifas con TV como "Home Fútbol" y "Home Cristal"
    # según tu solicitud de "sin television".
    tariffs = [
        {
            'tag': 'ESENCIAL',
            'title': 'Home',
            'features': [
                'Fibra 600 Mb',
                'Móvil 500 min / 10GB',
                'Fijo incluido'
            ],
            'price': '40,00€',
            'highlight': False,
        },
        {
            'tag': 'OFERTA',
            'title': 'Home Conecta',
            'features': [
                'Fibra 300 Mb',
                'Móvil Ilimitado 5G',
                'Llamadas ilimitadas'
            ],
            'price': '35,95€',
            'highlight': False,
        },
        {
            'tag': 'MÁS GIGAS',
            'title': 'Home Ilimitado',
            'features': ['Fibra 1 Gb', 'Móvil Ilimitado 5G+', 'Fijo y 2ª línea gratis'],
            'price': '55,00€',
            'highlight': True, # Ejemplo de cómo destacar una tarifa sin TV
        },
    ]
    return render(request, 'ventas/fibra_movil.html', {'tariffs': tariffs})

@login_required
def solo_movil(request):
    # Tarifas extraídas de revista.orange.es (Solo móvil / Tarifas GO)
    tariffs = [
        {
            'tag': 'GIGAS FLEXIBLES',
            'title': 'Tarifa Go Flex',
            'features': [
                '100 GB acumulables',
                '5G+ a máxima velocidad',
                'Llamadas ilimitadas'
            ],
            'price': '15,00€',
            'highlight': False,
        },
        {
            'tag': 'MÁS VENDIDA',
            'title': 'Tarifa Go Max',
            'features': [
                'Gigas Ilimitados 5G+',
                'Streaming de video HD',
                'Roaming incluido en UE'
            ],
            'price': '35,00€',
            'highlight': True,
        },
        {
            'tag': 'ECONÓMICA',
            'title': 'Tarifa Go Esencial',
            'features': ['20 GB de datos', 'Llamadas ilimitadas', 'Ideal para uso básico'],
            'price': '12,00€',
            'highlight': False,
        },
    ]
    return render(request, 'ventas/solo_movil.html', {'tariffs': tariffs})

@login_required
def tienda(request):
    return render(request, 'ventas/tienda.html')
