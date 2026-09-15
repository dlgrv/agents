# GitFlic Runner — docker compose (verified this session, GitFlic CE 4.12.2/4.13.0)

Place in e.g. `/opt/gitflic-runner/docker-compose.yaml`, then:
```bash
cd /opt/gitflic-runner
docker compose -p gitflic-runner -f ./docker-compose.yaml up -d
```
Stop / relieve memory (e.g. on a 4 GB box after OOM):
```bash
docker compose -p gitflic-runner -f ./docker-compose.yaml down
```

## Lessons
- Image is `registry.gitflic.ru/company/gitflic/runner:latest` (NOT `gitflic-runner`).
- `network_mode: host` lets the runner reach GitFlic directly, dodging the
  self-signed TLS on :8080 (no need to go through nginx/HTTPS).
- REG_URL = `http(s)://<host>[:port]/-/runner/registration` (copy from
  Admin → CI/CD → Runners → "Add this registration token").
- `DIDENABLE: false` + mounted `/var/run/docker.sock` → jobs run on host Docker.
- Leave `TAGS: ""` unless you deliberately tag jobs in `gitflic-ci.yaml`.

## Template (fill REG_URL / REG_TOKEN)
```yaml
services:
    runner:
        container_name: gitflic-runner
        image: registry.gitflic.ru/company/gitflic/runner:latest
        environment:
            DOCKER_REGISTRY_USERNAME: ""
            DOCKER_REGISTRY_PASSWORD: ""
            DOCKER_REGISTRY_URL: "https://registry.gitflic.ru"
            REG_URL: "<REG_URL>"
            REG_TOKEN: "<REG_TOKEN>"
            NAME: "gitflic-runner-1"
            TAGS: ""
            LOG_LEVEL: INFO
            IN_SESSION: true
            DIDENABLE: false
            PRIVILEGED: false
            CONCURRENCY_MODE: DEFAULT
            LIMIT_OF_CONCURRENCY_TO_PROCESS_JOBS: 8
        volumes:
        - /var/run/docker.sock:/var/run/docker.sock
        - runner-config:/gitflic-runner/config
        - runner-log:/gitflic-runner/log
        network_mode: host
        restart: unless-stopped
volumes:
    runner-config:
        name: runner-config
    runner-log:
        name: runner-log
```
