## Description

Bazel's spawn execution log does not properly handle symbolic link outputs. There are three related gaps in the current implementation:

1. **Unresolved symlink outputs are not logged correctly.** When a build action declares a symlink as an output (using the symlink declaration mechanism), the execution log treats it the same as a missing output — the symlink's target path is not captured at all.

2. **Outputs with the wrong filesystem type are not distinguished from missing outputs.** If an output is declared as a file but a directory is present on disk (or vice versa), the logger lumps this together with truly absent outputs under a single "missing path" category. These should be tracked separately so users can diagnose type mismatches.

3. **Indirect outputs through symlinks are not followed.** When a file or directory output is accessed on disk through an intermediate symbolic link (the declared path is a symlink pointing to the real content elsewhere), the logger should follow the link and capture the actual content details.

## Expected Behavior

- Declared symlink outputs that are actual symlinks on disk should appear in both the listed outputs and the actual outputs, with the symlink target path recorded.
- Declared file or directory outputs that exist with the wrong filesystem type should appear in listed outputs only, clearly separate from correctly-typed outputs.
- Declared file or directory outputs that are symlinks to the actual content should have that content (digest or directory listing) captured by following the symlink.

## Why This Matters

Without these fixes, execution logs are inaccurate for builds that use symlink outputs or have type mismatches, making it harder to reproduce and analyze build actions.

I've been looking into how Bazel logs spawn execution details and noticed a few gaps around symbolic link outputs. When a build action declares a symlink as one of its outputs and the action actually produces that symlink on disk, the execution log doesn't capture the symlink's target path — it just treats it like a missing output, which makes the log inaccurate. Similarly, if a declared file or directory output happens to be backed by a symbolic link on disk pointing to the real content elsewhere, the logger isn't following that link to capture the actual content.

There's also an issue with outputs that have the wrong filesystem type — for example, a declared file output that turns out to be a directory on disk, or a declared directory output that is actually a regular file. Right now these get lumped in with genuinely absent outputs, but they should be tracked differently so it's clear that the output exists but has an unexpected type.

I'd like the spawn execution logging to be updated so that symlink outputs are logged properly with their target paths, mismatched-type outputs are clearly distinguished from missing outputs, and indirect symlinks on file/directory outputs are followed transparently when capturing content details.
