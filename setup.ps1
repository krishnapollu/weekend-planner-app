# Weekend Planner Assistant - Quick Start Script (PowerShell)
# Run this to set up and test your environment

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Weekend Planner Assistant - Quick Setup" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Create virtual environment
Write-Host "Step 2: Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Step 3: Activate virtual environment
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Activation failed. You may need to run:" -ForegroundColor Yellow
    Write-Host "    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Install dependencies
Write-Host "Step 4: Installing Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Some dependencies may have failed to install" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Check .env file
Write-Host "Step 5: Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ .env file not found. Creating from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Created .env file" -ForegroundColor Green
    Write-Host "  ⚠ Please edit .env and add your API keys!" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Test configuration
Write-Host "Step 6: Testing API configuration..." -ForegroundColor Yellow
Write-Host ""
python test_config.py
Write-Host ""

# Done
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API keys (if not done)" -ForegroundColor White
Write-Host "2. Run: python main.py" -ForegroundColor White
Write-Host "3. Or try examples: python example_usage.py" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see SETUP.md" -ForegroundColor Gray
Write-Host ""
