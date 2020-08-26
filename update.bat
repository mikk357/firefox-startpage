
@SET T=%CD%
@CD %~dp0

@CALL .venv\Scripts\activate.bat
@CALL python main.py
@CALL .venv\Scripts\deactivate.bat

@CD %T%
@ECHO OK
