# Phase 1: 🔍 Analysis - GIMP Architecture Scan

## GIMP Version
- **Version:** 2.10.30
- **Location:** /usr/bin/gimp
- **Libraries:** /usr/lib/gimp/2.0/

## Scripting Capabilities

### 1. Script-Fu (Scheme)
- **Location:** /usr/share/gimp/2.0/scripts/
- **Count:** 53 built-in scripts
- **Use Case:** Quick batch operations via command line

### 2. Python-Fu
- **Status:** Not available by default
- **Alternative:** Use Script-Fu for batch operations

### 3. Batch Mode
```bash
gimp -i -b '(script-fu-command)' -b '(gimp-quit 0)'
```
- `-i`: No interface (headless)
- `-b`: Batch command
- Can chain multiple `-b` commands

## Key PDB Procedures (Procedural Database)

GIMP exposes functions via PDB. Key categories for our needs:

### File Operations
- `file-jpeg-save`
- `file-png-save`
- `gimp-file-load`

### Image Manipulation
- `gimp-image-scale`
- `gimp-drawable-brightness-contrast`
- `gimp-context-set-foreground`

### Filters
- `plug-in-unsharp-mask` (sharpen)
- `plug-in-borderaverage`

## Architecture Decision

**Approach:** Hybrid CLI-Anything harness
- **CLI Layer:** Python Click for user-friendly commands
- **Execution Layer:** Script-Fu for GIMP operations
- **Bridge:** Generate Script-Fu code dynamically from Python

## Next Steps
1. Design command structure (Phase 2)
2. Implement Click CLI with Script-Fu generation (Phase 3)
3. Test with sample images (Phase 5)
