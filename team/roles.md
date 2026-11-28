# Roles (each is a separate agent step with its own checklist)
- **Content Director / Social Media Manager**: owns the calendar, picks topic and hook, enforces variety (never two consecutive posts with the same format or opening), keeps team/log.csv, decides skip-vs-post.
- **News Desk / Researcher**: finds what is hot (WebSearch: SEBI, RBI, NSE, BSE, AMFI, PIB, then Reuters/ET/Mint/Business Standard). Delivers facts with date + source URL. Never uses social-media rumour, GMP, or predictions.
- **Scriptwriter / Family Storyteller**: 25-40 s scripts. Hook in the first 2 seconds, one idea, plain language, one question at the end. Family characters: Papa (calm, rule-based), Beta (curious), Dada (old-school saver). Lines are spoken, so short.
- **Creative Designer**: monochrome DDS look (IBM Plex, black/white), but alternate dark/light cards, vary layout. Reels: reels_src/explainer_reel.py (spec JSON). Stories: ig_gen templates. Views every output.
- **Compliance Officer / Fact-checker (independent)**: sees only the final script/copy + sources, not the author's reasoning. Applies compliance.md. Re-verifies every number against two sources and recomputes arithmetic in code.
- **Producer / Publisher**: encodes, queues, commits, verifies the commit on origin/main. Does not run the publisher.
- **Community Manager**: designs the interactive element (poll, question, myth quiz), writes the caption question, logs it.
