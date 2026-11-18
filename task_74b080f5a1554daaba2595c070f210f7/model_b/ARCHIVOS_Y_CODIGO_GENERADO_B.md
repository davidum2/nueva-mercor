# ARCHIVOS GENERADOS Y LÍNEAS DE CÓDIGO - AGENTE B (MODEL B)

**Tarea:** `bazelbuild-bazel-21177 [model A/B]`  
**Repositorio:** `bazelbuild/bazel`  
**Total de archivos modificados/creados:** 7 archivos (+20 / -13 líneas)  

---

## 1. ARCHIVOS MODIFICADOS Y FRAGMENTOS EXTRAÍDOS

- `/workspace/repo/src/main/java/com/google/devtools/build/lib/exec/ExpandedSpawnLogContext.java` (2 apariciones en la trayectoria)
- `/workspace/repo/src/main/java/com/google/devtools/build/lib/exec/SpawnLogContext.java` (1 apariciones en la trayectoria)
- `/workspace/repo/src/main/java/com/google/devtools/build/lib/exec/StableSort.java` (1 apariciones en la trayectoria)
- `/workspace/repo/src/main/protobuf/spawn.proto` (1 apariciones en la trayectoria)
- `/workspace/repo/src/test/java/com/google/devtools/build/lib/exec/CompactSpawnLogContextTest.java` (1 apariciones en la trayectoria)
- `/workspace/repo/src/test/java/com/google/devtools/build/lib/exec/SpawnLogContextTestBase.java` (1 apariciones en la trayectoria)

---

## 2. DETALLE DE CÓDIGO Y MODIFICACIONES POR ARCHIVO

### Archivo: `/workspace/repo/src/main/java/com/google/devtools/build/lib/exec/ExpandedSpawnLogContext.java`

#### Paso 2:
```java
1: // Copyright 2023 The Bazel Authors. All rights reserved.
2: //
3: // Licensed under the Apache License, Version 2.0 (the "License");
4: // you may not use this file except in compliance with the License.
5: // You may obtain a copy of the License at
6: //
7: //    http://www.apache.org/licenses/LICENSE-2.0
```

#### Paso 41:
```java
190:               .setIsTool(isTool);
191:         }
192:       } catch (IOException e) {
193:         logger.atWarning().withCause(e).log("Error computing spawn input properties");
194:       }
195:       try (SilentCloseable c1 = Profiler.instance().profile("logSpawn/outputs")) {
196:         ArrayList<String> outputPaths = new ArrayList<>();
```

---

### Archivo: `/workspace/repo/src/main/java/com/google/devtools/build/lib/exec/SpawnLogContext.java`

#### Paso 56:
```java
106:     return builder.build();
107:   }
108: 
109:   /**
110:    * How a declared spawn output must be logged, as determined by comparing its declared type with
111:    * the filesystem entry found at its path.
112:    */
```

---

### Archivo: `/workspace/repo/src/main/java/com/google/devtools/build/lib/exec/StableSort.java`

#### Paso 16:
```java
1: // Copyright 2019 The Bazel Authors. All rights reserved.
2: //
3: // Licensed under the Apache License, Version 2.0 (the "License");
4: // you may not use this file except in compliance with the License.
5: // You may obtain a copy of the License at
6: //
7: //    http://www.apache.org/licenses/LICENSE-2.0
```

---

### Archivo: `/workspace/repo/src/main/protobuf/spawn.proto`

#### Paso 3:
```protobuf
1: // Copyright 2018 The Bazel Authors. All rights reserved.
2: //
3: // Licensed under the Apache License, Version 2.0 (the "License");
4: // you may not use this file except in compliance with the License.
5: // You may obtain a copy of the License at
6: //
7: //    http://www.apache.org/licenses/LICENSE-2.0
```

---

### Archivo: `/workspace/repo/src/test/java/com/google/devtools/build/lib/exec/CompactSpawnLogContextTest.java`

#### Paso 14:
```java
1: // Copyright 2023 The Bazel Authors. All Rights Reserved.
2: //
3: // Licensed under the Apache License, Version 2.0 (the "License");
4: // you may not use this file except in compliance with the License.
5: // You may obtain a copy of the License at
6: //
7: //    http://www.apache.org/licenses/LICENSE-2.0
```

---

### Archivo: `/workspace/repo/src/test/java/com/google/devtools/build/lib/exec/SpawnLogContextTestBase.java`

#### Paso 15:
```java
1: // Copyright 2023 The Bazel Authors. All Rights Reserved.
2: //
3: // Licensed under the Apache License, Version 2.0 (the "License");
4: // you may not use this file except in compliance with the License.
5: // You may obtain a copy of the License at
6: //
7: //    http://www.apache.org/licenses/LICENSE-2.0
```

---

## 3. SOLUCIÓN FINAL Y PARCHE DEL MODELO B

```text
Done. All three gaps are fixed and tests pass.

Changes:
1. src/main/protobuf/spawn.proto:
   - File.symlink_target_path = 4: target of an unresolved symlink output (expanded format).
   - New ExecLogEntry.UnresolvedSymlink { path, target_path }, wired into the top-level payload oneof.
   - ExecLogEntry.Output gained unresolved_symlink_id = 4 and invalid_output_path = 5, the latter separating wrong-type outputs from missing_path.

2. SpawnLogContext.java:
   - New shared classifier getOutputType(output, path) returning FILE/DIRECTORY/UNRESOLVED_SYMLINK/MISSING/INVALID (SpawnLogContext.java:137).
   - Matches declared type (ActionInput.isSymlink() / isDirectory()) against disk:
     * Symlink outputs require an actual symlink (isSymbolicLink(), no following).
     * File/directory outputs follow symlinks transparently.
     * Mismatched types become INVALID rather than MISSING.

3. CompactSpawnLogContext.java:
   - Switches on getOutputType: logs UnresolvedSymlink into the table, logs invalid_output_path, or delegates to logFile/logDirectory.

4. ExpandedSpawnLogContext.java:
   - Uses getOutputType: adds actual_outputs with target_path for unresolved symlinks, omits INVALID from actual_outputs, records listed_outputs for both.

5. Tests:
   - CompactSpawnLogContextTest.java & SpawnLogContextTestBase.java:
     * Replaced testDirectoryOutput with testFileOutput_wrongType (covering type mismatch).
     * Added indirection coverage.
```
