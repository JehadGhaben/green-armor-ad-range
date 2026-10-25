#!/usr/bin/env python3
"""End-to-end tests of the REAL running Samba range (not mocked).

Run only after `python3 armorlab.py up`. Never print run-specific secrets.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'runtime' / 'state.json'


def exec_in(service: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ('docker', 'compose', '-f', str(ROOT / 'compose.yaml'),
         'exec', '-T', service, *args),
        cwd=ROOT, capture_output=True, text=True, check=False, timeout=75,
    )


def check(label: str, result: subprocess.CompletedProcess[str],
          *, success: bool = True, contains: str = '') -> bool:
    good = (result.returncode == 0) == success
    if contains:
        good = good and contains in (result.stdout + result.stderr)
    print(f"[{'PASS' if good else 'FAIL'}] {label}")
    if not good:
        print(f"       exit code: {result.returncode} (details: python3 armorlab.py logs)")
    return good


def main() -> int:
    if not STATE.exists():
        print('Start the range first: python3 armorlab.py up')
        return 2
    state = json.loads(STATE.read_text(encoding='utf-8'))
    student = r'ARMOR\student01%GreenArmor2026!'
    service = 'ARMOR\\svc_backup%' + state['service_password']

    checks = []
    checks.append(check('Samba configuration valid', exec_in('dc', 'testparm', '-s')))
    checks.append(check('Winbind executable present', exec_in('dc', 'test', '-x', '/usr/sbin/winbindd')))
    checks.append(check('Student DNS can resolve DC', exec_in('student', 'getent', 'hosts', 'dc')))
    checks.append(check('Student SMB connection', exec_in('student', 'nc', '-z', 'dc', '445')))
    checks.append(check('AD Kerberos connection', exec_in('student', 'nc', '-z', 'dc', '88')))
    checks.append(check('Samba AD DNS SRV record', exec_in(
        'student', 'dig', '+short', '@dc', '_ldap._tcp.armor.test', 'SRV'), contains='dc01'))
    checks.append(check('Student LDAP connection', exec_in('student', 'nc', '-z', 'dc', '389')))

    # Flag 01 must be discoverable over an authenticated share.
    checks.append(check('Authenticated public share', exec_in(
        'student', 'smbclient', '//dc/GA-Public', '-U', student,
        '-c', 'get START-HERE.txt /tmp/ga-flag01.txt')))
    checks.append(check('Flag 01 on public share', exec_in(
        'student', 'cat', '/tmp/ga-flag01.txt'), contains=state['flags']['01']))

    # Flag 02 must be visible to the legitimate student through LDAP.
    checks.append(check('Authenticated LDAP and flag 02', exec_in(
        'student', 'ldapsearch', '-x', '-H', 'ldap://dc',
        '-D', 'student01@armor.test', '-w', 'GreenArmor2026!',
        '-b', 'DC=armor,DC=test', '(sAMAccountName=svc_backup)', 'description'),
        contains=state['flags']['02']))

    checks.append(check('Exposed configuration available', exec_in(
        'student', 'smbclient', '//dc/GA-Public', '-U', student,
        '-c', 'get IT/legacy-integration.ini /tmp/ga-flag03.txt')))
    checks.append(check('Flag 03 in exposed configuration', exec_in(
        'student', 'cat', '/tmp/ga-flag03.txt'), contains=state['flags']['03']))

    # Negative check: initial student MUST NOT read the protected archive.
    checks.append(check('Archive denies initial student', exec_in(
        'student', 'smbclient', '//dc/GA-Archive', '-U', student,
        '-c', 'get reports/security-review.txt /tmp/ga-denied.txt'), success=False))
    checks.append(check('Archive accepts exposed service identity', exec_in(
        'student', 'smbclient', '//dc/GA-Archive', '-U', service,
        '-c', 'get reports/security-review.txt /tmp/ga-flag04.txt')))
    checks.append(check('Flag 04 in restricted archive', exec_in(
        'student', 'cat', '/tmp/ga-flag04.txt'), contains=state['flags']['04']))

    passed = sum(checks)
    print(f'\n{passed}/{len(checks)} end-to-end checks passed.')
    return 0 if passed == len(checks) else 1


if __name__ == '__main__':
    sys.exit(main())
