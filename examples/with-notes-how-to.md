# How to Debug Slow Docker Builds in Local Development

Waiting six minutes for a one-line code change to build inside a container gets painful fast. Once you see where the cache breaks, you can usually drop that down under thirty seconds.

## Why Layer Caching Breaks Without You Noticing

Docker builds images layer by layer. If one step changes, every command below it runs again from scratch. The biggest trap I see is copying the whole project before running package installs. When you copy everything early, touching a single test file invalidates your cache. The engine downloads hundreds of packages again. That burns several minutes. I think this single mistake causes half of all slow build complaints. Moving that broad copy step towards the bottom avoids the penalty entirely.

## Splitting Your Dependency Step From Application Code

The fix here is simple. It takes two minutes to set up.

First copy only the dependency declarations, such as package.json and the lockfile. Run your install command right after that. Then copy the remaining source files into the image. This keeps your heavy dependency layer untouched as long as you have not added or updated a library. Your daily edits rebuild in seconds because Docker reuses the existing layer. If you work on monorepos with multiple workspaces, you might need to copy several package manifests before running the install command. It takes an extra minute to wire up the paths, but it pays off immediately on every subsequent branch checkout. In my opinion, this is the highest return change you can make to any Dockerfile.

## Turning On BuildKit for Parallel Execution

Old engines run steps in a strict single line. BuildKit is much smarter. It maps out dependencies between build stages and runs independent jobs at the same time. You enable it by setting the DOCKER_BUILDKIT environment variable to 1 in your shell profile. In my tests with our team repo, BuildKit shaved about 40 seconds off our clean runs. It skips unused stages entirely. I'd say there is almost no downside to leaving it on everywhere.

## Using Cache Mounts Instead of Repeated Downloads

Package managers download tarballs into a local cache directory. Inside a container build, that folder normally disappears once the command finishes. Adding a cache mount flag tells the builder to keep that cache on disk across builds.

When you run pip install or npm ci with a mounted cache, your tools read local disk before hitting remote registries. It helps a lot on slow internet connections. I personally lean towards mounting both the package manager cache and compiler caches on larger projects. Mounted caches shave real minutes off local compilations throughout the workday.

## Trimming Context Bloat With a Proper Dockerignore

If you lack a dockerignore file, Docker sends your whole folder to the daemon before step one even starts. It wastes bandwidth. I once watched an engineer wait while Docker sent 2 GB over local sockets because node_modules and old git history sat in the directory. Create a dot-dockerignore file right now. Add your git folder, local virtual environments, and test artifacts. A tiny build context starts instantly and keeps the engine running smoothly.

## Multi-Stage Builds to Keep Final Images Small

Compilers and testing libraries take up tons of space. They do not belong in production.

A multi-stage build lets you compile binaries inside a heavy image, then copy only the final executable into a slim runtime like Alpine. I usually run DevPulse Profiler on our staging builds to see which stages hold the most disk weight. Our finished image dropped from 1 GB down to roughly 85 MB. Smaller images start faster and push quickly across registries.

## Checking Layer Sizes and Clean Up Habits

Old layers build up quickly on local laptops. Run docker system df once a week to see what is eating disk. Clear stale build cache entries with the prune command when space gets tight. Honestly, a full disk hurts build performance more than people realize. Running a quick prune command every couple of weeks keeps your workstation reliable.
