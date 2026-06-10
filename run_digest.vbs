Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c cd /d ""d:\Projects\Agentic Projects\Daily Tech Digest"" && python -u generate_and_send.py > daily_digest.log 2>&1", 0, False
