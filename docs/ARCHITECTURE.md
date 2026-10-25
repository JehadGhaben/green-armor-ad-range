# Architecture & threat model

**GREEN ARMOR Directory Range** intentionally implements a small teaching slice of Active Directory with **Samba AD DC** rather than a full Windows domain. There are two Docker services:

- `dc`: Samba AD DC for `ARMOR.TEST` supporting AD LDAP, SMB, Kerberos KDC, and AD DNS.
- `student`: a separate Debian toolbox with `smbclient`, `ldapsearch`, `dig`, `kinit`, `nmap`, and network utilities.

Both join `training`, an **internal Docker bridge network** with **no published ports**. The student can resolve `dc` using Docker's embedded DNS; native AD SRV queries are directed explicitly to Samba DNS using `dig @dc`.

## Onboarding identity

`student01` is a standard account. Sample co-worker accounts and a service account are provisioned so students can enumerate principals and group membership.

## Intentionally insecure elements

1. The general `GA-Public` share is readable by authenticated accounts, including broad IT information that should have been access restricted.
2. A service account has a flag-bearing description in LDAP, used to teach identification of atypical service-account metadata.
3. The IT share contains a plaintext legacy integration config with the service account's credentials. That is the key failure in the chain.
4. The leaked service account has share access to the restricted `GA-Archive`, illustrating blast radius through credential reuse/overprivilege.
5. The Samba LDAP simple-bind policy is relaxed **only to simplify local training**. It must not be mirrored in a production network.

## Dynamic flags

The host CLI uses Python's `secrets` module to generate flag values on initialization and writes them into `runtime/`. The bootstrap script seeds corresponding locations when the AD volume is created. All runtime answer files are covered by `.gitignore`.

Four flags follow the shape `GA{NN-RANDOMHEX}`. Correct submissions are compared with `hmac.compare_digest` and stage progress is stored locally.

## Limitations / integrity

This is not an adversarial multi-tenant platform. Local student Docker hosts are **not trusted**: Docker administrators can view volumes, service files, and answers. For graded events, deploy on instructor-controlled infrastructure and supervise logs, or use the range as a formative assessment with written evidence.

No domain trusts, AD CS, realistic Windows workstation exploit chains, or Group Policy privilege escalation are included. The range is intended to be extended by new scenario directories in future versions.
