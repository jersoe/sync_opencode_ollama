#!/usr/bin/env python3
"""
Sync the "ollama" provider block in opencode.json with the models
you actually have pulled in Ollama.

What it does:
  1. Asks your local Ollama server (GET /api/tags) which models are installed.
  2. Loads your existing opencode.json (creating one if it doesn't exist).
  3. Updates just the "provider.ollama.models" map to match — adding new
     models, and (optionally, with --prune) removing ones you've deleted.
  4. Leaves every other provider and setting in the file untouched.

Usage:
    python3 sync_opencode_ollama.py
    python3 sync_opencode_ollama.py --config ~/.config/opencode/opencode.json
    python3 sync_opencode_ollama.py --ollama-host http://192.168.1.50:11434
    python3 sync_opencode_ollama.py --prune          # remove models no longer in Ollama
    python3 sync_opencode_ollama.py --dry-run        # show what would change, don't write
"""

import argparse
import json
import os
import sys
import requests

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/opencode/opencode.json")
DEFAULT_OLLAMA_HOST = "http://localhost:11434"


def get_installed_models(ollama_host):
    """Return list of model names installed in Ollama, e.g. ['qwen3-coder:30b', 'gemma4:e4b']."""
    url = f"{ollama_host.rstrip('/')}/api/tags"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Could not reach Ollama at {url}: {e}")
        print("Is Ollama running? Try: ollama serve")
        sys.exit(1)

    data = resp.json()
    return sorted(m["name"] for m in data.get("models", []))


def load_config(path):
    if not os.path.exists(path):
        print(f'No config found at "{path}" — starting a new one.')
        return {"$schema": "https://opencode.ai/config.json"}

    with open(path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: {path} is not valid JSON ({e}). Fix or remove it and re-run.")
            sys.exit(1)


def merge_ollama_provider(config, model_names, ollama_host, prune):
    provider = config.setdefault("provider", {})
    ollama = provider.setdefault(
        "ollama",
        {
            "npm": "@ai-sdk/openai-compatible",
            "name": "Ollama (local)",
            "options": {"baseURL": f"{ollama_host.rstrip('/')}/v1"},
            "models": {},
        },
    )
    # Make sure required fields exist even if the block was already there
    ollama.setdefault("npm", "@ai-sdk/openai-compatible")
    ollama.setdefault("name", "Ollama (local)")
    ollama.setdefault("options", {})
    ollama["options"].setdefault("baseURL", f"{ollama_host.rstrip('/')}/v1")

    existing_models = ollama.setdefault("models", {})

    added, removed = [], []

    for name in model_names:
        if name not in existing_models:
            existing_models[name] = {}
            added.append(name)

    if prune:
        for name in list(existing_models.keys()):
            if name not in model_names:
                del existing_models[name]
                removed.append(name)

    return added, removed


def main():
    parser = argparse.ArgumentParser(description="Sync opencode.json's ollama provider with installed Ollama models.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help=f"Path to opencode.json (default: {DEFAULT_CONFIG_PATH})")
    parser.add_argument("--ollama-host", default=DEFAULT_OLLAMA_HOST, help=f"Ollama server URL (default: {DEFAULT_OLLAMA_HOST})")
    parser.add_argument("--prune", action="store_true", help="Remove models from config that are no longer installed in Ollama")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing the file")
    args = parser.parse_args()

    models = get_installed_models(args.ollama_host)
    if not models:
        print(f"No models found on {args.ollama_host}. Pull one first, e.g.: ollama pull qwen2.5-coder:7b")
        return

    print(f"Found {len(models)} model(s) in Ollama: {', '.join(models)}")

    config = load_config(args.config)
    added, removed = merge_ollama_provider(config, models, args.ollama_host, args.prune)

    if not added and not removed:
        print("opencode.json already matches your installed Ollama models. Nothing to do.")
        return

    if added:
        print(f"Would add:   {', '.join(added)}" if args.dry_run else f"Added:   {', '.join(added)}")
    if removed:
        print(f"Would remove: {', '.join(removed)}" if args.dry_run else f"Removed: {', '.join(removed)}")

    if args.dry_run:
        print("\nDry run — no changes written.")
        return

    os.makedirs(os.path.dirname(args.config), exist_ok=True)
    with open(args.config, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print(f"\nUpdated {args.config}")
    print("Restart OpenCode (or reopen /models) to pick up the changes.")


if __name__ == "__main__":
    main()
