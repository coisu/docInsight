# Makefile
.PHONY: build run stop decrypt-env encrypt-env

build: decrypt-env
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

re: stop build run

logs:
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning Docker containers, images, and volumes..."
	docker-compose down -v --rmi local --remove-orphans
	@echo "🧼 Removing compiled Python files and local data..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +
	rm -rf data/embeddings/index.faiss data/embeddings/metadata.pkl

decrypt-env:
	@bash -c '\
	read -s -p "🔐 Enter passphrase to decrypt .env.gpg: " PASSPHRASE; \
	echo ""; \
	if [ ! -f .env.gpg ]; then \
		echo "❌ .env.gpg file not found."; \
		exit 1; \
	fi; \
	gpg --quiet --batch --yes --passphrase="$$PASSPHRASE" -o .env -d .env.gpg && \
	echo "✅ .env file successfully decrypted." || \
	echo "❌ Failed to decrypt .env.gpg." \
	'

encrypt-env:
	@bash -c '\
	if [ ! -f .env ]; then \
		echo "❌ .env file not found."; \
		exit 1; \
	fi; \
	read -s -p "🔐 Enter passphrase to encrypt .env: " PASSPHRASE; \
	echo ""; \
	gpg --quiet --batch --yes --passphrase="$$PASSPHRASE" -c .env && \
	echo "✅ .env file encrypted to .env.gpg." || \
	echo "❌ Failed to encrypt .env." \
	'
