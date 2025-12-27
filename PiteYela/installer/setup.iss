; Inno Setup script for Alcohol POS installer
; Creates an installer that installs to user's Documents folder

[Setup]
AppName=Alcohol POS
AppVersion=1.0.0
AppPublisher=Alcohol POS System
DefaultDirName={userdocs}\AlcoholPOS
DefaultGroupName=Alcohol POS
OutputDir=installer_output
OutputBaseFilename=AlcoholPOS_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\AlcoholPOS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Alcohol POS"; Filename: "{app}\AlcoholPOS.exe"
Name: "{userdesktop}\Alcohol POS"; Filename: "{app}\AlcoholPOS.exe"

[Run]
Filename: "{app}\AlcoholPOS.exe"; Description: "Launch Alcohol POS"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  // Ensure data directory exists
  CreateDir(ExpandConstant('{userdocs}\AlcoholPOS\data'));
end;

