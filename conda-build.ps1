Param(
  $recipe = 'conda-recipe',
  [switch] $upload = $false
)
$user = 'openhydrology'
$channel = 'main'

$pyversions = '3.3', '3.4'
$build_platform = 'win-64'
$other_platforms = 'osx-64', 'linux-64'

$build_folder = "$env:LOCALAPPDATA\Continuum\Miniconda3\conda-bld"

$built_pkgs = @()
foreach ($pyversion in $pyversions) {
    conda build $recipe --python=$pyversion
    if ($lastexitcode -ne 0) {
        Throw "Conda build failed with exit code $lastexitcode"
    }
    $pkg = conda build $recipe --python=$pyversion --output
    $built_pkgs += $pkg

    $pkg_name = (Get-Item $pkg).Name
    foreach ($platform in $other_platforms) {
        conda convert --platform $platform --output-dir $build_folder $pkg
        if ($lastexitcode -ne 0) {
            Throw "Conda convert failed with exit code $lastexitcode"
        }
        $built_pkgs += "$build_folder\$platform\$pkg_name"
    }
}

if ($upload) {
    anaconda upload --user $user --channel $channel --force $built_pkgs
}
