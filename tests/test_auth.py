"""Tests for auth endpoints and JWT utilities."""
import pytest
from datetime import timedelta

from app.utils.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)


# ── Password hashing ──────────────────────────────────────────────────────────

def test_hash_and_verify():
    pw     = "supersecret123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)


def test_wrong_password_fails():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def test_create_and_decode_access_token():
    token   = create_access_token({"sub": "42"})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    token   = create_refresh_token({"sub": "42"})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_expired_token_raises():
    from fastapi import HTTPException
    token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc:
        decode_token(token)
    assert exc.value.status_code == 401


# ── Auth API endpoints ────────────────────────────────────────────────────────

def test_register_user(client):
    r = client.post("/api/v1/auth/register", json={
        "email": "alice@example.com",
        "password": "securepass1",
        "full_name": "Alice",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "alice@example.com"
    assert data["full_name"] == "Alice"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {"email": "bob@example.com", "password": "securepass1"}
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 400
    assert "already exists" in r.json()["detail"]


def test_register_short_password(client):
    r = client.post("/api/v1/auth/register", json={
        "email": "short@example.com",
        "password": "123",
    })
    assert r.status_code == 422


def test_login_success(client):
    client.post("/api/v1/auth/register", json={
        "email": "carol@example.com",
        "password": "securepass1",
    })
    r = client.post("/api/v1/auth/login", json={
        "email": "carol@example.com",
        "password": "securepass1",
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token"  in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "dave@example.com",
        "password": "securepass1",
    })
    r = client.post("/api/v1/auth/login", json={
        "email": "dave@example.com",
        "password": "wrongpassword",
    })
    assert r.status_code == 401


def test_login_unknown_email(client):
    r = client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "securepass1",
    })
    assert r.status_code == 401


def test_me_endpoint(client):
    client.post("/api/v1/auth/register", json={
        "email": "eve@example.com",
        "password": "securepass1",
    })
    login = client.post("/api/v1/auth/login", json={
        "email": "eve@example.com",
        "password": "securepass1",
    })
    token = login.json()["access_token"]
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "eve@example.com"


def test_me_without_token(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_refresh_token(client):
    client.post("/api/v1/auth/register", json={
        "email": "frank@example.com",
        "password": "securepass1",
    })
    login = client.post("/api/v1/auth/login", json={
        "email": "frank@example.com",
        "password": "securepass1",
    })
    refresh_token = login.json()["refresh_token"]
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_my_organizations(client):
    client.post("/api/v1/auth/register", json={
        "email": "grace@example.com",
        "password": "securepass1",
    })
    login = client.post("/api/v1/auth/login", json={
        "email": "grace@example.com",
        "password": "securepass1",
    })
    token = login.json()["access_token"]

    # Create an org and join it
    org = client.post("/api/v1/organizations/", json={"name": "Grace Org"})
    org_id = org.json()["id"]
    client.post(
        f"/api/v1/auth/me/organizations/{org_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get(
        "/api/v1/auth/me/organizations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    orgs = r.json()
    assert any(o["id"] == org_id for o in orgs)
