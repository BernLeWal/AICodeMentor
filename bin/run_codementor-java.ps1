# PowerShell script
# Usage: .\run_codementor.ps1 [additional arguments for your application]

# Define the image name
$imageName = "codementor-java"

# Check if the image exists, build it if not
if (-not (docker images | Select-String $imageName)) {
    Write-Host "Docker image not found. Building the image..."
    docker build -t $imageName -f docker\codementor-java\Dockerfile .
}

# Get the current working directory
$currentDir = Get-Location

# Run the container with the given arguments
docker run --rm `
    --env-file docker\.env `
    -v "$($currentDir)\workflows:/home/mentor/workflows" `
    -v "$($currentDir)\log:/home/mentor/log" `
    -p 5000:5000 `
    $imageName @args
