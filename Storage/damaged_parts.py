from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class DamagedParts(Base):
    
    __tablename__ = "damaged_parts"

    id = Column(Integer, primary_key=True)
    damage_cost = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    part_number = Column(Integer, nullable=False)
    part_type = Column(String(250), nullable=False)
    damaged_part_qty = Column(Integer, nullable=False)
    damage_description = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    order_date = Column(String(250), nullable=False)
    order_number = Column(String(250), nullable=False)


    def __init__(self, order_number, order_date, part_number, damage_cost, part_type, damaged_part_qty, damage_description, trace_id):
        """ Initializes a blood pressure reading """
        self.damage_cost = damage_cost
        self.damage_description = damage_description
        self.damaged_part_qty = damaged_part_qty
        self.order_date = order_date
        self.order_number = order_number
        self.part_number = part_number
        self.part_type = part_type
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        

    def to_dict(self):
        """ Dictionary Representation of a blood pressure reading """
        dict = {}
        dict['id'] = self.id
        dict['damage_cost'] = self.damage_cost
        dict['damage_description'] = self.damage_description
        dict['damaged_part_qty'] = self.damaged_part_qty
        dict['order_date'] = self.order_date
        dict['order_number'] = self.order_number
        dict['part_number'] = self.part_number
        dict['part_type']= self.part_type
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created
        
        

        return dict