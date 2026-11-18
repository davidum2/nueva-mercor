FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git curl ca-certificates patch \
    openjdk-17-jdk python3 zip unzip \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

RUN curl -L -o /usr/local/bin/bazel \
    https://github.com/bazelbuild/bazel/releases/download/6.4.0/bazel-6.4.0-linux-x86_64 \
    && chmod +x /usr/local/bin/bazel

WORKDIR /workspace

RUN git clone https://github.com/bazelbuild/bazel.git /workspace/repo && cd /workspace/repo && \
    BASE=3f11b34d4c614cbf1c9311984b48c0426d4280b1 && \
    cur_branch="$(git rev-parse --abbrev-ref HEAD)" && \
    git reset --hard "$BASE" && \
    git for-each-ref --format='%(refname:short)' refs/heads | while read -r b; do \
      [ "$b" = "$cur_branch" ] || git branch -D "$b"; \
    done && \
    git remote | xargs -r -n1 git remote remove && \
    rm -f .git/config.lock && \
    git reflog expire --expire=now --all && \
    git gc --prune=now --aggressive

WORKDIR /workspace/repo

RUN bazel build //src/test/java/com/google/devtools/build/lib/exec:ExecTests > /workspace/build.log 2>&1; \
    BUILD_EXIT=$?; \
    tail -50 /workspace/build.log; \
    exit $BUILD_EXIT

WORKDIR /workspace

# offline-harbor: warm dependency caches at build (offline-hermetic grade)
RUN set +e; cd /workspace/repo 2>/dev/null; export DEBIAN_FRONTEND=noninteractive; if ls pom.xml */pom.xml >/dev/null 2>&1; then (command -v mvn >/dev/null 2>&1 || (apt-get update && apt-get install -y --no-install-recommends maven)) >/dev/null 2>&1; mvn -q -B -DskipTests -Dmaven.test.skip=false dependency:go-offline 2>/dev/null; mvn -q -B -DincludeScope=test dependency:go-offline 2>/dev/null; mvn -q -B org.apache.maven.plugins:maven-dependency-plugin:resolve-plugins 2>/dev/null; mvn -q -B -DskipTests install 2>/dev/null; mvn -q -B -Dmaven.test.skip=false test-compile 2>/dev/null; mvn -q -B -Dtest=_zzz_nomatch_zzz -DfailIfNoTests=false -Dsurefire.failIfNoSpecifiedTests=false test 2>/dev/null; fi; if ls build.gradle build.gradle.kts gradlew gradle settings.gradle settings.gradle.kts >/dev/null 2>&1; then GW=''; [ -x ./gradlew ] && GW=./gradlew; [ -z "$GW" ] && [ -x ./gradle ] && GW=./gradle; [ -z "$GW" ] && command -v gradle >/dev/null 2>&1 && GW=gradle; if [ -n "$GW" ]; then ($GW --no-daemon -q assemble testClasses -x test 2>/dev/null || $GW --no-daemon -q dependencies 2>/dev/null); ($GW --no-daemon -q testClasses 2>/dev/null); ($GW --no-daemon --continue test --tests _zzz_nomatch_zzz 2>/dev/null); ($GW --no-daemon --continue jacocoTestReport 2>/dev/null); fi; fi; if [ -f package.json ]; then (npm ci 2>/dev/null || npm install 2>/dev/null || yarn install --frozen-lockfile 2>/dev/null || yarn install 2>/dev/null || (corepack enable 2>/dev/null; pnpm install 2>/dev/null)); (npx --yes playwright install --with-deps 2>/dev/null || npx --yes playwright install chromium 2>/dev/null); (npx --yes puppeteer browsers install chrome 2>/dev/null); (node node_modules/puppeteer/install.mjs 2>/dev/null || node node_modules/puppeteer/install.js 2>/dev/null); (node_modules/.bin/cypress install 2>/dev/null); fi; if [ -f Cargo.toml ]; then cargo fetch 2>/dev/null; cargo test --no-run 2>/dev/null; fi; if [ -f go.mod ]; then go mod download all 2>/dev/null || go mod download 2>/dev/null; go test -run _zzz_nomatch_zzz ./... 2>/dev/null; fi; if [ -f requirements.txt ]; then pip install -r requirements.txt 2>/dev/null; fi; if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt 2>/dev/null; fi; if [ -f pyproject.toml ] || [ -f setup.py ]; then pip install -e ".[test,dev,tests]" 2>/dev/null || pip install -e . 2>/dev/null || (pip install poetry 2>/dev/null; poetry install 2>/dev/null); fi; if [ -f Gemfile ]; then (command -v bundle >/dev/null 2>&1 || gem install bundler >/dev/null 2>&1); (bundle install --jobs 4 --retry 3 2>/dev/null || bundle install 2>/dev/null); fi; if [ -f composer.json ]; then export COMPOSER_ALLOW_SUPERUSER=1; (command -v composer >/dev/null 2>&1) && (composer install --no-interaction --no-progress 2>/dev/null || composer update --no-interaction --no-progress 2>/dev/null); fi; if ls *.sln *.csproj */*.csproj **/*.csproj >/dev/null 2>&1; then (command -v dotnet >/dev/null 2>&1) && dotnet restore 2>/dev/null; fi; true


