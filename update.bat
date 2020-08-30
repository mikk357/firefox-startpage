@ REM script for windows, achtung!
@ SET ORIGIN=%CD%
@ CD /D %~dp0

@ CALL .venv\Scripts\activate.bat
@ CALL python main.py
@ CALL .venv\Scripts\deactivate.bat

@ CD /D %ORIGIN%
@ ECHO     UwU    
