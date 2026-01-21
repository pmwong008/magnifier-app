# Raspberry Pi Onboarding Checklist

A repeatable playbook for adding a new Pi (e.g., Pi5 with Bookworm desktop) into your Dev/Test workflow.

---

## 1. Base System Setup
- Flash Raspberry Pi OS (Bookworm desktop or Lite) to SD card.
- Boot Pi and run initial configuration:
  - `sudo raspi-config` → enable SSH, set hostname, configure locale/timezone.
  - Update system: `sudo apt update && sudo apt upgrade -y`.

## 2. Git & SSH Configuration and Verification
- Install Git: `sudo apt install git`.
- Generate SSH key:
  ```bash
  ssh-keygen -t ed25519 -C "pi5@yourproject"
- List keys in your Pi: `ls ~/.ssh/`
- Inspect the public key to confirm its comment: `cat ~/.ssh/id_ed25519.pub`
- Login Github -> Settings -> SSH and GPG keys
- Make sure the public key from your Pi (`id_ed25519.pub`) is listed there. If not copy and paste into Github.
- Test SSH Connection: `ssh -T git@github.com`
- Check fingerprint(SHA256) of your local key. It should match the fingerprint GitHub shows: `ssh-keygen -lf ~/.ssh/id_ed25519.pub`

## 3. Repo Setup 
- Clone remote repo: `git clone git@github.com:pmwong008/magnifier-app.git`
- Verify remotes: `git remote -v`

