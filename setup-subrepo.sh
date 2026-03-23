#!/bin/bash
set -e

cd "$(dirname "$0")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Godot ENet Sandbox - git-subrepo Setup"
echo "=========================================="

# Verify clean state
echo -e "${YELLOW}Checking git status...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Uncommitted changes detected."
    exit 1
fi
echo "  ✓ Clean working tree"

# Initialize empty subrepos that don't have git yet
for dir in "godot-sandbox/bin" "godot-sandbox/ext/godot-cpp"; do
    if [ ! -d "$dir/.git" ] && [ -d "$dir" ]; then
        echo -e "${YELLOW}Initializing git in $dir...${NC}"
        cd "$dir"
        git init
        git config user.email "subrepo@monorepo"
        git config user.name "Subrepo Bot"
        cd - > /dev/null
    fi
done

# Configure .gitrepo files
echo -e "${YELLOW}\nConfiguring .gitrepo files...${NC}"

cat > riscv-toolchain/libriscv/.gitrepo << 'EOF'
[subrepo]
remote = https://github.com/fwsGonzo/libriscv.git
branch = main
method = merge
EOF

cat > godot-sandbox/ext/godot-cpp/.gitrepo << 'EOF'
[subrepo]
remote = https://github.com/godotengine/godot-cpp.git
branch = master
method = merge
EOF

# Note: bin doesn't have actual content, it's a reference to templates
cat > godot-sandbox/bin/.gitrepo << 'EOF'
[subrepo]
remote = https://github.com/godotengine/godot-headless-templates.git
branch = master
method = merge
EOF

git add */.gitrepo
 git commit -m "Configure git-subrepo structure" --quiet

echo -e "${GREEN}✓ .gitrepo files configured${NC}"

# Final instructions  
echo ""
echo "=========================================="
echo "${GREEN}Setup Complete!${NC"
echo "=========================================="
echo ""
echo "Manual steps needed:"
echo ""
echo "1. Push subrepos to GitHub:"
echo "   cd riscv-toolchain/libriscv"
echo "   git remote add origin https://github.com/fwsGonzo/libriscv.git"
echo "   git push -u origin main"
echo ""
echo "   cd godot-sandbox/ext/godot-cpp"
echo "   git remote add origin https://github.com/godotengine/godot-cpp.git"
echo "   git push -u origin master"
echo ""
echo "2. Push main monorepo:"
echo "   git push origin main"
echo ""
echo "Done!"
