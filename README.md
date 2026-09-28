<<<<<<< HEAD
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
=======
# PATHFINDER

Policy‑Aware Transaction Harness for Runtime Governance

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688)
![SQLite](https://img.shields.io/badge/SQLite-003B57)
![License](https://img.shields.io/badge/license-MIT-green)

## 📌 Overview

PATHFINDER is a runtime governance middleware designed to enforce policies, generate auditable receipts, and detect tampering for intelligent decision engines (AI agents, autonomous systems, algorithmic traders). It intercepts every decision request, evaluates it against a set of rules (defined in YAML), and either allows or denies execution. Allowed decisions are cryptographically signed with RSA, providing verifiable proof of policy compliance.

This repository contains a fully functional Reference Evaluation Kit (REK) that demonstrates:

Real‑time policy enforcement
Signed receipt generation & verification
Tamper detection
Decision replay (re‑evaluate past decisions with updated policies)
Audit logging
Dynamic policy reload (no server restart)
✨ Features

✅ Policy Engine – Evaluate decisions against rules written in YAML (supports and/or, comparisons, time‑of‑day, user roles).
✅ RSA Signatures – Each allowed decision gets a signed receipt (private key signing, public key verification).
✅ Tamper Detection – Detect modifications to stored data by comparing with the signed payload.
✅ Replay – Re‑evaluate historical decisions with the current policy set.
✅ Audit Trail – Every governance action is logged with timestamps.
✅ Persistent Storage – All data stored in SQLite (easily switch to PostgreSQL).
✅ Hot Policy Reload – Update policies.yaml and reload without restarting.
✅ REST API – Built with FastAPI, interactive Swagger UI at /docs.
🛠 Tech Stack

## Component	Technology
Backend	Python 3.8+ with FastAPI
ORM / Database	SQLAlchemy + SQLite (dev)
Cryptography	cryptography (RSA‑2048, PSS padding)
Policy Definition	YAML (via PyYAML)
Web Server	Uvicorn (ASGI)
📁 Project Structure


pathfinder_backend/
├── main.py               # FastAPI app, endpoints
├── models.py             # Pydantic schemas
├── policy.py             # PolicyEngine wrapper
├── policy_loader.py      # YAML parsing & rule evaluation
├── crypto.py             # RSA key management, sign/verify
├── memory.py             # DatabaseMemory (CRUD operations)
├── database.py           # SQLAlchemy models & session
├── logging_config.py     # Logging setup
├── config.py             # Paths and constants
├── policies.yaml         # Example policy rules
├── requirements.txt      # Python dependencies
├── private_key.pem       # RSA private key (generated)
├── public_key.pem        # RSA public key  (generated)
└── pathfinder.db         # SQLite database (created at runtime)
🚀 Getting Started

Prerequisites

Python 3.8 or higher
pip (Python package manager)
Installation

## Clone the repository

bash
git clone https://github.com/yourusername/pathfinder.git
cd pathfinder/pathfinder_backend
Create and activate a virtual environment (optional but recommended)

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Run the server

bash
uvicorn main:app --reload

The API will be available at http://localhost:8000.
Interactive documentation: http://localhost:8000/docs

Note: On first run, a new RSA key pair is automatically generated and saved as private_key.pem and public_key.pem. Do not commit these to version control.
🔧 Configuration

Policy rules – Edit policies.yaml to define your own conditions. See Policy Language below.
Database – By default, SQLite is used (pathfinder.db). To switch to PostgreSQL, set the environment variable DATABASE_URL (e.g., postgresql://user:pass@localhost/db).
Logging – Configured in logging_config.py.
📚 API Endpoints

All endpoints return JSON.

## Method	Endpoint	Description

POST	/decide	Submit a decision; returns allow/deny + receipt
GET	/receipt/{receipt_id}	Retrieve a specific receipt
POST	/verify	Verify a receipt against stored data
POST	/replay	Re‑evaluate a past decision with current policy
POST	/tamper	Simulate tampering (for demo)
GET	/audit	Retrieve the full audit log
GET	/decisions	List all decision IDs
POST	/policy/reload	Reload policies from policies.yaml
GET	/health	Health check

Example: Submit a decision

bash
curl -X POST http://localhost:8000/decide \
  -H "Content-Type: application/json" \
  -d '{"decision_data": {"action": "create", "amount": 100, "user": "alice"}}'
Example: Verify a receipt

bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "<decision_id>",
    "receipt": { ... }   # copy from /decide response
  }'
📝 Policy Language

Policies are defined in YAML under the policies key. Each policy has a name, version, enabled flag, and a list of rules. Each rule contains a condition and an effect (allow or deny).

Supported operators:

eq, ne, gt, lt, gte, lte
in, not_in
between (numeric ranges)
time_of_day (e.g., ["09:00", "17:00"])
and, or (nesting)
Example:

yaml
policies:
  - name: "standard_operations"
    version: "1.0.0"
    enabled: true
    rules:
      - condition:
          action: "create"
        effect: allow

      - condition:
          and:
            - action: "update"
            - amount:
                gt: 1000
        effect: deny

      - condition:
          user: "blocked_user"
        effect: deny

      - condition:
          and:
            - user:
                in: ["alice", "bob"]
            - amount:
                lte: 500
            - time_of_day:
                between: ["09:00", "17:00"]
        effect: allow
        
## 🔒 Security Considerations

Private key – Stored in the file system. In production, use a secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager).
Database – SQLite is fine for demos; for production, use a secure PostgreSQL instance with TLS.
Key rotation – Rotating the RSA key will invalidate all existing receipts. Plan accordingly.
Access control – The API currently has no authentication; add OAuth2 / JWT as needed.
🤝 Contributing

## Contributions are welcome! Please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.
📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgements

FastAPI – for the excellent web framework.
cryptography – for secure cryptographic operations.
SQLAlchemy – for the robust ORM.

## 📞 Contact

For questions or support, please open an issue on GitHub or reach out to warikakhilesh319@gmail.com


>>>>>>> 9d214d349f8311fb495d4ced59e7f10032b07685
