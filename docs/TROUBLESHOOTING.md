# Validation and troubleshooting

## Validate before distribution

```bash
python3 armorlab.py doctor
python3 armorlab.py up
python3 armorlab.py status
python3 scripts/smoke-test.py
python3 armorlab.py shell
```

The smoke script checks the **actual** running AD environment, LDAP auth, SMB shares, each flag's location, and both sides of the restricted archive access rule. No secrets are printed. GitHub Actions runs the same test using an actual Docker Engine runner after code is uploaded.

## If the Domain Controller exits

```bash
python3 armorlab.py logs
# or inspect stopped containers:
docker compose ps -a
```

**Missing AD schema:** The image explicitly installs `samba-ad-provision`; the `Dockerfile` fails its build if the required AD schema file is absent. Rebuild with `docker compose build --no-cache dc`.

**Missing winbindd:** The image explicitly installs `samba-ad-dc` and `winbind`. The Dockerfile asserts `/usr/sbin/winbindd` exists. Rebuild with `docker compose build --no-cache dc`.

**Incomplete AD volume:** If provisioning fails halfway through, the next startup will **stop explicitly** rather than treat a partial `sam.ldb` as valid. On a new lab only, after you confirm no student progress needs preservation, reset the volumes:

```bash
python3 armorlab.py reset --yes
python3 armorlab.py up
python3 scripts/smoke-test.py
```

This DESTROYS prior flags and scores. Never reset a student's working instance without asking them.

**LDAP global configuration warnings:** The startup script inserts the intentionally relaxed `ldap server require strong auth = no` directive directly inside `[global]`, validates `smb.conf` via `testparm`, then adds `[GA-Public]` and `[GA-Archive]` share sections.

**Cannot connect from host:** Intentional: no ports are published. Use `python3 armorlab.py shell` to enter the `student` container and talk to `dc` there.

**DNS:** For native AD SRV records, query `dig @dc _ldap._tcp.armor.test SRV` from the student container. Docker's normal alias lookup does not provide AD SRV records.

**Parrot and Podman:** A `docker` command can actually be a Podman compatibility wrapper on some Parrot installations. This project's primary supported runtime is **Docker Engine + Compose v2**. Confirm the engine behind `docker --version` and `docker info`. Podman has differing compose networking/health behavior and is not validated by Docker-based CI.

## Release checklist

1. Code/unit job green on GitHub Actions.
2. **`real-docker-smoke` green** on GitHub Actions.
3. Local `python3 scripts/smoke-test.py` passes all checks on the instructor's target runtime.
4. `runtime/` and solutions are not committed.
5. Students receive the correct public clone URL and the `docs/STUDENT_TASK.md` assignment.
