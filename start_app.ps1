# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe main.py --mode serve"

# Start Frontend
Set-Location web
npm run dev
