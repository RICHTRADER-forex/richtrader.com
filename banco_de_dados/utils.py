import random

def gerar_iban():
    """ Gera um IBAN único de 22 dígitos começando com 'AO' """
    return "AO" + "".join([str(random.randint(0, 9)) for _ in range(20)])
