Python -m pip install -r "$PSScriptRoot\requirements.txt" --quiet
Set-Location "$PSScriptRoot\client"
Python start.py
