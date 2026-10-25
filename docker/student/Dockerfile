FROM debian:12-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    smbclient ldap-utils dnsutils netcat-openbsd nmap krb5-user \
    python3 python3-ldap3 iputils-ping ca-certificates bash less && \
    rm -rf /var/lib/apt/lists/*
RUN printf '[libdefaults]\n default_realm = ARMOR.TEST\n dns_lookup_kdc = false\n rdns = false\n[realms]\n ARMOR.TEST = {\n  kdc = dc\n  admin_server = dc\n }\n[domain_realm]\n .armor.test = ARMOR.TEST\n armor.test = ARMOR.TEST\n' > /etc/krb5.conf
WORKDIR /home/student
CMD ["sleep", "infinity"]
