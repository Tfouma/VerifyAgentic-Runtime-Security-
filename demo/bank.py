"""In-memory mock core-banking system for the demo.

Every customer, account and balance here is fictional. Nothing in this module
talks to a network or a real system.
"""

from __future__ import annotations

import copy
import threading

SEED_CUSTOMERS = [
    {"id": "C-1001", "name": "Maria Santos", "tier": "Retail", "email": "maria.s@example.com", "ssn_last4": "4821"},
    {"id": "C-1002", "name": "James Okafor", "tier": "Private", "email": "j.okafor@example.com", "ssn_last4": "1937"},
    {"id": "C-1003", "name": "Lena Fischer", "tier": "Private", "email": "lena.f@example.com", "ssn_last4": "6610"},
    {"id": "C-1004", "name": "Hiro Tanaka", "tier": "Business", "email": "hiro.t@example.com", "ssn_last4": "2295"},
    {"id": "C-1005", "name": "Amara Diallo", "tier": "Retail", "email": "amara.d@example.com", "ssn_last4": "7054"},
]

SEED_ACCOUNTS = {
    "ACC-1001": {"owner": "C-1001", "balance": 8_420.00},
    "ACC-1002": {"owner": "C-1002", "balance": 412_300.00},
    "ACC-1003": {"owner": "C-1003", "balance": 268_950.00},
    "ACC-1004": {"owner": "C-1004", "balance": 1_140_000.00},
    "ACC-1005": {"owner": "C-1005", "balance": 15_780.00},
    # Account that received no customer instruction: the destination in the story.
    "ACC-7777": {"owner": "C-UNKNOWN", "balance": 0.00},
}


class Bank:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.customers = {c["id"]: dict(c) for c in SEED_CUSTOMERS}
            self.accounts = copy.deepcopy(SEED_ACCOUNTS)
            self.transfers: list[dict] = []
            self.records_read: set[str] = set()

    # --- tool surface exposed to agents ---------------------------------
    def get_account(self, account_id: str) -> dict:
        with self._lock:
            acc = self.accounts[account_id]
            self.records_read.add(acc["owner"])
            return {"account": account_id, **acc}

    def list_customers(self) -> list[dict]:
        with self._lock:
            self.records_read.update(self.customers)
            return list(self.customers.values())

    def transfer(self, src: str, dst: str, amount: float) -> dict:
        with self._lock:
            amount = min(amount, self.accounts[src]["balance"])
            self.accounts[src]["balance"] -= amount
            self.accounts[dst]["balance"] += amount
            tx = {"from": src, "to": dst, "amount": round(amount, 2)}
            self.transfers.append(tx)
            return tx

    # --- dashboard view ---------------------------------------------------
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "accounts": [
                    {
                        "id": aid,
                        "owner": a["owner"],
                        "name": self.customers.get(a["owner"], {}).get("name", "Unknown recipient"),
                        "balance": round(a["balance"], 2),
                        "seed": SEED_ACCOUNTS[aid]["balance"],
                    }
                    for aid, a in self.accounts.items()
                ],
                "transfers": list(self.transfers),
                "moved": round(sum(t["amount"] for t in self.transfers), 2),
                "records_exposed": len(self.records_read),
            }
