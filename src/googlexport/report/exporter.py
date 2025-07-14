from googlexport.report.repository import ExporterRepository
from googlexport.api.spreadsheet import GoogleSpreadsheet, GoogleSheet
from googlexport.api.range import SheetRange, SetSheetRangeRequest, WipeSheetRequest, MergeSheetRangeRequest

class ReportExporter:
    defaultRows = 50
    defaultColumns = 50

    def __init__(spreadsheet: GoogleSpreadsheet, storage: ExporterRepository):
        if not isinstance(spreadsheet, GoogleSpreadsheet):
            raise ValueError("spreadsheet must be an instance of GoogleSpreadsheet")
        
        if not issubclass(storage, ExporterRepository):
            raise ValueError("storage must be an instance of ExporterRepository")
        
        self._spreadsheet = spreadsheet
        self._storage = storage
    
    async def ExportEvent(self, eventId: UUID):
        event = self._storage.GetEvent(eventId)
        if event is None:
            raise ValueError(f"Event with id {eventId} does not exist")
        
        reports = self._storage.GetEventReports(eventId)
        try:
            sheet = GoogleSheet.ByTitle(self._spreadsheet, event.Name)
        except SheetNotFoundError:
            self._spreadsheet.AddSheet(event.Name, self.defaultRows, self.defaultColumns)
            sheet = GoogleSheet.ByTitle(self._spreadsheet, event.Name)
        

    async def _eventInfo(self, event: Event, sheet: GoogleSheet, rowOffset: int, columnOffset: int):
        sheetRange = SheetRange(sheet, columnOffset, rowOffset, rowOffset + 9, columnOffset + 2)

        sheet.AddRequest(WipeSheetRequest(sheet))





        
