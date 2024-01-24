from ast import literal_eval as ev

a = (1,'vert')
b = str(a)
c = b.encode()

def decodet(message):
    """
    Permet de récuper directement un tuple à partir des données reçue dans la messagequeue
    """
    return ev(message.decode())


print(decodet(c))
