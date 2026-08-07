Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

LockPath = "d:\Projects\Agentic Projects\Daily Tech Digest\digest_run.lock"

' If a fresh lock exists, a digest run is already in progress - skip this trigger
' to avoid concurrent processes racing on the registry and log file.
If fso.FileExists(LockPath) Then
    Set LockFile = fso.GetFile(LockPath)
    StaleTime = DateAdd("n", -45, Now())
    IsStale = (LockFile.DateLastModified < StaleTime)
    If Not IsStale Then
        WScript.Quit 0
    End If
    ' Stale lock: let main.py replace it on startup.
End If

WshShell.Run "cmd.exe /c cd /d ""d:\Projects\Agentic Projects\Daily Tech Digest"" && python -u main.py > daily_digest.log 2>&1", 0, False
