class ModDTO:
    def __init__(self, id: int, url_name: str):
        self.id = id
        self.url_name = url_name
        self.name = url_name.replace("_", " ")
        self.avg_offer = 0.0
        self.most_repeated_offer = 0.0
        self.avg_48h = 0.0
        self.amount_48 = 0
        self.avg_90d = 0.0
        self.amount_90 = 0