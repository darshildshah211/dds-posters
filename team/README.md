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
