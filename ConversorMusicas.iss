#define MyAppName "Conversor Músicas"
#define MyAppVersion "1.2.4"
#define MyAppPublisher "GuiaSys Studio"
#define MyAppExeName "ConversorMusicas.exe"

[Setup]
; AppId permanente. Nunca alterar.
AppId={{B17181A7-C736-4A0A-9D36-821F70A96C51}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={localappdata}\Programs\Conversor Músicas
UsePreviousAppDir=yes
DisableDirPage=auto

DefaultGroupName={#MyAppName}
UsePreviousGroup=yes
DisableProgramGroupPage=auto
UsePreviousTasks=yes
UsePreviousLanguage=yes

AllowNoIcons=yes
DirExistsWarning=auto

OutputDir=installer_output
OutputBaseFilename=Conversor-Musicas-Setup v1.2.4
SetupIconFile=assets\app_icon.ico

Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no
UninstallLogMode=append

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "dist\ConversorMusicas\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "modelos\*"; DestDir: "{app}\modelos"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist

[Dirs]
Name: "{app}\modelos"
Name: "{app}\modelos\powerpoint"
Name: "{app}\modelos\slja"
Name: "{app}\modelos\slja\imagens"
Name: "{app}\saida"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent
