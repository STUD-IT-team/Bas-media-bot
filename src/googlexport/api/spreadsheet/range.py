from typing import List
from googlexport.api.spreadsheet.sheet import GoogleSheet
from googlexport.api.spreadsheet.sheet import AddSheetRowsRequest, AddSheetColumnsRequest, SheetRequest
from utils.create_method import withCreate
from typing import Callable

class SheetRange:
    # start - inclusive, end - exclusive
    def __init__(self, sheet: GoogleSheet, startRow: int, startColumn: int, endRow: int, endColumn: int, valueMatrix: List[List[str]] = None, valueMatrixFromZero: List[List[str]] = None):
        if not isinstance(startRow, int):
            raise ValueError("startRow must be an int")
        
        if not isinstance(startColumn, int):
            raise ValueError("startColumn must be an int")
        
        if not isinstance(endRow, int):
            raise ValueError("endRow must be an int")
        
        if not isinstance(endColumn, int):
            raise ValueError("endColumn must be an int")
        
        if startRow >= endRow or startColumn >= endColumn:
            raise ValueError("startRow and startColumn must be less than endRow and endColumn")
        
        self._sheet = sheet
        self._startRow = startRow
        self._startColumn = startColumn
        self._endRow = endRow
        self._endColumn = endColumn
        if valueMatrix is None:
            self._valueMatrix = [[""]* (endColumn - startColumn) for _ in range(endRow - startRow)]
        elif len(valueMatrix) != (endRow - startRow) or len(valueMatrix[0]) != (endColumn - startColumn):
            for row in valueMatrix:
                if len(row) != (endColumn - startColumn):
                    row.extend(["" for _ in range(endColumn - startColumn - len(row))])
            
            for _ in range(endRow - startRow - len(valueMatrix)):
                valueMatrix.append(["" for _ in range(endColumn - startColumn)])
            
            self._valueMatrix = valueMatrix
        else:
            self._valueMatrix = valueMatrix
    
    # end - exclusive
    def SubRange(self, startRowOffset: int, startColumnOffset: int, endRowOffset: int, endColumnOffset: int):
        if not isinstance(startRowOffset, int):
            raise ValueError("startRowOffset must be an int")
        
        if not isinstance(startColumnOffset, int):
            raise ValueError("startColumnOffset must be an int")
        
        if not isinstance(endRowOffset, int):
            raise ValueError("endRowOffset must be an int")
        
        if not isinstance(endColumnOffset, int):
            raise ValueError("endColumnOffset must be an int")
        
        if startRowOffset < 0 or startColumnOffset < 0 or endRowOffset < 0 or endColumnOffset < 0:
            raise ValueError("startRowOffset, startColumnOffset, endRowOffset and endColumnOffset must be positive or zero int")
        
        if startRowOffset >= self.endRow or startColumnOffset >= self.endColumn or endRowOffset >= self.endRow or endColumnOffset >= self.endColumn:
            raise ValueError("startRowOffset, startColumnOffset, endRowOffset and endColumnOffset must be less than endRow and endColumn")
        
        subMatrix = [self._valueMatrix[i][startColumnOffset:endColumnOffset] for i in range(startRowOffset, endRowOffset)]
        return SheetRange(self._sheet, self._startRow + startRowOffset, self._startColumn + startColumnOffset, self._startRow + endRowOffset, self._startColumn + endColumnOffset, subMatrix)                                 

    def Address(self):
        return f"'{self._sheet.title}'!{TransformSheetAddress(self._startRow, self._startColumn)}:{TransformSheetAddress(self._endRow, self._endColumn)}"
    
    # Starts from 1
    @property
    def startRow(self):
        return self._startRow + 1
    
    # Starts from 1
    @property
    def startColumn(self):
        return self._startColumn + 1
    
    # Starts from 1
    @property
    def endRow(self):
        return self._endRow + 1
    
    # Starts from 1
    @property
    def endColumn(self):
        return self._endColumn + 1

    # By logical address, which starts from 1
    def value(self, row: int, column: int) -> str:
        return self._valueMatrix[row - self._startRow - 1][column - self._startColumn - 1]
    
    # Array index, which starts from 0
    def valueFromZero(self, row: int, column: int) -> str:    
        return self._valueMatrix[row][column]
    
    # By logical address, which starts from 1
    def setValue(self, row: int, column: int, value: str):
        self._valueMatrix[row - self._startRow - 1][column - self._startColumn - 1] = value
    
    # Array index, which starts from 0
    def setValueFromZero(self, row: int, column: int, value: str):
        self._valueMatrix[row][column] = value
    
    def AddRow(self):
        self._valueMatrix.append(["" for _ in range(self._endColumn - self._startColumn)])
        self._endRow += 1
    
    def AddColumn(self):
        for row in self._valueMatrix:
            row.append("")
        self._endColumn += 1


