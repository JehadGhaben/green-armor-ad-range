#!/usr/bin/env bash
set -Eeuo pipefail

SCENARIO="/run/armor/scenario.json"
READY="/var/lib/samba/.armor-ready"

fail() {
  printf '[!] %s\n' "$*" >&2
  exit 1
}

[[ -r "$SCENARIO" ]] || fail 'Missing scenario seed. Launch from project root: python3 armorlab.py up'
[[ -x /usr/sbin/winbindd ]] || fail 'Missing winbindd. Rebuild the DC image without cache.'
[[ -f /usr/share/samba/setup/ad-schema/AD_DS_Attributes__Windows_Server_2012_R2.ldf ]] || fail 'Missing samba-ad-provision schema. Rebuild the DC image.'

# Secrets are locally generated; none are committed to Git.
eval "$(python3 - "$SCENARIO" <<'PY'
import json, shlex, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
for name, key in (("ADMIN_PASSWORD", "admin_password"),
                  ("SERVICE_PASSWORD", "service_password")):
    print(f"{name}={shlex.quote(data[key])}")
for index in range(1, 5):
    print(f"FLAG_{index}={shlex.quote(data['flags'][f'{index:02d}'])}")
PY
)"

# A failed first start can leave an incomplete sam.ldb. Fail instead of treating
# this as a valid pre-existing domain. The reset command repairs the state.
if [[ ! -f "$READY" ]]; then
  if [[ -e /var/lib/samba/private/sam.ldb ]]; then
    fail 'Incomplete AD volume detected. For a fresh lab run: python3 armorlab.py reset --yes && python3 armorlab.py up'
  fi
  echo '[+] Provisioning training Active Directory ARMOR.TEST'
  mkdir -p /etc/samba /var/lib/samba /srv/armor
  rm -f /etc/samba/smb.conf
  samba-tool domain provision \
    --server-role=dc \
    --realm=ARMOR.TEST \
    --domain=ARMOR \
    --dns-backend=SAMBA_INTERNAL \
    --use-rfc2307 \
    --adminpass="$ADMIN_PASSWORD"

  # LDAP relaxed authentication is a deliberate training misconfiguration.
  # It MUST be in [global], not in a share section, otherwise Samba ignores it.
  python3 - /etc/samba/smb.conf <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
content = path.read_text(encoding='utf-8')
if '[global]' not in content.lower():
    raise SystemExit('Provisioning did not create a valid [global] section')
lines = content.splitlines()
found = False
for index, line in enumerate(lines):
    if line.strip().lower() == '[global]':
        lines.insert(index + 1, '    ldap server require strong auth = no')
        found = True
        break
if not found:
    raise SystemExit('Missing global section')
path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY

  cat >> /etc/samba/smb.conf <<'EOF_SHARES'

[GA-Public]
    path = /srv/armor/public
    read only = yes
    browseable = yes
    guest ok = no

[GA-Archive]
    path = /srv/armor/archive
    read only = yes
    browseable = yes
    guest ok = no
    valid users = ARMOR\svc_backup
EOF_SHARES

  # Exit promptly on malformed configuration, avoiding endless restarts.
  testparm -s >/dev/null 2>&1 || fail 'Generated smb.conf is invalid (testparm failed).'

  # Deliberately vulnerable class-only directory identities and memberships.
  samba-tool group add GA-Helpdesk
  samba-tool group add GA-IT-Operations
  samba-tool user create student01 'GreenArmor2026!' --given-name=Student --surname=Analyst \
    --description='Training cohort account. Review GA-Public before making changes.'
  samba-tool user create m.salem 'TrainingOnly2026!' --given-name=Mariam --surname=Salem \
    --description='Helpdesk technician'
  samba-tool user create t.nasser 'TrainingOnly2026!' --given-name=Tariq --surname=Nasser \
    --description='IT operations staff'
  samba-tool user create svc_backup "$SERVICE_PASSWORD" --given-name=Archive --surname=Service \
    --description="Legacy archive automation | assessment token: $FLAG_2"
  samba-tool group addmembers GA-Helpdesk m.salem
  samba-tool group addmembers GA-IT-Operations t.nasser
  samba-tool group addmembers GA-IT-Operations svc_backup

  install -d -m 755 /srv/armor/public/IT /srv/armor/public/Projects /srv/armor/archive/reports
  cat > /srv/armor/public/START-HERE.txt <<EOF_FLAG1
GREEN ARMOR ACADEMY // DIRECTORY OPERATIONS
Realm: ARMOR.TEST
Discovery ticket: $FLAG_1

Authenticated domain users can read this onboarding folder.
Use LDAP to review the directory accounts and their descriptions.
EOF_FLAG1
  cat > /srv/armor/public/Projects/architecture.txt <<'EOF_ARCH'
ARMOR.TEST
  DC01       Samba Active Directory domain controller
  GA-Public  Authenticated read-only share
  GA-Archive Service-account-only restricted share

Review directory information exposure and the principle of least privilege.
EOF_ARCH
  cat > /srv/armor/public/IT/legacy-integration.ini <<EOF_FLAG3
# Deliberately exposed training-only service configuration
service_domain=ARMOR
service_username=svc_backup
service_password=$SERVICE_PASSWORD
tracking_reference=$FLAG_3
EOF_FLAG3
  cat > /srv/armor/archive/reports/security-review.txt <<EOF_FLAG4
GREEN ARMOR ACADEMY // OPERATIONS ARCHIVE
A leaked service credential can grant unintended access to this archive.
Investigation reference: $FLAG_4

Document root cause, impact, evidence and a least-privilege remediation.
EOF_FLAG4
  chmod -R a+rX /srv/armor

  # Require the primary domain DB and all four challenge artifacts before
  # committing the ready marker. Partial state never silently passes startup.
  [[ -s /var/lib/samba/private/sam.ldb ]] || fail 'Provisioning did not create sam.ldb'
  [[ -s /srv/armor/archive/reports/security-review.txt ]] || fail 'Challenge archive not created'
  touch "$READY"
  echo '[+] AD domain provisioned and 4 training stages initialized.'
else
  [[ -s /var/lib/samba/private/sam.ldb ]] || fail 'Ready marker exists but domain DB is missing. Reset the lab.'
  echo '[+] Existing initialized training directory found.'
fi

if [[ -f /var/lib/samba/private/krb5.conf ]]; then
  cp /var/lib/samba/private/krb5.conf /etc/krb5.conf
fi

exec samba -i -M single
