#!/bin/bash

ENV_FILE=".env"
GPG_FILE=".env.gpg"

# 복호화할 파일이 존재하는지 확인
if [ ! -f "$GPG_FILE" ]; then
  echo "❌ Encrypted file '$GPG_FILE' not found."
  exit 1
fi

# 사용자로부터 패스프레이즈 입력 받기
read -s -p "🔐 Enter passphrase to decrypt .env.gpg: " PASSPHRASE
echo

# 복호화 시도
gpg --quiet --batch --yes --passphrase="$PASSPHRASE" -o "$ENV_FILE" -d "$GPG_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Successfully decrypted to '$ENV_FILE'."
else
  echo "❌ Failed to decrypt. Check your passphrase."
fi
