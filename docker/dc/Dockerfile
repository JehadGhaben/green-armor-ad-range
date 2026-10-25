FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive
# samba-ad-dc pulls in Winbind, while samba-ad-provision ships the AD schema
# and provisioning files. Both are explicitly installed: Debian's recommends
# are intentionally disabled to keep the image compact.
RUN apt-get update && apt-get install -y --no-install-recommends \
    samba samba-ad-dc samba-ad-provision winbind \
    samba-dsdb-modules samba-vfs-modules \
    krb5-user dnsutils netcat-openbsd ca-certificates python3 bash \
    && rm -rf /var/lib/apt/lists/* \
    && test -x /usr/sbin/winbindd \
    && test -f /usr/share/samba/setup/ad-schema/AD_DS_Attributes__Windows_Server_2012_R2.ldf

COPY entrypoint.sh /usr/local/bin/armor-dc-entrypoint
RUN chmod 755 /usr/local/bin/armor-dc-entrypoint

EXPOSE 53/tcp 53/udp 88/tcp 88/udp 135/tcp 139/tcp 389/tcp 389/udp 445/tcp 464/tcp 464/udp 3268/tcp
ENTRYPOINT ["/usr/local/bin/armor-dc-entrypoint"]
