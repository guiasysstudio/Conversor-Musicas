#define MyAppName "Conversor Músicas"
#define MyAppVersion "1.2.3"
#define MyAppPublisher "GuiaSys Studio"
#define MyAppExeName "ConversorMusicas.exe"

[Setup]
; IMPORTANTE: este AppId é permanente. Nunca alterar entre versões.
AppId={{B17181A7-C736-4A0A-9D36-821F70A96C51}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

; Primeira instalação: este é apenas o diretório sugerido.
; O usuário pode escolher outro diretório.
DefaultDirName={localappdata}\Programs\Conversor Músicas

; Se já existir uma instalação com o mesmo AppId,
; o Inno Setup recupera automaticamente o diretório usado anteriormente.
UsePreviousAppDir=yes

; "auto" = mostra escolha de diretório na PRIMEIRA instalação,
; mas oculta essa página quando detecta uma instalação anterior.
DisableDirPage=auto

DefaultGroupName={#MyAppName}
UsePreviousGroup=yes
DisableProgramGroupPage=auto
UsePreviousTasks=yes
UsePreviousLanguage=yes

AllowNoIcons=yes
DirExistsWarning=auto

OutputDir=installer_output
OutputBaseFilename=Conversor-Musicas-Setup
SetupIconFile=assets\app_icon.ico

Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; Instalação por usuário. Evita duplicação entre modos admin/não-admin
; a partir desta linha de versões.
PrivilegesRequired=lowest

ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

; Atualização substitui arquivos em uso com segurança.
CloseApplications=yes
RestartApplications=no

; Mantém um único registro/log de desinstalação para todas as versões.
UninstallLogMode=append

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
; Arquivos executáveis do programa: são atualizados a cada versão.
Source: "dist\ConversorMusicas\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Modelos editáveis:
; - primeira instalação: são copiados normalmente;
; - atualização: arquivos que já existem NÃO são sobrescritos;
; - modelos novos, com nomes novos, podem ser adicionados pela atualização.
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
