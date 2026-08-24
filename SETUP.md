# GitHub profile maintenance

This repository is the profile README for **m-zia-rasa**.

## Automatic contribution graph

`.github/workflows/update-profile.yml` fetches the public GitHub contribution calendar and rebuilds `assets/contrib-heatmap.svg` every day. It also runs automatically when the profile renderer, configuration, or workflow changes. No personal access token or paid image service is required.

If the refresh job can fetch/render but cannot push its result, open **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**.

## Customize the terminal panels

- Edit `profile.json`.
- Run `python scripts/render_profile.py` to rebuild the terminal header and info card.
- Replace `assets/source-avatar.webp`, install `requirements-local.txt`, then run `python scripts/render_ascii.py` to rebuild the ASCII portrait.
- For a manual contribution refresh, install `scripts/requirements.txt`, run `python scripts/fetch_contributions.py`, then `python scripts/render_contributions.py`.
