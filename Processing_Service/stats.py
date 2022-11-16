from sqlalchemy import Column, Integer, String, DateTime
from base import Base
class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_orders = Column(Integer, nullable=False)
    max_part_price = Column(Integer, nullable=True)
    max_part_number = Column(Integer, nullable=True)
    num_damaged_part = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_orders, max_part_price, max_part_number, num_damaged_part,last_updated):
        """ Initializes a processing statistics objet """
        self.num_orders = num_orders
        self.max_part_price = max_part_price
        self.max_part_number = max_part_number
        self.num_damaged_part = num_damaged_part
        self.last_updated = last_updated
        

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_orders'] = self.num_orders
        dict['max_part_price'] = self.max_part_price
        dict['max_part_number'] = self.max_part_number
        dict['num_damaged_part'] = self.num_damaged_part
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f") #07/28/2014 18:54:55.099
        
        return dict
    
        