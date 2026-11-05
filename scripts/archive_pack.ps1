param(
    [Parameter(Mandatory)][string]$SourceRoot,
    [Parameter(Mandatory)][string]$TargetRoot,
    [Parameter(Mandatory)][string[]]$Items,
    [switch]$Execute,
    [switch]$Move
)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$target = [IO.Path]::GetFullPath($TargetRoot)
if ($source -ne [IO.Path]::GetPathRoot($source)) { $source = $source.TrimEnd([IO.Path]::DirectorySeparatorChar) }
if ($target -ne [IO.Path]::GetPathRoot($target)) { $target = $target.TrimEnd([IO.Path]::DirectorySeparatorChar) }
function Test-Under([string]$Path,[string]$Root) {
    $prefix = $Root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    return $Path.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)
}
function Assert-NoLink([string]$Path) {
    $probe = $Path
    while ($probe) {
        if (Test-Path -LiteralPath $probe) {
            $node = Get-Item -LiteralPath $probe -Force
            if ($node.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked path rejected: $probe" }
        }
        $parent = [IO.Path]::GetDirectoryName($probe)
        if ($parent -eq $probe) { break }
        $probe = $parent
    }
}
Assert-NoLink $source
Assert-NoLink $target
function Assert-Tree([string]$Path) {
    Assert-NoLink $Path
    if ((Get-Item -LiteralPath $Path -Force).PSIsContainer) {
        foreach ($node in Get-ChildItem -LiteralPath $Path -Recurse -Force) {
            if ($node.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked item rejected: $($node.FullName)" }
        }
    }
}
$plan = @()
foreach ($name in $Items) {
    if ([IO.Path]::IsPathRooted($name)) { throw "Use relative item names: $name" }
    $src = (Resolve-Path -LiteralPath (Join-Path $source $name)).Path
    $dst = [IO.Path]::GetFullPath((Join-Path $target $name))
    if (-not (Test-Under $src $source) -or -not (Test-Under $dst $target)) { throw 'Item escaped the selected roots' }
    if ($dst -eq $src -or (Test-Under $dst $src)) { throw 'Destination cannot be inside a source item' }
    if (Test-Path -LiteralPath $dst) { throw "Destination exists; no overwrite: $dst" }
    Assert-Tree $src
    $node = Get-Item -LiteralPath $src -Force
    if ($node.PSIsContainer) {
        foreach ($child in Get-ChildItem -LiteralPath $src -Recurse -Force) {
            if ($child.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked item rejected: $($child.FullName)" }
        }
    }
    foreach ($previous in $plan) {
        if ($src -eq $previous.Source -or (Test-Under $src $previous.Source) -or (Test-Under $previous.Source $src)) {
            throw 'Overlapping source items are not accepted'
        }
    }
    $plan += [pscustomobject]@{Source=$src;Target=$dst;Directory=$node.PSIsContainer}
}
$plan | Format-Table Source,Target
if (-not $Execute) { Write-Output 'Plan only. Use -Execute to copy; add -Move only when the task authorizes moving.'; return }
New-Item -ItemType Directory -Path $target -Force | Out-Null
$records = @()
foreach ($entry in $plan) {
    $parent = [IO.Path]::GetDirectoryName($entry.Target)
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    # Recheck after planning; no -Force means unexpected collisions are not intentional replacements.
    if (Test-Path -LiteralPath $entry.Target) { throw 'Destination appeared during execution' }
    Assert-Tree $entry.Source
    Copy-Item -LiteralPath $entry.Source -Destination $entry.Target -Recurse
    $files = if ($entry.Directory) { @(Get-ChildItem -LiteralPath $entry.Source -Recurse -File -Force) } else { @(Get-Item -LiteralPath $entry.Source) }
    $copied = if ($entry.Directory) { @(Get-ChildItem -LiteralPath $entry.Target -Recurse -File -Force) } else { @(Get-Item -LiteralPath $entry.Target) }
    if ($files.Count -ne $copied.Count) { throw 'Copied file count differs; sources preserved' }
    foreach ($file in $files) {
        $destFile = if ($entry.Directory) { Join-Path $entry.Target ([IO.Path]::GetRelativePath($entry.Source,$file.FullName)) } else { $entry.Target }
        $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        if ($digest -ne (Get-FileHash -LiteralPath $destFile -Algorithm SHA256).Hash) { throw 'Hash mismatch; sources preserved' }
        $records += [pscustomobject]@{Source=$file.FullName;Target=$destFile;SHA256=$digest}
    }
}
$log = Join-Path $target ('archive-' + [guid]::NewGuid().ToString() + '.json')
ConvertTo-Json -InputObject @($records) -Depth 4 | Set-Content -LiteralPath $log -Encoding utf8
if ($Move) {
    # A second full pass checks for new, removed, or changed source files before removing any source tree.
    foreach ($entry in $plan) {
        Assert-Tree $entry.Source
        Assert-Tree $entry.Target
        if ($entry.Directory) {
            $sourceDirs = @(Get-ChildItem -LiteralPath $entry.Source -Recurse -Directory -Force | ForEach-Object {[IO.Path]::GetRelativePath($entry.Source,$_.FullName)} | Sort-Object)
            $targetDirs = @(Get-ChildItem -LiteralPath $entry.Target -Recurse -Directory -Force | ForEach-Object {[IO.Path]::GetRelativePath($entry.Target,$_.FullName)} | Sort-Object)
            if (($sourceDirs -join "`n") -ne ($targetDirs -join "`n")) { throw 'Directory set changed; sources preserved' }
        }
        $current = if ($entry.Directory) { @(Get-ChildItem -LiteralPath $entry.Source -Recurse -File -Force) } else { @(Get-Item -LiteralPath $entry.Source) }
        $expected = @($records | Where-Object {$_.Source -eq $entry.Source -or (Test-Under $_.Source $entry.Source)})
        if ($current.Count -ne $expected.Count) { throw 'Source set changed; sources preserved' }
        foreach ($file in $current) {
            Assert-NoLink $file.FullName
            $match = @($expected | Where-Object {$_.Source -eq $file.FullName})
            if ($match.Count -ne 1 -or (Get-FileHash -LiteralPath $file.FullName).Hash -ne $match[0].SHA256 -or
                (Get-FileHash -LiteralPath $match[0].Target).Hash -ne $match[0].SHA256) { throw 'Files changed; sources preserved' }
        }
    }
    foreach ($entry in $plan) {
        $resolved = (Resolve-Path -LiteralPath $entry.Source).Path
        if (-not (Test-Under $resolved $source)) { throw 'Unsafe cleanup path' }
        Assert-Tree $resolved
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
Write-Output "Verified archive complete. Manifest: $log"
