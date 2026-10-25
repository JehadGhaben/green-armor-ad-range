# Security policy — deliberately vulnerable classroom range

This is an educational Samba Active Directory **simulation** with intentionally weak LDAP and SMB settings. The Docker Compose network is `internal: true`, and no ports are published on the host. Do not connect the containers to the Internet, any real domain, or university/enterprise infrastructure.

The public repository must never contain `runtime/`, active service credentials, flags, or instructor-only solutions. Training usernames/passwords are fictional and must not be reused anywhere else.

Local grading is **not tamper-proof**. Learners controlling the container host can inspect volumes and locally generated state. Assess the student report and evidence instead of relying solely on `armorlab.py score`.

For unintended issues, contact the maintainers through https://www.greenarmor.academy without posting actual credentials or host secrets.
