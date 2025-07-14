from googlexport.api.client import GoogleServiceClient


class GoogleSpreadsheet:
    def __init__(self, serviceClient: GoogleServiceClient, spreadsheetId: str):
        if not isinstance(serviceClient, GoogleServiceClient):
            raise ValueError("serviceClient must be an instance of GoogleServiceClient")
        
        if not isinstance(spreadsheetId, str):
            raise ValueError("spreadsheetId must be a string")
        
        self._service = serviceClient.GetService('sheets', 'v4')
        self._spreadsheetId = spreadsheetId

        self._title = None
        self._url = None
        self._sheets = None

        self._updateProperties()
    
    def _updateProperties(self):
        spreadsheet = self._service.spreadsheets().get(spreadsheetId=self._spreadsheetId).execute()
        self._title = spreadsheet['properties']['title']
        self._url = spreadsheet['spreadsheetUrl']
        self._sheets = spreadsheet['sheets']
    
    @property
    def title(self):
        return self._title
    
    @property
    def url(self):
        return self._url
    
    def _sheetByTitle(self, title: str) -> dict:
        self._updateProperties()

        for sheet in self._sheets:
            if sheet['properties']['title'] == title:
                return sheet
        
        return None

    def _sheetById(self, sheetId: str) -> dict:
        self._updateProperties()

        for sheet in self._sheets:
            if sheet['properties']['sheetId'] == sheetId:
                return sheet
        
        return None

    async def _sheetUpdate(self, request):
        req = self._service.spreadsheets().batchUpdate(spreadsheetId=self._spreadsheetId, body={
            'requests': [
                request
            ]
        })
        
        resp = req.execute()
        self._updateProperties()
        return resp

    def AddSheet(self, title: str, rows: int, columns: int):
        if not isinstance(title, str):
            raise ValueError("title must be a string")
        
        if not isinstance(rows, int):
            raise ValueError("rows must be an int")
        
        if not isinstance(columns, int):
            raise ValueError("columns must be an int")

        if self._sheetByTitle(title) is not None:
            raise SheetAlreadyExists(f"Sheet with title {title} already exists")

        req = self._service.spreadsheets().batchUpdate(spreadsheetId=self._spreadsheetId, body={
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': title,
                            'gridProperties': {
                                'rowCount': rows,
                                'columnCount': columns
                            }
                        }
                    }
                }
            ]
        })

        resp = req.execute()
        self._updateProperties()

class SheetAlreadyExists(ValueError):
    pass

    
    
