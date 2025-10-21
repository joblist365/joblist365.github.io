
Jobpatra — Static site (GitHub Pages-ready)
===========================================

Files included:
- index.html  : Single-page app (vanilla JS) that loads a small placeholder dataset
- styles.css  : Clean white theme CSS
- data.json   : Placeholder JSON dataset (replace with full dataset when ready)
- README.md   : This file

How to publish to GitHub Pages (quick):
1. Create a GitHub account (if you don't have one): https://github.com/join
2. Create a new repository named: jobpatra.github.io
3. Upload these files into the repository root.
4. GitHub Pages will automatically publish at: https://<your-github-username>.github.io/jobpatra.github.io
   (If you name the repo exactly jobpatra.github.io and your username is 'jobpatra', the site will be at https://jobpatra.github.io)

Replacing dataset:
- Replace data.json with your full dataset and update the DATA constant in index.html if needed.
- The app reads the DATA constant embedded in index.html for quick demo. For larger datasets, load data.json asynchronously.

Notes:
- This is a starting professional template. Once you're happy, I can expand it to include:
  - Full India dataset embedded or loaded dynamically
  - SEO meta tags, sitemap, and PWA support
  - Downloadable APK or React Native version for Expo
