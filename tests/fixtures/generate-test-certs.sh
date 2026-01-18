#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

# Generate self-signed test certificates for XML signing tests.
# These certificates are for testing only and should NOT be used in production.
#
# Requirements:
# - OpenSSL 3.0+ (for -addext support)
#
# Generated files:
# - test-private.pem: RSA 2048-bit private key
# - test-cert.pem: RSA self-signed certificate (1 year validity)
# - test-ec-private.pem: ECDSA P-256 private key
# - test-ec-cert.pem: ECDSA self-signed certificate (1 year validity)
#
# Certificate extensions (required by signxml strict validation):
# - basicConstraints: CA:FALSE (end-entity certificate)
# - keyUsage: digitalSignature
# - extendedKeyUsage: codeSigning
# - subjectAltName: DNS name (required by signxml)
# - subjectKeyIdentifier: auto-generated
# - authorityKeyIdentifier: auto-generated (self-referencing for self-signed)

set -euo pipefail

cd "$(dirname "$0")"

echo "Generating RSA test certificate..."
openssl genpkey -algorithm RSA -out test-private.pem -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key test-private.pem -out test-cert.pem -days 365 \
    -subj "/C=US/O=JuxLib/CN=Test" \
    -addext "basicConstraints=critical,CA:FALSE" \
    -addext "keyUsage=digitalSignature" \
    -addext "extendedKeyUsage=codeSigning" \
    -addext "subjectAltName=DNS:test.juxlib.local" \
    -addext "subjectKeyIdentifier=hash" \
    -addext "authorityKeyIdentifier=keyid:always"
chmod 600 test-private.pem

echo "Generating ECDSA test certificate..."
openssl ecparam -name prime256v1 -genkey -out test-ec-private.pem
openssl req -new -x509 -key test-ec-private.pem -out test-ec-cert.pem -days 365 \
    -subj "/C=US/O=JuxLib/CN=TestEC" \
    -addext "basicConstraints=critical,CA:FALSE" \
    -addext "keyUsage=digitalSignature" \
    -addext "extendedKeyUsage=codeSigning" \
    -addext "subjectAltName=DNS:testec.juxlib.local" \
    -addext "subjectKeyIdentifier=hash" \
    -addext "authorityKeyIdentifier=keyid:always"
chmod 600 test-ec-private.pem

echo "Done. Generated test certificates:"
ls -la test-*.pem

echo ""
echo "Certificate validity:"
openssl x509 -in test-cert.pem -noout -dates
openssl x509 -in test-ec-cert.pem -noout -dates
