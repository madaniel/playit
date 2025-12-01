#!/usr/bin/env python3
"""
1Password Secret Fetcher for Playit Service

This script authenticates with 1Password using a service account token
and retrieves the playit secret key from the specified vault.
"""

import os
import subprocess
import sys
import json


def check_op_cli():
    """Check if 1Password CLI is installed."""
    try:
        result = subprocess.run(
            ["op", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ 1Password CLI version: {result.stdout.strip()}", file=sys.stderr)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Error: 1Password CLI (op) is not installed or not in PATH", file=sys.stderr)
        return False


def check_service_account_token():
    """Check if the service account token is available."""
    token = os.environ.get("OP_SERVICE_ACCOUNT_TOKEN")
    if not token:
        print("✗ Error: OP_SERVICE_ACCOUNT_TOKEN environment variable is not set", file=sys.stderr)
        return False
    print("✓ OP_SERVICE_ACCOUNT_TOKEN is set", file=sys.stderr)
    return True


def fetch_secret(secret_reference):
    """
    Fetch a secret from 1Password using the secret reference.
    
    Args:
        secret_reference: The 1Password secret reference (e.g., "op://vault/item/field")
    
    Returns:
        The secret value as a string, or None if retrieval fails
    """
    try:
        print(f"Fetching secret from: {secret_reference}", file=sys.stderr)
        result = subprocess.run(
            ["op", "read", secret_reference],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ.copy()
        )
        secret = result.stdout.strip()
        if secret:
            print("✓ Secret retrieved successfully", file=sys.stderr)
            return secret
        else:
            print("✗ Error: Retrieved secret is empty", file=sys.stderr)
            return None
    except subprocess.CalledProcessError as e:
        print(f"✗ Error fetching secret: {e.stderr.strip()}", file=sys.stderr)
        return None


def write_env_file(secret_key, output_file="/tmp/playit.env"):
    """
    Write the secret to an environment file.
    
    Args:
        secret_key: The secret value to write
        output_file: Path to the output file
    """
    try:
        with open(output_file, "w") as f:
            f.write(f"SECRET_KEY={secret_key}\n")
        print(f"✓ Environment file written to: {output_file}")
        return True
    except IOError as e:
        print(f"✗ Error writing environment file: {e}", file=sys.stderr)
        return False


def export_to_env(secret_key):
    """
    Export the secret to the current environment.
    This is useful when sourcing the script.
    """
    os.environ["SECRET_KEY"] = secret_key
    print("✓ SECRET_KEY exported to environment")


def main():
    """Main function to orchestrate secret retrieval."""
    print("=" * 60, file=sys.stderr)
    print("1Password Secret Fetcher for Playit", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Step 1: Check prerequisites
    if not check_op_cli():
        sys.exit(1)
    
    if not check_service_account_token():
        sys.exit(1)
    
    # Step 2: Fetch the secret
    secret_reference = os.environ.get(
        "PLAYIT_SECRET_REFERENCE",
        "op://API Dev/Playit/credential"
    )
    
    secret_key = fetch_secret(secret_reference)
    if not secret_key:
        sys.exit(1)
    
    # Step 3: Export to environment (for current process context if needed)
    os.environ["SECRET_KEY"] = secret_key
    print("✓ SECRET_KEY fetched successfully", file=sys.stderr)
    
    print("=" * 60, file=sys.stderr)
    print("✓ All operations completed successfully", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # CRITICAL: Print ONLY the secret to stdout so it can be captured
    print(secret_key)


if __name__ == "__main__":
    main()
