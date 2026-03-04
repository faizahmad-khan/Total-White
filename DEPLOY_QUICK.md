# Itch.io Deployment Checklist

## Prerequisites
- [ ] itch.io account created (https://itch.io)
- [ ] Game tested locally (`python main.py` works)
- [ ] README.md and screenshots ready

## Quick Start (5 min)

### 1. Rebuild Web Version
```bash
# macOS/Linux
./build_web.sh

# Windows
build_web.bat

# OR manually:
pip install pygbag
python -m pygbag main.py --build
```

### 2. Create itch.io Project
1. Go to https://itch.io/dashboard
2. Click "Create new project"
3. Fill in:
   - **Title**: Camouflage: Advanced Stealth Game
   - **URL**: camouflage-stealth (or your choice)
   - **Kind**: Game → Browser
   - Click "Save & continue"

### 3. Upload Game
1. In project editor, go to **Uploads** section
2. Click **Upload files**
3. Drag & drop the `build/web/` **folder**
4. Check: "This file will be played in a browser"
5. **Important**: Set viewport to **800 × 600**
6. Click **Upload files**

### 4. Add Game Details
- **Cover image**: Use a screenshot from `images/`
- **Description**: Copy from README.md
- **Tags**: puzzle, stealth, python, pygame
- **Release status**: Public
- Click **Save**

## Your Game URL
Once published: `https://[your-username].itch.io/camouflage-stealth`

Update the README badge with your actual URL:
```markdown
[![Play on itch.io](https://img.shields.io/badge/Play_on-itch.io-fa5c5c?style=for-the-badge&logo=itch.io&logoColor=white)](https://your-username.itch.io/camouflage-stealth)
```

## Testing
- [ ] Game loads in browser
- [ ] Arrow keys work
- [ ] Game is playable (no console errors)
- [ ] All 5 levels accessible
- [ ] Scoring system works

## After Publishing
- [ ] Share on Twitter/Reddit
- [ ] Add to your portfolio/GitHub
- [ ] Invite friends to play
- [ ] Collect feedback
- [ ] Plan future updates

---

## Detailed Instructions
See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step guide with troubleshooting.
