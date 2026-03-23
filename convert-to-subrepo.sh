#!/bin/bash
# Convert monorepo subdirectories to git-subrepos
# This script uses git filter-repo to split history

set -e

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "Converting to git-subrepo structure"
echo "========================================"

# Step 1: Update .gitignore
echo -e "${YELLOW}Step 1: Updating .gitignore...${NC}"
cat << 'EOF' > .gitignore
# Build artifacts
build/
*.so
*.elf
*.o
*.a

# Godot
.godot/
*.translation

# Python
__pycache__/
*.py[cod]
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitrepo
EOF

echo -e "  ${GREEN}✓ .gitignore updated${NC}"

# Step 2: Install git-subrepo if needed
echo -e "${YELLOW}Step 2: Checking git-subrepo...${NC}"
if ! command -v git-subrepo &> /dev/null; then
    echo "  Installing git-subrepo..."
    curl -s https://raw.githubusercontent.com/ingydotts/git-subrepo/master/install.sh | bash
fi

echo -e "  ${GREEN}✓ git-subrepo is available${NC}"

# Step 3: Create upstream repos (you'll need to create these on GitHub first)
echo -e "${YELLOW}Step 3: Create these upstream repos on GitHub:${NC}"
echo "  1. https://github.com/fwsGonzo/libriscv"
echo "  2. https://github.com/godotengine/godot-cpp"  
echo "  3. https://github.com/godotengine/godot-headless-templates"
echo ""
echo "  Then run:"
echo "  git subrepo push riscv-toolchain/libriscv"
echo "  git subrepo push godot-sandbox/ext/godot-cpp"
echo "  git subrepo push godot-sandbox/bin"
echo ""

read -p "Have you created the upstream repos? (y/N): " confirm
if [ "$confirm" != "y" ]; then
    echo -e "${RED}Please create the repos and re-run this script.${NC}"
    exit 1
fi

# Step 4: Convert to subrepos
echo -e "${GREEN}Step 4: Converting to git-subrepos...${NC}"

# riscv-toolchain/libriscv
echo "  Converting riscv-toolchain/libriscv..."
git subrepo init riscv-toolchain/libriscv -r https://github.com/fwsGonzo/libriscv.git -b main
git subrepo update riscv-toolchain/libriscv

# godot-sandbox/ext/godot-cpp  
echo "  Converting godot-sandbox/ext/godot-cpp..."
git subrepo init godot-sandbox/ext/godot-cpp -r https://github.com/godotengine/godot-cpp.git -b master
git subrepo update godot-sandbox/ext/godot-cpp

# godot-sandbox/bin
echo "  Converting godot-sandbox/bin..."
git subrepo init godot-sandbox/bin -r https://github.com/godotengine/godot-headless-templates.git -b master
git subrepo update godot-sandbox/bin

echo -e "  ${GREEN}✓ All subrepos initialized${NC}"

# Step 5: Commit
echo -e "${GREEN}Step 5: Committing...${NC}"
git add .
git commit -m "Convert to git-subrepo structure"

echo -e "  ${GREEN}✓ Committed${NC}"

echo ""
echo -e "${GREEN}========================================"
echo "SUCCESS! Monorepo converted to git-subrepo"
echo "========================================${NC}"
echo ""
echo "Push with:"
echo "  git push origin main"
echo ""
echo "Push subrepos with:"
echo "  git subrepo push riscv-toolchain/libriscv"
echo "  git subrepo push godot-sandbox/ext/godot-cpp"
echo "  git subrepo push godot-sandbox/bin"
echo ""
