"""TimeRange class for handling time ranges"""
from typing import Optional
from datetime import datetime

class TimeRange:
    """Class to handle time ranges"""
    
    def __init__(self, starttype: str = None, stoptype: str = None, 
                 startts: int = None, stopts: int = None):
        self.starttype = starttype
        self.stoptype = stoptype
        self.startts = startts
        self.stopts = stopts
