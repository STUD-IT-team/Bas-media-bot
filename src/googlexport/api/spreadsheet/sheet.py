from __future__ import annotations
from typing import Callable
from googlexport.api.spreadsheet.spreadsheet import GoogleSpreadsheet
from utils.create_method import withCreate

class GoogleSheet:
    def __init__(self, spreadsheet: GoogleSpreadsheet, properties: dict):
        if not isinstance(spreadsheet, GoogleSpreadsheet):
            raise ValueError("spreadsheet must be an instance of GoogleSpreadsheet")
        
        if not isinstance(properties, dict):
            raise ValueError("properties must be a dict")
        
        self._spreadsheet = spreadsheet
        self._id = properties['properties']['sheetId']
        self._title = properties['properties']['title']
        self._index = properties['properties']['index']
        self._rowCount = properties['properties']['gridProperties']['rowCount']
        self._columnCount = properties['properties']['gridProperties']['columnCount']

        self._updateRequests = []
    
    @staticmethod
    def ById(spreadsheet: GoogleSpreadsheet, sheetId: str) -> GoogleSheet:
        if not isinstance(spreadsheet, GoogleSpreadsheet):
            raise ValueError("spreadsheet must be an instance of GoogleSpreadsheet")
        
        if not isinstance(sheetId, str):
            raise ValueError("sheetId must be a string")
        
        sheet = spreadsheet._sheetById(sheetId)
        if sheet is None:
            raise ValueError("sheetId does not exist")
        
        return GoogleSheet(spreadsheet, sheet)
    
    @staticmethod
    def ByTitle(spreadsheet: GoogleSpreadsheet, title: str) -> GoogleSheet:
        if not isinstance(spreadsheet, GoogleSpreadsheet):
            raise ValueError("spreadsheet must be an instance of GoogleSpreadsheet")
        
        if not isinstance(title, str):
            raise ValueError("title must be a string")
        
        sheet = spreadsheet._sheetByTitle(title)
        if sheet is None:
            raise SheetNotFoundError("title does not exist")
        
        return GoogleSheet(spreadsheet, sheet)
    
    def AddRequest(self, request: SheetRequest):
        if not isinstance(request, SheetRequest):
            raise ValueError("request must be an instance of SheetRequest")
        
        self._updateRequests.append(request)
    
    async def Sync(self):
        reqs = []
        def _addRequestCallback(request: dict):
            reqs.append(request)
        
        for request in self._updateRequests:
            request._requestCallback(self, _addRequestCallback)
        
        resp = self._spreadsheet._sheetUpdate(reqs)
        self._updateRequests = []
        return await resp
    
    @property
    def id(self):
        return self._id
    
    @property
    def title(self):
        return self._title
    
    @property
    def rowCount(self):
        return self._rowCount
    
    @property
    def columnCount(self):
        return self._columnCount

class SheetRequest:
    def _dictRequest(self, googleSheet: GoogleSheet):
        raise NotImplementedError
    
    def _requestCallback(self, googleSheet: GoogleSheet, callback: Callable[[dict], None]):
        callback(self._dictRequest(googleSheet))

@withCreate
class UpdateSheetTitleRequest(SheetRequest):
    def __init__(self, title: str):
        if not isinstance(title, str):
            raise ValueError("title must be a string")
        
        self._title = title
    
    def _dictRequest(self, googleSheet: GoogleSheet):
        return {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': googleSheet._id,
                    'title': self._title
                },
                'fields': 'title'
            }
        }

@withCreate 
class AddSheetRowsRequest(SheetRequest):
   def __init__(self, rows: int):
       if not isinstance(rows, int):
           raise ValueError("rows must be an int")
       
       self._rows = rows
          
   def _dictRequest(self, googleSheet: GoogleSheet):
       return {
           'updateSheetProperties': {
               'properties': {
                   'sheetId': googleSheet._id,
                   'gridProperties': {
                       'rowCount': googleSheet._rowCount + self._rows
                   }
               },
               'fields': 'gridProperties.rowCount'
           }
       }

@withCreate
class AddSheetColumnsRequest(SheetRequest):
  def __init__(self, columns: int):
      if not isinstance(columns, int):
          raise ValueError("columns must be an int")
      
      self._columns = columns
  
  def _dictRequest(self, googleSheet: GoogleSheet):
      return {
          'updateSheetProperties': {
              'properties': {
                  'sheetId': googleSheet._id,
                  'gridProperties': {
                      'columnCount': googleSheet._columnCount + self._columns
                  }
              },
              'fields': 'gridProperties.columnCount'    
          }
      }
    

class SheetNotFoundError(Exception):
    pass