#!/bin/bash
cp pam_netsyms.py debian/lib/security/pam_netsyms.py
dpkg-deb -b debian netsyms-pam-auth_0.2_all.deb
