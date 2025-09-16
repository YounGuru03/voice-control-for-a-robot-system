#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build script for Voice Control App - Creates native Windows executable

.DESCRIPTION
    This script builds the WinUI3 Voice Control App into a standalone Windows executable
    with all dependencies included for optimal deployment.

.EXAMPLE
    .\build.ps1
    .\build.ps1 -Configuration Release -Platform x64
#>

param(
    [string]$Configuration = "Release",
    [string]$Platform = "x64",
    [switch]$Clean = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Script configuration
$ProjectName = "VoiceControlApp"
$ProjectPath = "VoiceControlApp/$ProjectName.csproj"
$OutputPath = "dist"

function Write-BuildMessage {
    param([string]$Message, [string]$Type = "Info")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = switch ($Type) {
        "Error" { "❌" }
        "Warning" { "⚠️" }
        "Success" { "✅" }
        "Info" { "🔨" }
        default { "ℹ️" }
    }
    Write-Host "[$timestamp] $prefix $Message" -ForegroundColor $(
        switch ($Type) {
            "Error" { "Red" }
            "Warning" { "Yellow" }
            "Success" { "Green" }
            default { "White" }
        }
    )
}

function Test-Prerequisites {
    Write-BuildMessage "Checking build prerequisites..."
    
    # Check .NET SDK
    try {
        $dotnetVersion = & dotnet --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "dotnet command failed"
        }
        Write-BuildMessage "✓ .NET SDK version: $dotnetVersion"
    }
    catch {
        Write-BuildMessage ".NET 8 SDK not found. Please install from https://dotnet.microsoft.com/download" "Error"
        exit 1
    }

    # Check Windows SDK
    $windowsSDK = Get-ChildItem -Path "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -ErrorAction SilentlyContinue |
                  Sort-Object Name -Descending | Select-Object -First 1
    
    if ($windowsSDK) {
        Write-BuildMessage "✓ Windows SDK found: $($windowsSDK.Name)"
    } else {
        Write-BuildMessage "Windows 10/11 SDK not found. Install from Visual Studio Installer" "Warning"
    }

    # Check project file
    if (-not (Test-Path $ProjectPath)) {
        Write-BuildMessage "Project file not found: $ProjectPath" "Error"
        exit 1
    }
    Write-BuildMessage "✓ Project file found: $ProjectPath"
}

function Invoke-CleanBuild {
    Write-BuildMessage "Cleaning previous build artifacts..."
    
    $cleanDirs = @("bin", "obj", $OutputPath, "VoiceControlApp/bin", "VoiceControlApp/obj")
    foreach ($dir in $cleanDirs) {
        if (Test-Path $dir) {
            Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
            Write-BuildMessage "Cleaned: $dir"
        }
    }
}

function Restore-Dependencies {
    Write-BuildMessage "Restoring NuGet packages..."
    
    $restoreArgs = @(
        "restore"
        $ProjectPath
        "--verbosity", $(if ($Verbose) { "normal" } else { "quiet" })
    )
    
    & dotnet @restoreArgs
    if ($LASTEXITCODE -ne 0) {
        Write-BuildMessage "Package restore failed" "Error"
        exit 1
    }
    
    Write-BuildMessage "✓ Dependencies restored" "Success"
}

function Invoke-Build {
    Write-BuildMessage "Building $ProjectName ($Configuration|$Platform)..."
    
    # Ensure output directory exists
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    $buildArgs = @(
        "build"
        $ProjectPath
        "--configuration", $Configuration
        "--runtime", "win-$($Platform.ToLower())"
        "--self-contained", "true"
        "--verbosity", $(if ($Verbose) { "normal" } else { "quiet" })
        "-p:PublishSingleFile=true"
        "-p:IncludeNativeLibrariesForSelfExtract=true"
        "-p:PublishTrimmed=false"  # Keep full functionality for voice recognition
        "-p:TrimMode=partial"
        "-p:WindowsAppSDKSelfContained=true"
    )
    
    & dotnet @buildArgs
    if ($LASTEXITCODE -ne 0) {
        Write-BuildMessage "Build failed" "Error"
        exit 1
    }
    
    Write-BuildMessage "✅ Build completed successfully" "Success"
}

function Invoke-Publish {
    Write-BuildMessage "Publishing standalone executable..."
    
    $publishArgs = @(
        "publish"
        $ProjectPath
        "--configuration", $Configuration
        "--runtime", "win-$($Platform.ToLower())"
        "--self-contained", "true"
        "--output", $OutputPath
        "--verbosity", $(if ($Verbose) { "normal" } else { "quiet" })
        "-p:PublishSingleFile=true"
        "-p:IncludeNativeLibrariesForSelfExtract=true"
        "-p:PublishTrimmed=false"
        "-p:TrimMode=partial"
        "-p:WindowsAppSDKSelfContained=true"
        "-p:UseAppHost=true"
    )
    
    & dotnet @publishArgs
    if ($LASTEXITCODE -ne 0) {
        Write-BuildMessage "Publish failed" "Error"
        exit 1
    }
    
    Write-BuildMessage "✅ Published to: $OutputPath" "Success"
}

function Copy-Assets {
    Write-BuildMessage "Copying additional assets..."
    
    # Copy configuration files
    $assetFiles = @(
        "README.md"
        "LICENSE"  
        "VoiceControlApp/appsettings.json"
    )
    
    foreach ($file in $assetFiles) {
        if (Test-Path $file) {
            Copy-Item -Path $file -Destination $OutputPath -Force
            Write-BuildMessage "Copied: $file"
        }
    }
    
    # Create empty text.txt file
    $textFile = Join-Path $OutputPath "text.txt"
    "" | Out-File -FilePath $textFile -Encoding UTF8
    Write-BuildMessage "Created: text.txt"
}

function Show-BuildResults {
    Write-BuildMessage "Build Results Summary:" "Success"
    
    if (Test-Path $OutputPath) {
        $exeFile = Get-ChildItem -Path $OutputPath -Filter "*.exe" | Select-Object -First 1
        
        if ($exeFile) {
            $sizeMB = [math]::Round($exeFile.Length / 1MB, 1)
            Write-BuildMessage "📦 Executable: $($exeFile.Name) ($sizeMB MB)"
            Write-BuildMessage "📁 Location: $(Resolve-Path $OutputPath)"
            
            # List all output files
            Write-BuildMessage "`nOutput files:"
            Get-ChildItem -Path $OutputPath | ForEach-Object {
                $size = if ($_.PSIsContainer) { "[DIR]" } else { "$([math]::Round($_.Length / 1KB, 1)) KB" }
                Write-Host "  📄 $($_.Name) - $size"
            }
        } else {
            Write-BuildMessage "No executable found in output directory" "Warning"
        }
    }
    
    Write-BuildMessage "`n🎉 Build completed successfully!" "Success"
    Write-BuildMessage "Ready for deployment and testing." "Success"
}

# Main build process
try {
    Write-BuildMessage "🚀 Starting Voice Control App Build Process"
    Write-BuildMessage "Configuration: $Configuration | Platform: $Platform"
    
    Test-Prerequisites
    
    if ($Clean) {
        Invoke-CleanBuild
    }
    
    Restore-Dependencies
    Invoke-Build
    Invoke-Publish
    Copy-Assets
    Show-BuildResults
    
    exit 0
}
catch {
    Write-BuildMessage "Build failed with error: $($_.Exception.Message)" "Error"
    Write-BuildMessage "Stack trace: $($_.ScriptStackTrace)" "Error"
    exit 1
}