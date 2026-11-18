## Description

The project is migrating its ZMODEM file transfer support from a TypeScript-based library to a newer WebAssembly-based implementation. As part of this migration, the build system configuration needs to be updated to reference the new library rather than the old one.

Currently, the build system configuration still references the old TypeScript-based library. This means the bundler is not correctly set up to handle the new WebAssembly package, which could cause build failures or incorrect chunking behavior.

## Expected Behavior

- The build configuration file should reference the WebAssembly-based file transfer library instead of the old one
- The bundler should be configured to properly handle the new WebAssembly package (e.g., excluding it from dependency pre-bundling as appropriate)

## Why This Matters

Keeping the build configuration in sync with the actual installed packages is essential for a successful build. Without this update, the project may fail to build correctly or bundle the new library improperly.

I'm working on updating the ZMODEM file transfer support in this terminal application to use a WebAssembly-based library instead of the older TypeScript-based one. I've updated the package dependencies, but I also need to update the build configuration to reference the new library. The build configuration currently still points to the old file transfer library, so the bundler isn't set up correctly for the new WebAssembly library. Can you update the build configuration file to use the new WebAssembly-based library name instead of the old one?
