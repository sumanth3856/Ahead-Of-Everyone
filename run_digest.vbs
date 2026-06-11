Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c cd /d ""d:\Projects\Agentic Projects\Daily Tech Digest"" && python -u main.py > daily_digest.log 2>&1", 0, False
