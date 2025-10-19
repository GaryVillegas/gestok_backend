class Product:

    def __init__(self, id, name, price, quantity, size, category, local):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.size = size
        self.category = category
        self.local = local
    
    #TODO: to_dict