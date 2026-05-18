# Changelog

All notable changes to this project are documented in this file.

## [0.10.0] - 2026-05-18

### Changed
- Bumped IOx package and Docker base image to Alpine 3.21 (from EOL 3.15).
- Pinned Python dependencies (`paho-mqtt`, `pynmea2`, `requests`) for reproducible builds.
- `build.sh` always syncs `package.yaml` with `VERSION` and uses `--platform linux/arm64`.
- Hardened `startup.sh` config loading (quoted paths, safe `export key=value`).
- Fixed consumer publish logic for nested `location` / `gps_qual` queue payloads.
- Redacted MQTT password in application logs.
- Added HTTP request timeouts and narrower exception handling.

### Fixed
- Added missing `requests` dependency to `requirements.txt`.
- Docker image uses a build-stage venv and `PYTHONPATH` for portable site-packages (Alpine 3.21 PEP 668).
- Docker `CMD` uses exec form for reliable startup.

### Documentation
- README updated for v0.10, buildx, configuration, payload format, and privacy notes.

## [0.9.0] - (unreleased tag)

- Version drift between `package.yaml` and `VERSION` file in development tree.

## [0.8.0] - (unreleased tag)

- In-tree `VERSION` file at 0.8 during development.

## [0.7.0] - 2024

- Multi-queue producer/consumer architecture (MQTT + HTTP).
- HTTP consumer and CLI upgrade documentation.
- Reduced container image size.
- Git tag `v0.7`.

### Earlier history

- Initial MQTT-focused release with producer/consumer split and store-and-forward queues.
