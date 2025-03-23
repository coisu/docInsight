# Makefile
.PHONY: build run stop

build: decrypt-mama
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

re: stop build run

logs:
	docker-compose logs -f

decrypt-env:
	@read -s -p "🔐 Enter passphrase to decrypt .env.gpg: " PASSPHRASE; \
	echo ""; \
	if [ ! -f .env.gpg ]; then \
		echo "❌ .env.gpg file not found."; \
		exit 1; \
	fi; \
	gpg --quiet --batch --yes --passphrase="$$PASSPHRASE" -o .env -d .env.gpg && \
	echo "✅ .env file successfully decrypted." || \
	echo "❌ Failed to decrypt .env.gpg."