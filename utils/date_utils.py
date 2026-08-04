from datetime import datetime


def now_str():
    """
    Fecha y hora actual en formato 'YYYY-MM-DD HH:MM:SS'.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    """
    Fecha actual en formato 'YYYY-MM-DD'.
    """
    return datetime.now().strftime("%Y-%m-%d")


def time_str():
    """
    Hora actual en formato 'HH:MM'.
    """
    return datetime.now().strftime("%H:%M")
