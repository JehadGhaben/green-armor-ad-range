# UNIVERSITY PRACTICAL TASK
## OPERATION DIRECTORY — Active Directory Security Assessment

**Prepared by:** JEHAD GHABEN · GREEN ARMOR ACADEMY  
**Environment:** ARMOR.TEST · isolated Docker lab  
**Difficulty:** Beginner → Intermediate  
**Assessment:** 100 points / four flags

### Learning objectives

Understand AD domains, directory principals, SMB share enumeration, LDAP queries, permission boundaries, insecure storage of service account credentials, and responsible vulnerability reporting.

### Scenario

You are an entry-level security analyst assigned to assess the fictional organization **ARMOR.TEST**. An internal audit suspects that a legacy integration account has been mishandled. You have a limited-privilege domain account and must locate evidence, demonstrate business impact **inside the lab only**, and propose remediation.

### Initial access

- Domain: `ARMOR.TEST`
- Hostname: `dc`
- Account: `ARMOR\student01`
- Password: `GreenArmor2026!`
- Terminal: `python3 armorlab.py shell`

### Deliverables

1. Stage 01 — **15 pts:** Identify directory services and discover the first assessment flag in a legitimately accessible authenticated file share.
2. Stage 02 — **20 pts:** Enumerate LDAP users and relevant attributes; identify an unusual service-account description and obtain the second flag.
3. Stage 03 — **25 pts:** Find a mishandled configuration file, obtain the third flag, and explain why the contents constitute a security exposure.
4. Stage 04 — **40 pts:** Compare SMB permissions under the initial identity and the exposed identity; demonstrate access to the sensitive archive and obtain the final flag.

### Submission requirements

- Submit all found flags using `python3 armorlab.py submit 'GA{...}'` **on the host**.
- Attach a screenshot or a terminal transcript for each stage. Redact credentials from any report distributed publicly.
- Include a short vulnerability report: **finding, observation, affected resource, impact, severity rationale, recommended remediation**.
- Submit a score summary: `python3 armorlab.py score --json`.

### Rules

- Work on the isolated Docker environment only.
- Do not inspect the host-generated `runtime/` secrets or the AD volumes to collect flags.
- Do not use the Docker host administrator credentials as an attack shortcut.
- No real-world scanning, production credentials, Internet exposure, or unauthorized targets.
- The instructor may award report-quality points separately from the technical flag score.

### Hints

Use `python3 armorlab.py hint 01 1` and substitute other stage IDs or levels 1–3 if required. Strong submissions explain **how** the issue occurred, not merely where the flag was found.
