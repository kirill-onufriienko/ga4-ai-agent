import sys
import io
import traceback
import math
import json
import statistics
from datetime import datetime, timedelta

# Список модулей которые разрешено использовать в sandbox
ALLOWED_MODULES = {
    "math": math,
    "json": json,
    "statistics": statistics,
    "datetime": datetime,
    "timedelta": timedelta,
}

# Попробуем добавить pandas если установлен
try:
    import pandas as pd

    ALLOWED_MODULES["pd"] = pd
    ALLOWED_MODULES["pandas"] = pd
except ImportError:
    pass


def run_safe(code: str) -> dict:
    """
    Запускает Python код в ограниченной среде.

    Возвращает словарь:
    - success: True/False
    - output: что вывел print()
    - error: текст ошибки если была
    """

    # Перехватываем stdout чтобы поймать print() вызовы
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    try:
        # Создаём ограниченное пространство имён
        # Код будет видеть только эти переменные и модули
        safe_globals = {
            "__builtins__": {
                # Разрешённые встроенные функции
                "print": print,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "isinstance": isinstance,
                "type": type,
            },
            **ALLOWED_MODULES
        }

        # Запускаем код
        exec(code, safe_globals)

        result["success"] = True
        result["output"] = captured_output.getvalue()

    except Exception as e:
        result["success"] = False
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["output"] = captured_output.getvalue()

    finally:
        # Обязательно восстанавливаем stdout
        sys.stdout = old_stdout

    return result