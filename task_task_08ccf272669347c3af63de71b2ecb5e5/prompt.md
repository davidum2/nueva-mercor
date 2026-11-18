## Description

When an artifact is removed from a Spinnaker pipeline, other stages that reference that artifact by ID are not automatically cleaned up. This leaves stale artifact references scattered across stage configurations, causing inconsistencies in pipeline state. There is currently no centralized mechanism that allows stage types to declare which of their fields hold artifact references and ensures those fields are cleared when an artifact is deleted.

## Expected Behavior

- Stage types should be able to register which fields (including nested fields and array fields) hold references to artifacts.
- When an artifact is deleted from a pipeline, a sweep operation should traverse all pipeline stages and remove every occurrence of that artifact's ID from any registered field.
- The sweep must correctly handle top-level properties, deeply nested object paths, array elements referenced by index, and arrays containing the artifact ID anywhere in their contents.
- If a referenced field does not match the artifact being removed, or if a registered path cannot be fully resolved in a given stage, the stage should be left unchanged.
- Multiple artifact reference fields may be declared for the same stage type; all are processed during a cleanup sweep.

## Why This Matters

Without this service, removing an artifact from a pipeline leaves dangling references in stages that referenced it, which can lead to validation errors or unexpected behavior at pipeline execution time. A centralized service gives both core and plugin stage types a consistent way to participate in artifact lifecycle management.

I'm working on Spinnaker's pipeline configuration UI and need a centralized service for managing artifact references across pipeline stages. Right now, when an artifact is deleted from a pipeline, other stages that reference that artifact by ID are not cleaned up — stale references just sit there, which can cause problems at runtime.

I'd like a service that lets each stage type declare which of its fields hold artifact references (including nested fields and array fields), and that can perform a sweep across all pipeline stages to remove a specific artifact reference wherever it appears. The service needs to handle simple top-level properties, deeply nested object paths, array elements at a known index, and arrays that may contain the artifact ID anywhere in their contents. When a path can't be fully resolved in a given stage, or when the field value doesn't match the artifact being removed, the stage should be left untouched. Multiple reference fields per stage type should be supported.

## Additional Requirements

Your implementation must expose the following public API exactly as named, since downstream callers depend on these exact identifiers/signatures:

- `ArtifactReferenceServiceProvider` (class) — `export class ArtifactReferenceServiceProvider`
