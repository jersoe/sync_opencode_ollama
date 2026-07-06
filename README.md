# 📖 Opencode Ollama Sync Script (`sync_opencode_ollama.py`) Guide

This script synchronizes the list of models configured for the "Ollama" provider within your `opencode.json` file with the models actually installed on your local Ollama server instance. This ensures that your development environment is always pointing to the correct and current set of available models, preventing "Model not found" type errors in OpenCode.

## ⚙️ Setup & Prerequisites

Before running the script, ensure you have:

1.  **Python 3:** The script requires Python 3 to run.
2.  **Requests Library:** Install the necessary Python dependency: `pip install requests`
3.  **Running Ollama Instance:** Your local Ollama server must be running in the background (`ollama serve`).

## ✨ How It Works

The `sync_opencode_ollama.py` script performs three main functions:

1.  **Discovery:** It connects to the configured Ollama API endpoint (defaulting to `http://localhost:11434/api/tags`) and automatically pulls a list of every model currently available on your Ollama machine (e.g., `llava:latest`, `qwen2:7b`).
2.  **Loading:** It loads the existing configuration from `opencode.json` (or creates a default one if it doesn't exist).
3.  **Synchronization:** It updates the specific section for the Ollama provider (`provider.ollama.models`) to match the discovered list of models.

## 🚀 Usage Guide

**1. Basic Sync (Standard Use)**

This command connects to Ollama and syncs all current model names into `opencode.json`.

```bash
python3 sync_opencode_ollama.py
```

**2. Specifying a Config File**

If your configuration file is not in the default location (`~/.config/opencode/opencode.json`), use the `--config` flag:

```bash
python3 sync_opencode_ollama.py --config /path/to/your/project/opencode.json
```

**3. Specifying a Custom Ollama Host**

If your Ollama server is running on a different machine or port, use `--ollama-host`:

```bash
python3 sync_opencode_ollama.py --ollama-host http://192.168.1.50:11434
```

**🛡️ Maintenance Commands (Highly Recommended)**

* **Pruning:** If you delete a local model through the `ollama rm` command, it remains listed in `opencode.json`. Running the sync with `--prune` removes orphaned entries from your configuration:
    ```bash
    python3 sync_opencode_ollama.py --prune
    ```

* **Dry Run:** To see exactly what changes will be made without actually touching your configuration file:
    ```bash
    python3 sync_opencode_ollama.py --dry-run
    ```

***

## Shell Aliases Setup

To make model management faster, we recommend setting up the following shell aliases in your shell's startup file (`~/.zshrc`, `~/.bashrc`, etc.). These wrappers wrap standard Ollama commands to provide immediate feedback and consistency.

Add the following lines to your shell configuration file:

```bash
# Opencode Ollama Helpers
alias ollamapull='ollama pull && echo "✅ Models pulled successfully."'
alias ollamaremove='echo "🗑️ Ready to remove model? Please specify the model name (e.g., llava):"'
```

**How to Activate:**

After adding these aliases, reload your shell configuration: 
* For Zsh: `source ~/.zshrc`
* For Bash: `source ~/.bashrc`