# offline-harbor: warm-by-running-pristine (observe not predict)
RUN set +e; cd /workspace/repo 2>/dev/null && ( cd /workspace/repo && bazel test //src/test/java/com/google/devtools/build/lib/exec:ExecTests --test_output=all && cat bazel-testlogs/src/test/java/com/google/devtools/build/lib/exec/ExecTests/test.xml ) >/dev/null 2>&1; true

# offline-harbor: grade-time offline SEAL + build-time completeness VERIFY (non-weakening: REAL resolution from the baked cache, ZERO network; same tests, same assertions)
ARG DEPWARM_STRICT=0
RUN set +e; cd /workspace/repo 2>/dev/null; export DEBIAN_FRONTEND=noninteractive; H="${HOME:-/root}"; mkdir -p /opt; : > /opt/depwarm_verify.log; echo '# offline dep-warm completeness verify (build-time, network-disabled resolution)' >> /opt/depwarm_verify.log; if ls pom.xml */pom.xml >/dev/null 2>&1 && command -v mvn >/dev/null 2>&1; then LR="$H/.m2/repository"; mkdir -p "$H/.m2" /etc/maven; SX='<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"><localRepository>'"$LR"'</localRepository><offline>true</offline></settings>'; printf '%s' "$SX" > "$H/.m2/settings.xml"; printf '%s' "$SX" > /etc/maven/settings.xml 2>/dev/null; MVNH="$(dirname "$(dirname "$(readlink -f "$(command -v mvn)")")")"; [ -d "$MVNH/conf" ] && printf '%s' "$SX" > "$MVNH/conf/settings.xml" 2>/dev/null; if mvn -o -q -B -Dmaven.test.skip=false test-compile >/tmp/_mvnv.log 2>&1; then echo 'maven  VERIFY=PASS (offline `mvn -o test-compile` resolved from baked ~/.m2)' >> /opt/depwarm_verify.log; else echo 'maven  VERIFY=FAIL (offline resolution INCOMPLETE — see tail)' >> /opt/depwarm_verify.log; grep -iE 'Unknown host|Could not resolve|Cannot access|Non-resolvable|Failed to (read|collect)|BUILD FAILURE' /tmp/_mvnv.log | head -8 >> /opt/depwarm_verify.log 2>/dev/null; fi; fi; if ls build.gradle build.gradle.kts settings.gradle settings.gradle.kts >/dev/null 2>&1; then for GH in "$H/.gradle" "${GRADLE_USER_HOME:-}" /root/.gradle; do [ -n "$GH" ] || continue; mkdir -p "$GH" 2>/dev/null; printf 'startParameter.offline = true\n' > "$GH/init.gradle" 2>/dev/null; done; GW=''; [ -x ./gradlew ] && GW=./gradlew; [ -z "$GW" ] && [ -x ./gradle ] && GW=./gradle; [ -z "$GW" ] && command -v gradle >/dev/null 2>&1 && GW=gradle; if [ -n "$GW" ]; then if $GW --no-daemon --offline -q testClasses >/tmp/_grv.log 2>&1; then echo 'gradle VERIFY=PASS (offline testClasses resolved from baked cache)' >> /opt/depwarm_verify.log; else echo 'gradle VERIFY=WARN (offline testClasses did not fully resolve — see tail)' >> /opt/depwarm_verify.log; grep -iE 'Could not (resolve|download|GET)|No cached version|offline mode|name resolution' /tmp/_grv.log | head -6 >> /opt/depwarm_verify.log 2>/dev/null; fi; fi; fi; if [ -f Gemfile ] && command -v bundle >/dev/null 2>&1; then bundle config set --global frozen true 2>/dev/null; if bundle check >/tmp/_bcv.log 2>&1; then echo 'bundler VERIFY=PASS (bundle check: every locked gem present)' >> /opt/depwarm_verify.log; else echo 'bundler VERIFY=WARN (repo-dir bundle check unsatisfied; may use a custom BUNDLE_GEMFILE — see tail)' >> /opt/depwarm_verify.log; grep -iE 'Could not find|is not yet installed|missing' /tmp/_bcv.log | head -6 >> /opt/depwarm_verify.log 2>/dev/null; fi; fi; if ls *.sln *.csproj */*.csproj >/dev/null 2>&1 && command -v dotnet >/dev/null 2>&1; then GPF="$(dotnet nuget locals global-packages -l 2>/dev/null | sed 's/^[^:]*: *//')"; [ -z "$GPF" ] && GPF="$H/.nuget/packages"; mkdir -p "$H/.nuget/NuGet"; NC='<?xml version="1.0" encoding="utf-8"?><configuration><fallbackPackageFolders><add key="depwarm-baked" value="'"$GPF"'" /></fallbackPackageFolders></configuration>'; printf '%s' "$NC" > "$H/.nuget/NuGet/NuGet.Config"; if dotnet build -c Debug --no-restore >/tmp/_ndv.log 2>&1 || dotnet build --no-restore >/tmp/_ndv.log 2>&1; then echo 'nuget  VERIFY=PASS (build --no-restore succeeded against baked packages)' >> /opt/depwarm_verify.log; else echo 'nuget  VERIFY=WARN (no-restore build did not fully succeed — see tail)' >> /opt/depwarm_verify.log; grep -iE 'NU1[0-9]{3}|Unable to load|unable to find|not restored' /tmp/_ndv.log | head -6 >> /opt/depwarm_verify.log 2>/dev/null; fi; fi; if [ -f composer.json ] && command -v composer >/dev/null 2>&1; then export COMPOSER_ALLOW_SUPERUSER=1; if composer check-platform-reqs --no-interaction >/tmp/_cpv.log 2>&1 || [ -d vendor ]; then echo 'composer VERIFY=PASS (vendor/ present; platform reqs checked)' >> /opt/depwarm_verify.log; else echo 'composer VERIFY=WARN (vendor/ may be incomplete)' >> /opt/depwarm_verify.log; fi; fi; if [ -f go.mod ] && command -v go >/dev/null 2>&1; then go env -w GOPROXY=off GOFLAGS=-mod=mod GOSUMDB=off GONOSUMCHECK=1 2>/dev/null; if go build ./... >/tmp/_gov.log 2>&1; then echo 'go     VERIFY=PASS (offline `go build ./...` resolved from the warmed module cache; GOPROXY=off)' >> /opt/depwarm_verify.log; else echo 'go     VERIFY=WARN (offline go build did not fully resolve — see tail)' >> /opt/depwarm_verify.log; grep -iE 'cannot find module|missing go.sum|dial tcp|proxy.golang|no required module|lookup .* on ' /tmp/_gov.log | head -6 >> /opt/depwarm_verify.log 2>/dev/null; fi; fi; if [ -f Cargo.toml ] && command -v cargo >/dev/null 2>&1; then CH="${CARGO_HOME:-$H/.cargo}"; mkdir -p "$CH"; printf '[net]\noffline = true\n' > "$CH/config.toml"; printf '[net]\noffline = true\n' > "$CH/config" 2>/dev/null; if cargo build --offline >/tmp/_crv.log 2>&1 || cargo check --offline >/tmp/_crv.log 2>&1; then echo 'cargo  VERIFY=PASS (offline `cargo build/check` resolved from the vendored registry cache)' >> /opt/depwarm_verify.log; else echo 'cargo  VERIFY=WARN (offline cargo build did not fully resolve — see tail)' >> /opt/depwarm_verify.log; grep -iE 'no matching package|failed to (get|download)|unable to get packages|registry index|network failure' /tmp/_crv.log | head -6 >> /opt/depwarm_verify.log 2>/dev/null; fi; fi; if [ -f package.json ]; then if command -v npm >/dev/null 2>&1; then npm config set offline true 2>/dev/null; npm config set prefer-offline true 2>/dev/null; npm config set audit false 2>/dev/null; npm config set fund false 2>/dev/null; fi; if command -v yarn >/dev/null 2>&1; then yarn config set enableGlobalCache true 2>/dev/null; yarn config set prefer-offline true 2>/dev/null; yarn config set yarn-offline-mirror "$H/.yarn-offline-mirror" 2>/dev/null; fi; if [ -d node_modules ]; then echo 'npm/yarn VERIFY=PASS (node_modules present; offline+prefer-offline set in ~/.npmrc)' >> /opt/depwarm_verify.log; else echo 'npm/yarn VERIFY=WARN (no node_modules — grade-time install must resolve from the warmed cache)' >> /opt/depwarm_verify.log; fi; fi; if command -v pip >/dev/null 2>&1 && { [ -f requirements.txt ] || [ -f pyproject.toml ] || [ -f setup.py ]; }; then WH=/opt/pip-wheelhouse; mkdir -p "$WH"; ([ -f requirements.txt ] && pip wheel -w "$WH" -r requirements.txt 2>/dev/null); (pip wheel -w "$WH" . 2>/dev/null); if ls "$WH"/*.whl >/dev/null 2>&1; then mkdir -p /etc "$H/.config/pip"; PC='[global]\nno-index = true\nfind-links = '"$WH"'\n'; printf "$PC" > /etc/pip.conf; printf "$PC" > "$H/.config/pip/pip.conf"; echo 'pip    VERIFY=PASS (wheelhouse built at /opt/pip-wheelhouse; grade-time pip is no-index find-links)' >> /opt/depwarm_verify.log; else echo 'pip    VERIFY=SKIP (no wheelhouse built — package pre-installed at build; no grade-time no-index applied)' >> /opt/depwarm_verify.log; fi; fi; echo '---- /opt/depwarm_verify.log ----'; cat /opt/depwarm_verify.log; if [ "${DEPWARM_STRICT}" = "1" ] && grep -q 'VERIFY=FAIL' /opt/depwarm_verify.log; then echo 'DEPWARM_STRICT: offline dep-warm INCOMPLETE — failing build'; exit 17; fi; true
# ---- Harbor harness deps (tmux + asciinema) baked at build for offline eval ----
RUN (command -v tmux >/dev/null 2>&1 && command -v asciinema >/dev/null 2>&1) \
    || (apt-get update && apt-get install -y --no-install-recommends tmux asciinema \
        && rm -rf /var/lib/apt/lists/*) || true

# ---- verifier-integrity: FULL immutable pristine snapshot of the base tree (graded-surface restore source for tests/test.sh) ----
RUN set +e; mkdir -p /opt/pristine; cd /workspace/repo 2>/dev/null && \
    { git archive HEAD 2>/dev/null | tar -x -C /opt/pristine 2>/dev/null \
      || cp -a /workspace/repo/. /opt/pristine/ 2>/dev/null; }; \
    chmod -R a-w /opt/pristine 2>/dev/null; \
    chattr -R +i /opt/pristine 2>/dev/null; true

# ---- verifier-integrity: immutable snapshot of the RUNNER-EXECUTABLE surface (wrappers + node_modules/.bin + runner package BODIES + all node_modules package.json + vendor/bin) for tests/test.sh (2e) restore ----
RUN set +e; mkdir -p /opt/runner_pristine; cd /workspace/repo 2>/dev/null && \
    { find . \( -name gradlew -o -name gradlew.bat -o -name mvnw -o -name mvnw.cmd \) -o -path '*/gradle/wrapper/*' -o -path '*/node_modules/.bin/*' -o -path '*/vendor/bin/*' -o -path '*/bin/*' -o -path '*/node_modules/vitest/*' -o -path '*/node_modules/@vitest/*' -o -path '*/node_modules/jest/*' -o -path '*/node_modules/jest-cli/*' -o -path '*/node_modules/@jest/*' -o -path '*/node_modules/mocha/*' -o -path '*/node_modules/jasmine/*' -o -path '*/node_modules/jasmine-core/*' -o -path '*/node_modules/ava/*' -o -path '*/node_modules/tap/*' -o -path '*/node_modules/tape/*' -o -path '*/node_modules/uvu/*' -o -path '*/node_modules/vite/*' -o -path '*/node_modules/ts-node/*' -o -path '*/node_modules/tsx/*' -o -path '*/node_modules/*/package.json' 2>/dev/null | sed 's#^\./##' ; } | while IFS= read -r f; do \
      [ -e "$f" ] || continue; mkdir -p "/opt/runner_pristine/$(dirname "$f")" 2>/dev/null; \
      cp -a "$f" "/opt/runner_pristine/$f" 2>/dev/null; \
    done; \
    mkdir -p /opt/toolchain_pristine; printf '%s' "$PATH" > /opt/trusted_path 2>/dev/null; \
    for tb in pytest py.test python python3 go gofmt mvn mvnw gradle ./gradlew node npm npx yarn pnpm jest vitest mocha cargo cargo-nextest rustc ctest cmake dotnet phpunit composer rspec ruby bundle rake make gmake ninja bazel bazelisk msbuild mix elixir erl swift swiftc clang gcc g++ tsc tsx ts-node ava tap; do \
      rp=$(command -v "$tb" 2>/dev/null) || continue; [ -f "$rp" ] || continue; \
      case "$rp" in /workspace/*) continue;; esac; \
      mkdir -p "/opt/toolchain_pristine$(dirname "$rp")" 2>/dev/null; \
      cp -a "$rp" "/opt/toolchain_pristine$rp" 2>/dev/null; \
    done; \
    for d in /usr/local/bin /usr/local/sbin; do [ -d "$d" ] || continue; \
      for x in "$d"/*; do [ -f "$x" ] || continue; \
        mkdir -p "/opt/toolchain_pristine$d" 2>/dev/null; cp -a "$x" "/opt/toolchain_pristine$x" 2>/dev/null; \
      done; done; \
    chmod -R a-w /opt/runner_pristine /opt/trusted_path /opt/toolchain_pristine 2>/dev/null; \
    chattr -R +i /opt/runner_pristine /opt/toolchain_pristine 2>/dev/null; chattr +i /opt/trusted_path 2>/dev/null; true

# ---- verifier-integrity: immutable snapshot of OUT-OF-REPO aux verifier helpers (/usr/local/{bin,sbin}/*.{sh,py,js}|run_*|setup_*|convert_* + /workspace top-level helpers) for tests/test.sh restore ----
RUN set +e; mkdir -p /opt/aux_pristine; \
    { find /usr/local/bin /usr/local/sbin -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' -o -name '*.js' -o -name '*.rb' -o -name 'run_*' -o -name 'setup_*' -o -name 'convert_*' \) 2>/dev/null; \
      find /workspace /tmp -maxdepth 1 -type f \( -name '*.py' -o -name '*.sh' -o -name '*.js' -o -name '*.rb' -o -name '*_hook.*' -o -name 'run_*' -o -name 'setup_*' -o -name 'check_*' \) 2>/dev/null; } | while IFS= read -r f; do \
      [ -e "$f" ] || continue; mkdir -p "/opt/aux_pristine$(dirname "$f")" 2>/dev/null; \
      cp -a "$f" "/opt/aux_pristine$f" 2>/dev/null; \
    done; chmod -R a-w /opt/aux_pristine 2>/dev/null; chattr -R +i /opt/aux_pristine 2>/dev/null; true

# offline-harbor: git blob-drop shrink (client-contract .git<100MB, HEAD==base)
RUN set +e; cd /workspace/repo 2>/dev/null && ( rm -rf .git/modules .git/worktrees 2>/dev/null; H=$(git rev-parse HEAD 2>/dev/null); [ -n "$H" ] && git update-ref --no-deref HEAD "$H" 2>/dev/null; git remote remove origin 2>/dev/null; git tag -l | xargs -r git tag -d >/dev/null 2>&1; git for-each-ref --format='%(refname)' refs/remotes refs/tags 2>/dev/null | xargs -r -n1 git update-ref -d 2>/dev/null; git for-each-ref --format='%(refname)' refs/heads 2>/dev/null | xargs -r -n1 git update-ref -d 2>/dev/null; [ -n "$H" ] && printf "%s\n" "$H" > .git/shallow; git reflog expire --expire=now --all 2>/dev/null; rm -rf .git/logs; { git rev-list --objects HEAD 2>/dev/null | awk '{print $1}'; printf "%s\n" "$H"; } | git cat-file --batch-check='%(objectname) %(objecttype)' 2>/dev/null | awk '$2!="blob"&&$1~/^[0-9a-f]{40}$/{print $1}' | sort -u > /tmp/_keep.txt; if [ ! -s /tmp/_keep.txt ]; then git cat-file --batch-all-objects --batch-check='%(objectname) %(objecttype)' 2>/dev/null | awk '$2!="blob"{print $1}' > /tmp/_keep.txt; fi; if [ -s /tmp/_keep.txt ]; then git pack-objects --quiet /tmp/_kp < /tmp/_keep.txt >/dev/null 2>&1 && rm -rf .git/objects/pack && mkdir -p .git/objects/pack && find .git/objects -maxdepth 1 -type d -name '[0-9a-f][0-9a-f]' -exec rm -rf {} + 2>/dev/null; mv /tmp/_kp-*.pack /tmp/_kp-*.idx .git/objects/pack/ 2>/dev/null; fi; git rev-parse HEAD >/dev/null 2>&1 || echo "WARN head-broken"; du -sm .git 2>/dev/null | cut -f1 ) ; true

# --- client-req: expose toolchain on the LOGIN shell PATH (bash -lc) ---
RUN set +e; \
    for b in cargo rustc rustup cargo-nextest go gofmt node npm npx yarn pnpm python3 pip3 \
             java javac mvn gradle ruby bundle gem php composer dotnet dub swift clang gcc; do \
      p="$(command -v "$b" 2>/dev/null)"; \
      [ -n "$p" ] && [ "$p" != "/usr/local/bin/$b" ] && ln -sf "$p" "/usr/local/bin/$b"; \
    done; \
    printf 'export PATH="%s:$PATH"\n' "$PATH" > /etc/profile.d/99-toolchain.sh; \
    for v in CARGO_HOME RUSTUP_HOME GOROOT GOPATH JAVA_HOME NVM_DIR PYENV_ROOT; do \
      val="$(printenv "$v" 2>/dev/null)"; [ -n "$val" ] && echo "export $v=\"$val\"" >> /etc/profile.d/99-toolchain.sh; \
    done; \
    chmod 0644 /etc/profile.d/99-toolchain.sh; true

# offline-harbor: harness-integrity smoke check (fail-loud: tar/gzip/git/python3 must work under the graded env)
RUN set -e; tar --version >/dev/null; gzip --version >/dev/null; git --version >/dev/null; python3 --version >/dev/null; d=$(mktemp -d); echo ok > "$d/f"; tar czf "$d/a.tgz" -C "$d" f; tar tzf "$d/a.tgz" >/dev/null; rm -rf "$d"; echo 'harness-integrity OK'
