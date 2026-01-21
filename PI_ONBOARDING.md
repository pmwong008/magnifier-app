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

## 4. Device Roles and Workflow

### devPi (ArgonOne Pi4B)
- **Purpose:** Development and coding in VSCode.
- **GPIO Controls:** Not used (pins are fiddly on ArgonOne case).
- **Magnifier Startup:** Disabled — does not auto‑start on boot.
- **Execution:** Run manually inside `.venv` when testing (`source .venv/bin/activate` → `python magnifier.py`).
- **GitHub Role:** Push/pull code changes; bridge to testPi and Pi5.

### testPi
- **Purpose:** Appliance‑like testing with GPIO controls.
- **GPIO Controls:** Enabled and wired in.
- **Magnifier Startup:** Enabled via `systemctl` — auto‑starts on boot.
- **Execution:** Runs headless after boot, no manual activation needed.
- **GitHub Role:** Pull latest code from devPi; validate real‑world operation.

### Pi5 (new)
- **Purpose:** Next‑generation workflow bridge.
- **GPIO Controls:** None (same as devPi).
- **Magnifier Startup:** Disabled — does not auto‑start on boot.
- **Execution:** Manual run inside `.venv` for development/testing.
- **GitHub Role:** Sync with devPi and testPi; future onboarding target.

---

### Workflow Summary
1. **Develop on devPi** (manual run in `.venv`).
2. **Push to GitHub**.
3. **Pull on testPi** (auto‑start via `systemctl` with GPIO).
4. **Validate appliance behavior**.
5. **Onboard Pi5** following same split: devPi (manual) vs. testPi (auto).

---

### Notes
- `systemctl is-enabled magnifier.service` → check if auto‑start is enabled.
- `systemctl start|stop|restart magnifier.service` → manually control service.
- `.venv` must be activated on devPi/Pi5 when running manually.
- GitHub remains the single source of truth for bridging all devices.

## NordVPN Control (devPi)


- Use terminal login for reliability:

`nordvpn login`
`nordvpn connect`
`nordvpn disconnect`
`nordvpn status`

- Allow devPi to reach testPi even while the VPN is active:

`nordvpn set lan-discovery enable`

- Enable auto connect:

`nordvpn set autoconnect on`

- List all settings:

`nordvpn settings`