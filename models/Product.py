class Product:

    def __init__(self, id, name, price, stock, size, category, distributor, store):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.size = size
        self.category = category
        self.distributor = distributor
        self.store = store

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.name,
            'stock': self.stock,
            'size': self.size,
            'categoy': self.category,
            'distributor': self.distributor,
            'store': self.store
        }