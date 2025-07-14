from googlexport.report.repository import ExporterRepository
from googlexport.api.spreadsheet.spreadsheet import GoogleSpreadsheet
from googlexport.api.spreadsheet.sheet import GoogleSheet, SheetNotFoundError
from googlexport.api.spreadsheet.range import SheetRange, SetSheetRangeRequest, WipeSheetRequest, MergeSheetRangeRequest
from models.report import ReportType, Report
from models.event import Event
from uuid import UUID

class ReportExporter:
    defaultRows = 50
    defaultColumns = 50

    eventInfoRowOffset = 0
    eventInfoColumnOffset = 0
    reportsTableRowOffset = 0
    reportsTableColumnOffset = 2

    def __init__(self, spreadsheet: GoogleSpreadsheet, storage: ExporterRepository):
        if not isinstance(spreadsheet, GoogleSpreadsheet):
            raise ValueError("spreadsheet must be an instance of GoogleSpreadsheet")
        
        if not isinstance(storage, ExporterRepository):
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
        
        await self._wipeSheet(sheet)
        await self._eventInfo(event, sheet, self.eventInfoRowOffset, self.eventInfoColumnOffset)
        await self._reportsTable(reports, sheet, self.reportsTableRowOffset, self.reportsTableColumnOffset)

        await sheet.Sync()


    async def _wipeSheet(self, sheet: GoogleSheet):
        sheet.AddRequest(WipeSheetRequest(sheet))
        

    async def _eventInfo(self, event: Event, sheet: GoogleSheet, rowOffset: int, columnOffset: int):
        sheetRange = SheetRange(sheet, rowOffset, columnOffset, rowOffset + 9, columnOffset + 2)
        # Информация о меро
        sheet.AddRequest(MergeSheetRangeRequest(sheetRange.SubRange(0, 0, 1, 2)))

        # Активисты
        sheet.AddRequest(MergeSheetRangeRequest(sheetRange.SubRange(7, 0, 8, 2)))

        sheetRange.setValueFromZero(0, 0, "Информация о мероприятии")
        sheetRange.setValueFromZero(1, 0, "Название")
        sheetRange.setValueFromZero(1, 1, event.Name)
        sheetRange.setValueFromZero(2, 0, "Место")
        sheetRange.setValueFromZero(2, 1, event.Place)
        sheetRange.setValueFromZero(3, 0, "Время")
        sheetRange.setValueFromZero(3, 1, event.Date.strftime("%d-%m-%Y %H:%M"))
        sheetRange.setValueFromZero(4, 0, "Фото")
        sheetRange.setValueFromZero(4, 1, str(event.PhotoCount))
        sheetRange.setValueFromZero(5, 0, "Видео")
        sheetRange.setValueFromZero(5, 1, str(event.VideoCount))
        sheetRange.setValueFromZero(6, 0, "Ответственный")
        sheetRange.setValueFromZero(6, 1, event.Chief.Activist.Name)
        sheetRange.setValueFromZero(7, 0, "Активисты")
        for i, act in enumerate(event.Activists):
            sheetRange.AddRow()
            sheetRange.setValueFromZero(8 + i, 0, str(i + 1))
            sheetRange.setValueFromZero(8 + i, 1, act.Activist.Name)

        sheet.AddRequest(SetSheetRangeRequest(sheetRange))
    

    async def _reportsTable(self, reports: list[Report], sheet: GoogleSheet, rowOffset: int, columnOffset: int):
        # Header
        sheetRange = SheetRange(sheet, rowOffset, columnOffset, rowOffset + 2, columnOffset + 5)


        sheet.AddRequest(MergeSheetRangeRequest(sheetRange.SubRange(0, 0, 1, 5)))

        sheetRange.setValueFromZero(0, 0, "Отчёты")
        sheetRange.setValueFromZero(1, 0, "№")
        sheetRange.setValueFromZero(1, 1, "Тип")
        sheetRange.setValueFromZero(1, 2, "Ссылка")
        sheetRange.setValueFromZero(1, 3, "Активист")
        sheetRange.setValueFromZero(1, 4, "Дата создания")

        # Body
        for i, report in enumerate(reports):
            sheetRange.AddRow()
            sheetRange.setValueFromZero(i + 2, 0, str(i + 1))
            reportType = ""
            match report.Type:
                case ReportType.Photo:
                    reportType = "Фото"
                case ReportType.Video:
                    reportType = "Видео"
            sheetRange.setValueFromZero(i + 2, 1, reportType)
            sheetRange.setValueFromZero(i + 2, 2, report.URL)
            sheetRange.setValueFromZero(i + 2, 3, report.Activist.Name)
            sheetRange.setValueFromZero(i + 2, 4, report.CreatedAt.strftime("%d-%m-%Y %H:%M"))
        
        sheet.AddRequest(SetSheetRangeRequest(sheetRange))



        
