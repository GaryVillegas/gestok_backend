class Test():

    def __init__(self, id, text, created_at):
        self.id = id
        self.text = text
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at
        }