def TransformSheetAddress(row: int, column: int) -> str:
    return f"{TransformRowAddress(row)}{TransformColumnAddress(column)}"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def TransformColumnAddress(column: int) -> str:
    return f"{column + 1}"

def TransformRowAddress(row: int) -> str:
    if row < 0:
        raise ValueError("row must be a positive or zero int")
    if row == 0:
        return "A"
    
    rowStr = ""
    while row > 0:
        row, remainder = divmod(row - 1, 26)
        rowStr = ALPHABET[remainder] + rowStr
    
    return rowStr

@withCreate
class SetSheetRangeRequest(SheetRequest):
    def __init__(self, range: SheetRange):
        if not isinstance(range, SheetRange):
            raise ValueError("range must be an instance of SheetRange")
        
        self._range = range

    def _dictRequest(self, googleSheet: GoogleSheet):
        return {
            'updateCells': {
                'range': {
                    'sheetId': googleSheet.id,
                    'startRowIndex': self._range._startRow,
                    'endRowIndex': self._range._endRow,
                    'startColumnIndex': self._range._startColumn,
                    'endColumnIndex': self._range._endColumn
                },
                'fields': 'userEnteredValue',
                'rows': [
                    {
                        'values': [
                            {
                                'userEnteredValue': {
                                    'stringValue': self._range.value(row, column)
                                }
                            }
                            for column in range(self._range.startColumn, self._range.endColumn)
                        ]
                    }
                    for row in range(self._range.startRow, self._range.endRow)
                ]
            }
        }
    
    def _requestCallback(self, googleSheet: GoogleSheet, callback: Callable[[dict], None]):
        # Firstly add rows and columns if needed
        if self._range._endRow > googleSheet._rowCount:
            req = AddSheetRowsRequest.Create(self._range._endRow - googleSheet._rowCount)
            req._requestCallback(googleSheet, callback)
        
        if self._range._endColumn > googleSheet._columnCount:
            req = AddSheetColumnsRequest.Create(self._range._endColumn - googleSheet._columnCount)
            req._requestCallback(googleSheet, callback)
        
        # Then add the request
        super()._requestCallback(googleSheet, callback)


class WipeSheetRangeRequest(SetSheetRangeRequest):
    def __init__(self, sheet: GoogleSheet, startRow: int, startColumn: int, endRow: int, endColumn: int):
        r = SheetRange(sheet, startRow, startColumn, endRow, endColumn)
        super().__init__(r)
    
class WipeSheetRequest(WipeSheetRangeRequest):
    def __init__(self, sheet: GoogleSheet):
        super().__init__(sheet, 0, 0, sheet.rowCount, sheet.columnCount)


class MergeSheetRangeRequest(SheetRequest):
    def __init__(self, sheetRange: SheetRange):
        if not isinstance(sheetRange, SheetRange):
            raise ValueError("sheetRange must be an instance of SheetRange")
        
        self._sheetRange = sheetRange
    
    def _dictRequest(self, googleSheet: GoogleSheet):
        return {
            'mergeCells': {
                'range': self._sheetRange.Address(),
                'mergeType': 'MERGE_ALL'
            }
        }
