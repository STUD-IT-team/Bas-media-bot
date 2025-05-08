from datetime import datetime


TIME_FORMAT = "%d-%m-%Y %H:%M"

def GetTimeDateFormatDescription() -> str:
    return "{День}-{Месяц}-{Год} {Час}:{Минуты}"

def GetTimeDateFormatExample() -> str:
    return "15-05-2022 18:00"

def ParseTimeDate(dtstr : str) -> (datetime, bool):
    try:
        dt = datetime.strptime(dtstr, TIME_FORMAT)
        return dt, True
    except ValueError:
        return None, False