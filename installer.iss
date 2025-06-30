[Setup]
AppName=Devinova POS
AppVersion=1.0
DefaultDirName={pf}\DevinovaPOS

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "templates\*"; DestDir: "{app}\templates"; Flags: recursesubdirs
Source: "static\*"; DestDir: "{app}\static"; Flags: recursesubdirs
Source: "static\images\*"; DestDir: "{app}\static\images"; Flags: recursesubdirs
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "devinova_pos.accdb"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Devinova POS"; Filename: "{app}\main.exe"
Name: "{userdesktop}\Devinova POS"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Launch Devinova POS"; Flags: nowait postinstall skipifsilent