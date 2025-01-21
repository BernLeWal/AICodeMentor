# PowerShell script
# Usage: .\run_codementor.ps1 [additional arguments for your application]

# Define the image name
$imageName = "codementor-image"

# Check if the image exists, build it if not
if (-not (docker images | Select-String $imageName)) {
    Write-Host "Docker image not found. Building the image..."
    docker build -t $imageName -f docker\codementor\Dockerfile .
}

# Get the current working directory
$currentDir = Get-Location

# Run the container with the given arguments
docker run --rm `
    --env-file docker\codementor\.env `
    -v "$($currentDir)\workflows:/home/mentor/workflows" `
    -v "$($currentDir)\output:/home/mentor/output" `
    -v "$($currentDir)\log:/home/mentor/log" `
    $imageName @args
