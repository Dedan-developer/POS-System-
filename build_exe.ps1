# PowerShell script to build the standalone executable for Devinova POS

# Step 1: Install PyInstaller if not already installed
pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Installing PyInstaller...'
    pip install pyinstaller
}

# Step 2: Build the executable using the .spec file
Write-Host 'Building the executable...'
pyinstaller main.spec

Write-Host 'Build complete! Find your .exe in the dist/ folder.'
