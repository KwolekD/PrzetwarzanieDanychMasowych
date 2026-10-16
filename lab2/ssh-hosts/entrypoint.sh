#!/bin/bash
set -e

# Użytkownik bez hasła - logowanie tylko kluczem z /tmp/key.pub
if ! id "$SSH_USER" >/dev/null 2>&1; then
    useradd -m -s /bin/bash "$SSH_USER"
    usermod -p '*' "$SSH_USER"
fi

install -d -m 700 -o "$SSH_USER" -g "$SSH_USER" "/home/$SSH_USER/.ssh"
install -m 600 -o "$SSH_USER" -g "$SSH_USER" /tmp/key.pub "/home/$SSH_USER/.ssh/authorized_keys"

exec /usr/sbin/sshd -D -e
