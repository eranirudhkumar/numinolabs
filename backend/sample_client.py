#!/usr/bin/env python3
"""
Sample client — demonstrates the full borrow/return lifecycle.

Usage:
    pip install httpx
    python sample_client.py

Assumes the backend is running at http://localhost:8000.
"""

import httpx

BASE = "http://localhost:8000/api/v1"


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=10) as client:
        print("=" * 50)
        print("1. Create a book")
        book = client.post(
            "/books",
            json={
                "title": "The Pragmatic Programmer",
                "author": "David Thomas",
                "isbn": "978-0-13-595705-9",
                "genre": "Technology",
                "published_year": 2019,
                "total_copies": 2,
            },
        )
        book.raise_for_status()
        book_data = book.json()
        print(f"   Created: {book_data['title']} (id={book_data['id']})")

        print("\n2. Register a member")
        member = client.post(
            "/members",
            json={
                "first_name": "Alice",
                "last_name": "Smith",
                "email": "alice@example.com",
                "phone": "+1-555-0100",
            },
        )
        member.raise_for_status()
        member_data = member.json()
        print(f"   Registered: {member_data['first_name']} {member_data['last_name']} (id={member_data['id']})")

        print("\n3. Borrow the book")
        loan = client.post(
            "/loans/borrow",
            json={"book_id": book_data["id"], "member_id": member_data["id"]},
        )
        loan.raise_for_status()
        loan_data = loan.json()
        print(f"   Loan id={loan_data['id']}")
        print(f"   Due: {loan_data['due_date']}")

        print("\n4. List Alice's active loans")
        active = client.get(
            f"/loans/member/{member_data['id']}",
            params={"active_only": True},
        )
        active.raise_for_status()
        print(f"   Active loans: {active.json()['total']}")

        print("\n5. Return the book")
        returned = client.post(f"/loans/{loan_data['id']}/return")
        returned.raise_for_status()
        returned_data = returned.json()
        print(f"   Status: {returned_data['status']}")
        print(f"   Fine:   ${returned_data['fine_amount']:.2f}")

        print("\n6. Verify book availability restored")
        refreshed = client.get(f"/books/{book_data['id']}")
        refreshed.raise_for_status()
        print(f"   Available copies: {refreshed.json()['available_copies']}")

        print("\nAll checks passed!")


if __name__ == "__main__":
    main()
