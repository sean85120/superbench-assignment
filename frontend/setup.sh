#!/bin/bash

echo "Setting up AI Agent Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install npm first."
    exit 1
fi

echo "Installing dependencies..."
npm install

echo "Setup complete!"
echo ""
echo "To start the frontend:"
echo "1. Make sure the backend server is running on http://localhost:8000"
echo "2. Run: npm start"
echo ""
echo "Or open demo.html in your browser for a simple demo:"
echo "open demo.html" 