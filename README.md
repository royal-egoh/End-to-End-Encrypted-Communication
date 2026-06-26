# Cipher

A private, end-to-end encrypted messaging app. Messages are encrypted on your device before they ever leave it — the server never sees your plaintext.

🔗 **Live:** [cipher-5ajs.onrender.com](https://cipher-5ajs.onrender.com)

---

## What It Does

- End-to-end encrypted messaging between users
- Keys generated on your device, never sent to the server
- Private key encrypted with your PIN before storage
- Real-time messaging via WebSockets
- Offline message delivery — messages queue and deliver when you reconnect

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL (Neon) |
| Real-time | WebSockets |
| Encryption | Web Crypto API (RSA-OAEP + AES-GCM) |
| Frontend | Vanilla HTML/CSS/JS |
| Hosting | Render |

---

## How The Encryption Works

1. On registration, your browser generates an RSA key pair locally
2. Your private key is encrypted with your PIN using AES-GCM (via PBKDF2 key derivation)
3. Only the encrypted private key and your public key are sent to the server
4. The server stores your public key to allow others to encrypt messages to you
5. The server never sees your PIN, your private key, or your message plaintext

```
Registration:
  Browser generates RSA key pair
  Private key encrypted with PIN → stored on server
  Public key → stored on server (used by others to encrypt to you)

Sending a message:
  Fetch recipient's public key from server
  Encrypt message in browser
  Send ciphertext to server
  Server stores and forwards — never sees plaintext

Receiving a message:
  Fetch ciphertext from server
  Decrypt in browser using your private key
```

---

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/YOURUSERNAME/cipher.git
cd cipher
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root:

```
DATABASE_URL=postgresql://user:password@host/dbname
SECRET_KEY=your-secret-key
```

### 4. Run the app

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

---

## Project Structure

```
cipher/
  main.py          # FastAPI app, routes, WebSocket handler
  models.py        # SQLAlchemy database models
  auth.py          # JWT authentication
  static/
    chat.js        # Frontend logic, encryption, WebSocket client
  templates/
    index.html     # Chat UI
    login.html     # Login page
    register.html  # Registration page
  requirements.txt
  .env             # Never committed
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |

---

## Deployment

Deployed on [Render](https://render.com) with a [Neon](https://neon.tech) managed Postgres database.

```
Build command:  pip install -r requirements.txt
Start command:  uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Known Limitations

- One device per account — linking multiple devices is not yet supported
- No message history on new device login
- PIN-based key encryption is brute-forceable if the encrypted key is stolen — hardware key storage (Web Crypto + device binding) is the ideal next step

---

## License

MIT
