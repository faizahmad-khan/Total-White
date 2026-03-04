# Deploying Camouflage to itch.io

Follow these steps to deploy your game to itch.io:

## Step 1: Create an itch.io Account (if you don't have one)
1. Go to https://itch.io
2. Sign up for an account
3. Verify your email

## Step 2: Create a New Game Project

1. Log in to itch.io
2. Click your profile icon → **Dashboard**
3. Click **Create new project**
4. Fill in the form:
   - **Project title**: Camouflage: Advanced Stealth Game
   - **Project URL**: `camouflage-stealth` (or your preferred slug)
   - **Kind of project**: Game
   - **Classify content**: Choose appropriate tags
   - **Description**: Copy from README.md (or customize)
   - Click **Save & continue**

## Step 3: Rebuild the Web Build (Optional but Recommended)

If you want to ensure the web build is fresh and uses your latest code:

### Install Pygbag

```bash
pip install pygbag
```

### Build for Web

```bash
cd /Users/faizahmadkhan/Desktop/Total-White
pygbag main.py --build
```

This creates a new `build/` folder with the optimized web version.

## Step 4: Upload to itch.io

You have two options:

### Option A: Web Upload (Easiest - Recommended)

1. In your itch.io project's edit page:
   - Scroll to **Uploads** section
   - Click **Upload file**
   - Select the **HTML file** setup:
     - Choose `build/web/index.html` folder (select the entire `web/` folder)
     - Check **This file will be played in a browser**
     - Check **Make file downloadable?** (optional)
     - Set **Viewport / Window size** to: `800 x 600`
   - Click **Upload**

2. itch.io will automatically host it as a web game

### Option B: Manual Build & Upload (Advanced)

If you prefer, zip the `build/web/` folder and upload:

```bash
cd /Users/faizahmadkhan/Desktop/Total-White/build
zip -r web.zip web/
```

Then upload `web.zip` to itch.io's upload section.

## Step 5: Configure Project Settings

On your itch.io project edit page:

1. **Cover image**: 
   - Use one of your game screenshots from `images/`
   - Recommended: 315×250px minimum for thumbnail

2. **Display options**:
   - Set game window to: **800 × 600**
   - Enable "**Fullscreen**" if desired
   - Check "**Embed in page**"

3. **Tags**:
   - Add: `puzzle`, `stealth`, `python`, `pygame`

4. **Release status**:
   - Set to **Released** or **Early Alpha** as preferred
   - Check "**This project is free**"

5. **Visibility**:
   - Set to **Public**
   - Optionally: Check "**Featured**" for homepage visibility

## Step 6: Launch!

1. Click **Save** on the itch.io project page
2. Test your game by clicking the play button
3. Share your game URL with friends!

Your game will be available at: `https://your-username.itch.io/camouflage-stealth`

---

## Alternative: Using itch CLI (Advanced)

If you want to automate uploads:

### Install itch CLI

```bash
# macOS with Homebrew
brew install butler

# Or download from: https://itch.io/docs/butler/
```

### Push to itch.io

```bash
cd /Users/faizahmadkhan/Desktop/Total-White/build/web

butler login  # First time only - follow prompt

butler push . your-username/camouflage-stealth:html5
```

Replace `your-username` with your actual itch.io username.

---

## Troubleshooting

### Game doesn't load in browser
- Ensure `build/web/index.html` exists
- Check browser console (F12) for errors
- Try Force Reload (Ctrl+Shift+R or Cmd+Shift+R)

### Game runs but is slow
- This is normal for Python in the browser
- Pygbag's WASM runtime has overhead
- Reduce graphics if needed

### Web build doesn't have latest code
- Rebuild using `pygbag main.py --build`
- Clear itch.io browser cache

---

## Next Steps

Once deployed:
- Share on Social Media with the itch.io link
- Add gameplay GIFs/videos to your itch.io page
- Collect feedback from players
- Update your game with improvements
- Consider writing a devlog

Good luck! 🎮
