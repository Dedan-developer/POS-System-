# Devinova POS Standalone Executable Instructions

## How to Build the Standalone .exe

1. **Install PyInstaller**
   Open PowerShell and run:
   ```powershell
   pip install pyinstaller
   ```

2. **Build the Executable**
   In your project directory, run:
   ```powershell
   pyinstaller --onefile --add-data "config.json;." --add-data "devinova_pos.accdb;." --add-data "static;static" --add-data "templates;templates" main.py
   ```
   - This will create a `dist/main.exe` file.
   - The `--add-data` options ensure your config, database, static, and templates folders are included.

3. **Distribute**
   - Copy the `dist/main.exe` and any required files (e.g., `config.json`, `devinova_pos.accdb`) to the target machine.
   - The target machine must have Microsoft Access or the Access Database Engine installed.

## Notes
- No need to install Python or Flask on the target machine.
- If you update your code, re-run the PyInstaller command.
- If you use other files (images, uploads), add them with `--add-data` as needed.

## Troubleshooting
- If you see database connection errors, ensure the Access ODBC driver is installed on the target machine.
- If you see missing file errors, check your `--add-data` paths.

---

For advanced customization, edit the generated `main.spec` file and re-run:
```powershell
pyinstaller main.spec
```
