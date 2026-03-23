#!/bin/bash
# Publish script for The Godot ENet Sandbox monorepo

set -e

echo "============================================"
echo "Publishing The Godot ENet Sandbox to GitHub"
echo "============================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) not found. Please install it first."
    echo "  https://cli.github.com/"
    exit 1
fi

# Get username
USERNAME=$(gh api user --jq '.login')

# Create repo
echo "Creating GitHub repository..."
gh repo create "$USERNAME/godot-enet-sandbox" --public --push --source=. --description="Godot 4.7 ENet Sandbox with RISC-V integration and Python bridge"

echo ""
echo "============================================"
echo "✅ Published!"
echo "============================================"
echo ""
echo "Your monorepo is now at:"
echo "  https://github.com/$USERNAME/godot-enet-sandbox"
echo ""
echo "Project structure:"
echo "  - godot-sandbox/     # Godot 4.7 project"
echo "  - python-bridge/     # Python ENet bridge"
echo "  - riscv-toolchain/   # RISC-V toolchain"
echo "  - docs/              # Documentation"
echo ""
