# PATHFINDER

**Policy-Aware Transaction Harness for Runtime Governance**

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688)
![SQLite](https://img.shields.io/badge/SQLite-003B57)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📌 Overview

PATHFINDER is a runtime governance middleware designed to enforce policies, generate auditable receipts, and detect tampering for intelligent decision engines such as AI agents, autonomous systems, and algorithmic traders.

It intercepts every decision request, evaluates it against a set of rules defined in YAML, and either allows or denies execution.

Allowed decisions are cryptographically signed with RSA, providing verifiable proof of policy compliance.

This repository contains a fully functional **Reference Evaluation Kit (REK)** that demonstrates:

- Real-time policy enforcement
- Signed receipt generation and verification
- Tamper detection
- Decision replay
- Audit logging
- Dynamic policy reload without server restart

---

## ✨ Features

- ✅ **Policy Engine** – Evaluate decisions against YAML-defined rules with support for `and`/`or`, comparisons, time-of-day conditions, and user roles.
- ✅ **RSA Signatures** – Each allowed decision gets a signed receipt using RSA cryptography.
- ✅ **Tamper Detection** – Detect modifications to stored data by comparing it with the signed payload.
- ✅ **Replay** – Re-evaluate historical decisions using the current policy set.
- ✅ **Audit Trail** – Every governance action is logged with timestamps.
- ✅ **Persistent Storage** – All data is stored in SQLite and can be migrated to PostgreSQL.
- ✅ **Hot Policy Reload** – Update `policies.yaml` and reload policies without restarting the server.
- ✅ **REST API** – Built with FastAPI, with interactive Swagger UI available at `/docs`.

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Backend | Python 3.8+ with FastAPI |
| ORM / Database | SQLAlchemy + SQLite |
| Cryptography | `cryptography` — RSA-2048 with PSS padding |
| Policy Definition | YAML via PyYAML |
| Web Server | Uvicorn (ASGI) |
| Frontend | Next.js 14, React 18, Tailwind CSS |
| Visualization | React Flow |

---

## 📁 Project Structure

```text
PathFinder/
├── pathfinder_backend/              # FastAPI backend
│   ├── main.py                      # FastAPI app and endpoints
│   ├── models.py                    # Pydantic schemas
│   ├── policy.py                    # PolicyEngine wrapper
│   ├── policy_loader.py             # YAML parsing and rule evaluation
│   ├── crypto.py                    # RSA key management, signing and verification
│   ├── memory.py                    # DatabaseMemory CRUD operations
│   ├── database.py                  # SQLAlchemy models and session
│   ├── logging_config.py            # Logging setup
│   ├── config.py                    # Paths and constants
│   ├── insurance_client.py          # Dataset integration script
│   ├── policies.yaml                # Policy rules
│   ├── requirements.txt             # Python dependencies
│   ├── private_key.pem              # RSA private key (generated)
│   ├── public_key.pem               # RSA public key (generated)
│   └── pathfinder.db                # SQLite database (created at runtime)
│
├── pathfinder_frontend/             # Next.js frontend
│   ├── app/
│   │   ├── page.tsx                 # Dashboard
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── HitlApproval.tsx         # HITL decision gate
│   │   ├── AuditReplay.tsx          # Audit trail and replay
│   │   ├── FlowGraph.tsx            # React Flow topology
│   │   └── AgentStream.tsx          # Autonomous agent simulator
│   │
│   ├── lib/
│   │   └── api.ts                   # API helpers
│   ├── package.json
│   └── next.config.ts               # API proxy rewrite
│
├── .gitignore
├── LICENSE
└── README.md


## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- `pip` and `npm`

### 1. Clone the repository

```bash
git clone https://github.com/a1k7/PathFinder.git
cd PathFinder
2. Start the Backend

bash
cd pathfinder_backend
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
The API will be available at http://localhost:8000.
Interactive docs: http://localhost:8000/docs

Note: On first run, an RSA key pair is auto-generated and saved as private_key.pem and public_key.pem. Do not commit these to version control.
3. Start the Frontend

In a new terminal:

bash
cd pathfinder_frontend
npm install
npm run dev
Open http://localhost:3000 to access the PATHFINDER Governance Console.

##🔧 Configuration

Policy rules – Edit pathfinder_backend/policies.yaml to define your own conditions.
Database – By default, SQLite is used (pathfinder.db). To switch to PostgreSQL, set the environment variable DATABASE_URL (e.g., postgresql://user:pass@localhost/db).
Logging – Configured in logging_config.py.
API Proxy – The frontend routes /api/proxy/* → http://127.0.0.1:8000/* via next.config.ts.
📚 API Endpoints

##Method	Endpoint	Description

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
    "receipt": { ... }
  }'
##📝 Policy Language

Policies are defined in YAML under the policies key. Each policy has a name, version, enabled flag, and a list of rules. Each rule contains a condition and an effect (allow or deny).

Supported operators:

eq, ne, gt, lt, gte, lte
in, not_in
between (numeric ranges)
time_of_day (e.g., ["09:00", "17:00"])
and, or (nesting)
Example

yaml
policies:
  - name: "insurance_governance"
    version: "2.0.0"
    enabled: true
    rules:
      - condition:
          user: "blocked_user"
        effect: deny

      - condition:
          and:
            - action: "update"
            - amount:
                gt: 10000
        effect: deny

      - condition:
          action:
            in: ["create", "view", "update"]
        effect: allow

      - condition: {}
        effect: deny
🧪 Demo: Using the Insurance Dataset

The repository includes a script to feed the BDR-AI/insurance_decision_boundaries_v1 dataset through the governance pipeline:

bash
cd pathfinder_backend
pip install datasets
python insurance_client.py
Each insurance case is mapped to a governance decision and evaluated against the policies.

##🔒 Security Considerations

Private key – Stored on the file system. In production, use a secrets manager (HashiCorp Vault, AWS Secrets Manager).
Database – SQLite is fine for demos; for production, use a secure PostgreSQL instance with TLS.
Key rotation – Rotating the RSA key invalidates all existing receipts. Plan accordingly.
Access control – The API currently has no authentication; add OAuth2 / JWT as needed.
🤝 Contributing

Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.
📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

##🙏 Acknowledgements

FastAPI – web framework
cryptography – secure cryptographic operations
SQLAlchemy – ORM
Next.js – React framework
React Flow – graph visualization
📞 Contact

For questions or support, please open an issue on GitHub or reach out to warikakhilesh319@gmail.com.
