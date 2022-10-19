# group-cmput404-project



## Setup Virtual Environment

Unix or MacOS (bash)
```
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (powershell)
```
python -3.10 -m venv .\venv
.\venv\Scripts/Activate.ps1
pip install -r requirements.txt
```

!! Make sure you work in venv !!
  - On Unix or MacOS, using the bash shell: `source /path/to/venv/bin/activate`
  - On Unix or MacOS, using the csh shell: `source /path/to/venv/bin/activate.csh`
  - On Unix or MacOS, using the fish shell: `source /path/to/venv/bin/activate.fish`
  - On Windows using the Command Prompt: `path\to\venv\Scripts\activate.bat`
  - On Windows using PowerShell: `path\to\venv\Scripts\Activate.ps1`

## To run the live server:

`uvicorn main:app --reload`



## When working:

- If adding new dependeceny always add to requirements.txt file
  - `pip freeze > requirements.txt`
- To update your installation after a pull, simply run pip install again
  - `pip install -r requirements.txt`


