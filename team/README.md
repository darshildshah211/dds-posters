# DDS Capital Wealth, Instagram content team (@dds_capital)

Goal: content a family stops to watch: interactive, varied, professional, and always compliant.
Posting is done by the GitHub publisher (scripts/ig_publish.py) from instagram/queue/. The team only adds media + queue files.

## Weekly calendar (IST) - 3 publishing days
| Day | Format | Content | Publish |
|---|---|---|---|
| Tuesday | REEL 25-40 s, voiceover | NEWS EXPLAINER: the week's most discussed market/economy/regulatory topic, facts only, explained for a family | 19:00 |
| Thursday | REEL 25-40 s, voiceover | FAMILY STORY (Papa / Beta / Dada dialogue) or CONCEPT EXPLAINER (SIP, NAV, rebalancing, emergency fund...) alternating weekly | 19:00 |
| Sunday | STORY SET, 4 frames | 10:00 myth-vs-fact, 13:00 poll (A/B), 17:00 question of the week, 20:00 weekly plan-check quote | as listed |
Reels carry a caption (hook, 3 short lines, one question, hashtags, disclaimer). Reel cover/first line must be a hook, not a brand line.

## Pipeline (every publishing day) - see roles.md
1. Content Director (social media manager) picks the slot from calendar.md and team/log.csv (no repeated topic/hook within 8 weeks).
2. News Desk / Researcher gathers material. Tuesday: 3-5 candidate topics from the last 7 days, each with >=2 official/reliable sources.
3. Scriptwriter / Family Storyteller writes the script (reel) or frame copy (stories).
4. Compliance Officer + Fact-checker reviews against compliance.md. FAIL -> rewrite once; FAIL again -> evergreen fallback; still unsure -> skip and notify.
5. Creative Designer builds media: reels with reels_src/explainer_reel.py; stories with ig_gen.story_poll / story_myth / story_question / story_news / story_quote. Every PNG/frame is viewed for clipping.
6. Producer/Publisher converts (JPEG for stories, MP4 for reels), writes queue JSON, commits, pushes, verifies on origin/main.
7. Community Manager step: logs the question/poll in team/log.csv so the next Sunday can refer to replies; weekly summary is the only notification when something fails.

## Platform limits (be honest)
- The Instagram API cannot attach native poll/question/slider stickers to stories. Poll and question frames are reply-to-vote designs ("Reply A or B"). The owner can overlay a native sticker in the Instagram app in 10 seconds if wanted.
- Replies/DMs and comments are read and answered by a person, not by the automation.

## v2 (colour, Hinglish, pain-point led) - overrides the monochrome notes above
Pillars (rotate; every post names a pain point first, then a habit, never a product): 1 MONTH-END (salary gayab, EMI, festival spend) 2 FAMILY GOALS (school fees, wedding, parents' health costs) 3 MONEY MYTHS 4 NEWS IN PLAIN BHASHA 5 BEHIND THE DESK (who we are, how a review meeting works, no client names) 6 COMMUNITY (replies, questions, polls).
Division of labour: REELS = reach (strangers; hook, pain point, one idea, 25-40 s, Tue/Thu). CAROUSEL FEED POSTS = saves and credibility (6-8 slides: myth vs fact, checklist, "3 things", news explainer; use ig_gen feed templates + brand colours; add when the feed automation is revived). STORIES = relationship (Sunday set: myth, poll, question, a reply-to-reply frame, behind-the-desk). Reels use reels_src/reel_v2.py. Brand details in brand.md.
Research notes (Nov 2026): Meta/Ipsos study (Aug 2025) found 57% of urban 25-45 Indians use Instagram for financial decisions; Grant Thornton Bharat Oct 2026 survey: 83% would have under a year of savings if income stopped, 62% expect pay rises to lag inflation. Vendor blogs claim completion rate, shares (WhatsApp/DMs) and saves matter most, Hinglish is dominant, animated subtitles help: unverified. Treat as direction, not fact; do not quote these numbers in posts without verifying two sources.

## v3 (28 Nov 2026): VOICE-OVER REELS PAUSED - owner decision
No computer voices. Until a licensed/own voice is set up (see human-voice.md), the weekly plan is:
- TUESDAY 12:30: branded FEED POST (single image 1080x1350: myth-vs-fact, "3 things", or a plain-Hinglish news explainer with ig_gen.feed_* then ig_gen.brand()), caption with a question. 18:00: one reply-to-vote STORY frame linked to it.
- THURSDAY 19:00: SILENT CHAT REEL (reels_src/reel_chat.py with "silent": true; text bubbles, typing dots, count-up stat card, soft beat, no voice). Spec example: reels/team/sample-silent-spec.json.
- SUNDAY: interactive story set (myth, poll, question, desk/reply frame, plan-check).
Revive voiced reels only when the owner supplies a voice (human recording via "voice_file" or a licensed voice via a GitHub Actions workflow).
