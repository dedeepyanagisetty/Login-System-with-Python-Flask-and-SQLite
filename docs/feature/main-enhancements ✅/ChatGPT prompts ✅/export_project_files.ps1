# ==========================================
# export_project_files.ps1
#
# Purpose:
# Export all readable code/text files into one text file
# and open automatically in Notepad.
# ==========================================

# Ask user for project path
# If Enter is pressed, current folder is used
$path = Read-Host "Enter project path (Press Enter for current folder)"

# Use current folder if blank
if ([string]::IsNullOrWhiteSpace($path)) {
    $path = (Get-Location).Path
}

# Output file location
$outputFile = Join-Path $path "project_files.txt"

# Delete old output file if it exists
if (Test-Path $outputFile) {
    Remove-Item $outputFile -Force
}

# Binary extensions to exclude
$excludedExtensions = @(
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico",
    ".mp4", ".avi", ".mov", ".wmv", ".mkv",
    ".mp3", ".wav", ".aac", ".flac",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".exe", ".dll", ".so", ".bin", ".msi",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".db", ".sqlite", ".sqlite3",
    ".pyc", ".pyo", ".class", ".jar",
    ".ttf", ".otf", ".woff", ".woff2", ".iso"
)

# Find all files recursively
# Ignore common binary/cache folders
Get-ChildItem -Path $path -Recurse -File |
Where-Object {
    $_.FullName -notmatch '\\__pycache__\\' -and
    $_.FullName -notmatch '\\node_modules\\' -and
    $_.FullName -notmatch '\\\.git\\' -and
    $_.Extension.ToLower() -notin $excludedExtensions
} |
ForEach-Object {

    try {

        # Add file header
        "`r`n==================== $($_.FullName) ====================`r`n" |
            Out-File -FilePath $outputFile -Append -Encoding UTF8

        # Add file contents
        Get-Content -Path $_.FullName |
            Out-File -FilePath $outputFile -Append -Encoding UTF8

    }
    catch {
        # Skip unreadable or inaccessible files
    }

}

Write-Host ""
Write-Host "Export completed successfully."
Write-Host "Output File: $outputFile"

# Open output automatically
notepad.exe $outputFile