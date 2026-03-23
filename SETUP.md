# Monorepo Setup Guide

## Current Structure

```
monorepo/
├── godot-sandbox/           # Godot 4.7 ENet Sandbox project
│   ├── bin/                 # Build artifacts (.so, .gdextension)
│   ├── ext/godot-cpp/       # godot-cpp subrepo (empty, will clone)
│   └── ...
├── python-bridge/           # Python networking bridge
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD
└── riscv-toolchain/libriscv/ # libriscv source (full clone)
```

## Subrepos Setup

### 1. `riscv-toolchain/libriscv/`
This contains the full [libriscv](https://github.com/fwsGonzo/libriscv) source code.

```bash
cd riscv-toolchain/libriscv
git remote add origin https://github.com/fwsGonzo/libriscv.git
git fetch origin
git branch --set-upstream-to=origin/main main
git subrepo push
```

### 2. `godot-sandbox/ext/godot-cpp/`
This is a mostly-empty directory that clones [godot-cpp](https://github.com/godotengine/godot-cpp).

```bash
cd godot-sandbox/ext/godot-cpp
git remote add origin https://github.com/godotengine/godot-cpp.git
git fetch origin
git branch --set-upstream-to=origin/main main
git subrepo push
```

### 3. `godot-sandbox/bin/`
This contains **build artifacts** (compiled `.so` files), NOT source code.
Add to `.gitignore`:
```gitignore
# Build artifacts
godot-sandbox/bin/
```

## After Setup

1. Push main monorepo:
```bash
git push origin main
```

2. Push subrepos:
```bash
git subrepo push riscv-toolchain/libriscv
git subrepo push godot-sandbox/ext/godot-cpp
```

## Notes

- `godot-sandbox/bin/` contains the compiled `libgodot_riscv.linux.template_release.double.x86_64.so` (5.4MB) - this is a build artifact, not source
- `godot-sandbox/ext/godot-cpp/` is mostly empty - it only clones the godot-cpp interface headers
