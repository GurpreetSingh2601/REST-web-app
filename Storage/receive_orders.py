from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class ReceivedOrders(Base):
    
    __tablename__ = "receive_orders"

    id = Column(Integer, primary_key=True)
    order_date = Column(String(100), nullable=False)
    order_number = Column(String(250), nullable=False)
    part_number = Column(Integer, nullable=False)
    part_price = Column(Integer, nullable=False)
    part_quantity = Column(Integer, nullable=False)
    part_type = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    

    def __init__(self, order_date, order_number, part_number,part_price ,part_quantity, part_type, trace_id):
        self.order_date = order_date
        self.order_number = order_number
        self.part_number = part_number
        self.part_price = part_price
        self.part_quantity = part_quantity
        self.part_type = part_type
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['order_date'] = self.order_date
        dict['order_number'] = self.order_number
        dict['part_number'] = self.part_number
        dict['part_price'] = self.part_price
        dict['part_quantity'] = self.part_quantity
        dict['part_type'] = self.part_type
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict