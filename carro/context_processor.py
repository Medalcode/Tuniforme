# carro/context_processor.py

def valor_total_carro(request):
    total = 0
    # Iterar sobre los elementos en el carro de la sesión
    for key, value in request.session['carro'].items():
        # Calcular el total sumando el precio multiplicado por la cantidad de cada artículo
        total = total + (float(value['precio']) * value['cantidad'])
    # Devolver el total calculado en un diccionario
    return {'valor_total_carro': total}