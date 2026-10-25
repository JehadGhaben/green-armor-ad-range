# Changelog

## 0.2.0 — Clean repository rebuild (2026-10-25)

- New standalone repository identity `green-armor-ad-range`, keeping JEHAD GHABEN and GREEN ARMOR ACADEMY credits.
- DC image explicitly installs `samba-ad-dc`, `samba-ad-provision` and `winbind`, and checks required files during image build.
- Correct LDAP security training option placement inside `[global]` instead of SMB share sections.
- Detect failed or partial first-time AD initialization instead of silently accepting corrupt persistent volumes.
- Fail-fast DC startup and improved health probing for SMB and LDAP.
- End-to-end smoke checks of all 4 flags, LDAP, public share, denied initial archive access, and permitted service-account access.
- GitHub Actions workflow now includes a **real Docker integration job** after static checks. Check that result before teaching.
- Refreshed Arabic/English guides and Parrot/Podman troubleshooting.

**Honest status:** static validation completed; real Docker integration must be confirmed via GitHub Actions / instructor host after upload.
