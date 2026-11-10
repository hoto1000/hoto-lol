# Hotolosophy TikTok + hoto.lol blog: one plan

Last updated 2026-11-03. This file is a plan only. `build.py` does not read it, so it never shows up on the site.

## The idea in one line

Every TikTok asks one question in 45 seconds. Every hoto.lol post sits with that same question for longer. The video is the doorway, the post is the room.

Shared theme line: **getting through the day on purpose.**
Shared pillar line: *where you stand shapes what you see, and good questions help you see more.*

## How the two fit together

| | TikTok (@hotolosophy) | hoto.lol blog |
|---|---|---|
| Job | Hook someone with one idea, one example, one question | Give the full argument, sources, and the strongest objection |
| Length | 45 s (Video 1 also has a 5 to 6 min lecture cut) | 800 to 1,500 words, optional audio version |
| Ends with | The closing question, spoken | The same question as the post's "Sit with this" (`sit` in `FRAMING`) |
| Points to | hoto.lol/links/ (bio link, PR #83) | The video, as a plain outbound link (no TikTok embeds: the site loads nothing third party) |
| Label | "Student reflection, not therapy or advice." + 988 on hard topics + TikTok AI label when the voice is AI | Crisis strip (already on every page), "Opinion is labeled," "Claims get sources," dated corrections |

The rule that ties them: **a video's hook becomes the post's `question`, and the video's closing question becomes the post's `sit`.** Then a viewer who clicks through finds the exact question they were just asked.

## The 12 videos and their companion posts

Posting days follow the 2026-11-03 growth plan: Mon, Tue, Thu, Sat. That runs the series in 3 weeks instead of 4. Toy videos go to the separate hotofidgets account, so Thursday is free for the series.

Dates assume the series starts Monday 2026-11-09. Shift the whole table if Video 1 goes up sooner.

| # | Date | Pillar | Hook | Closing question | Companion post | Status |
|---|---|---|---|---|---|---|
| 1 | Mon 11-09 | Location | Where you stand changes what you see | What's one place you stand that changes how you see things? | [Social location: where you stand decides what you see](https://hoto.lol/blog/social-location-where-you-stand/), then [Where power and identity cross](https://hoto.lol/blog/where-power-and-identity-cross/) as "read next" | Post exists. Video cut done (`final-video/` in project files) |
| 3 | Tue 11-10 | Cultural | Growing up, "I'm fine" meant something else | What did "fine" mean at home? | [Love that showed up as food](https://hoto.lol/blog/love-that-showed-up-as-food/) | Post exists. Script drafted |
| 4 | Thu 11-12 | Philosophy | Stoics on what you control | What's one thing today that isn't up to you? | **New post needed:** "Two piles: what Epictetus meant by up to us" | Write by Sun 11-08 |
| 6 | Sat 11-14 | Philosophy | Rawls' veil of ignorance | Which rule would you change? | [We didn't all start at the same line](https://hoto.lol/blog/we-didnt-all-start-at-the-same-line/) | Post exists |
| 2 | Mon 11-16 | Cultural | Why "just rest" is easy advice for some | What did rest mean in your house? | [A rest from happiness](https://hoto.lol/blog/a-rest-from-happiness/) | Post exists |
| 5 | Tue 11-17 | Location | Same stress, different weight | What cushions your stress? | [Privilege is everything you never had to think about](https://hoto.lol/blog/privilege-is-everything-you-never-had-to-think-about/) | Post exists |
| 8 | Thu 11-19 | Philosophy | Camus and the pointless Monday | What small thing makes your day yours? | **New post needed:** "Camus and the pointless Monday" | Write by Sun 11-15 |
| 9 | Sat 11-21 | Location | Intersectionality in 40 seconds | Which overlap shapes your day? | [Where power and identity cross](https://hoto.lol/blog/where-power-and-identity-cross/) | Post exists |
| 7 | Mon 11-23 | Cultural | Who gets called "difficult"? | What label did others give you? | [When a label becomes the problem](https://hoto.lol/blog/you-are-not-the-problem-but-the-label-might-be/) | Post exists |
| 10 | Tue 11-24 | Philosophy | Frankl on meaning | What gives your week meaning? | **New post needed:** "What Frankl meant by meaning" (fix the logotherapy date first, see fact checks) | Write by Sun 11-22 |
| 11 | Thu 11-26 | Cultural | Whose normal is "normal"? | What's a norm you never questioned? | [What therapy ethics codes get right and miss about culture](https://hoto.lol/blog/what-therapy-ethics-codes-miss-about-culture/) | Post exists. 11-26 is Thanksgiving, so schedule it ahead or swap with #12 |
| 12 | Sat 11-28 | Philosophy | Why I study this | Why are you here? | [How great thinkers are made](https://hoto.lol/blog/how-great-thinkers-are-made/) | Post exists |

Same order as the 2026-11-02 social plan. The only change is the days: Mon/Tue/Thu/Sat instead of Mon/Tue/Wed.

### The three new posts

All three are "Sourced explainer" posts in the "Mind and how to live" theme. Each follows the hoto.lol rules: one framing question, sources linked, the strongest fair objection inside the piece, and a "Sit with this" that matches the video.

| Post | `question` (= video hook) | `sit` (= video closing question) | `voices` | Strongest objection to include |
|---|---|---|---|---|
| Two piles: what Epictetus meant by "up to us" | What is actually up to me today? | What's one thing today that isn't up to you? | Epictetus, Aaron Beck, Albert Ellis | "Accept what you can't control" can be used to tell people to accept injustice. Where does acceptance stop? |
| Camus and the pointless Monday | What do you do with a day that feels pointless? | What small thing makes your day yours? | Albert Camus | Is "imagine Sisyphus happy" just a nicer way of saying "cope"? |
| What Frankl meant by meaning | Can meaning be found in a bad week, or only made? | What gives your week meaning? | Viktor Frankl | Meaning can't be demanded of people in pain. Frankl's own story is not a template for anyone else's |

Each needs a `FRAMING` entry in `build.py` (`build.py` refuses to build if one is missing). Suggested `related`: Epictetus to `a-rest-from-happiness`, Camus to `how-great-thinkers-are-made`, Frankl to `is-there-a-perfect-income`.

## The weekly routine, merged

| Day | TikTok | Blog |
|---|---|---|
| Sun | Batch: film the week's 4 videos (webcam + cards), schedule them in TikTok Studio | Finish any companion post due that week. Publish it before its video goes live so the link works on day one |
| Mon, Tue, Thu, Sat | Video posts. Reply to comments that day | Nothing new. Check the companion post link from /links/ still works |
| Daily | Reply to comments (10 min) | Note any comment question worth a post |
| Sat | 10 min review: watch time, shares, profile visits, link clicks | Pick one comment question for `OPEN_QUESTIONS` on the front page, or for the next series |

Writing load: 3 new posts across 3 weeks, one per week, all on Sundays before their video.

## Content that flows both ways

**Blog to TikTok (series 2 ideas).** These posts already exist and have no video yet. Each already has a question that works as a hook:

- [The watcher in your pocket](https://hoto.lol/blog/the-watcher-in-your-pocket/) (panopticon and social media), a strong fit for TikTok itself
- [What Arendt meant by the banality of evil](https://hoto.lol/blog/what-arendt-meant-by-the-banality-of-evil/): "How do ordinary people take part in terrible things without deciding anything?"
- [What a Freudian slip can and cannot tell us](https://hoto.lol/blog/what-a-freudian-slip-can-and-cannot-tell-us/): "When a word slips out, does it mean anything?"
- [Is there a perfect income?](https://hoto.lol/blog/is-there-a-perfect-income/)
- [What we teach men about pain](https://hoto.lol/blog/what-we-teach-men-about-pain/): needs the 988 plate
- [Fearless speech for regular people](https://hoto.lol/blog/fearless-speech-for-regular-people/)
- [The rules nobody said out loud](https://hoto.lol/blog/the-rules-nobody-said-out-loud/)
- [One roll of toilet paper](https://hoto.lol/blog/one-roll-of-toilet-paper/)

That is most of a second 12-video run without writing anything new.

**TikTok to blog.** The front page already has an "Open questions" list (`OPEN_QUESTIONS` in `build.py`). Good comment questions go there first, then become a post when there is enough to say.

**Video 1 long cuts.** The 5 to 6 min lecture and the 5.5 min voiced essay (`video-01-social-location/essay/`) cover the same ground as the social location post plus micro/meso/macro and DeGraffenreid v. GM. Two options, pick one later:
- Add a short "Updated" section to the social location post with the micro/meso/macro levels and the GM case, and link the long video.
- Or post the essay audio as a podcast episode, since the site already hosts audio (`EPISODES`, `audio/`).

## One set of guardrails for both

- "Student reflection, not therapy or advice" on every video caption. The blog's crisis strip covers posts.
- 988 (call or text, US) on any video that touches hard feelings.
- No claims that philosophy, a tip, or a toy treats, cures, or prevents anything.
- Personal stories stay "my family," never "Asian American families."
- TikTok's AI-generated content label whenever the voice or visuals are AI. Posts drafted with AI help keep the `note` line (as on "Where power and identity cross").
- Claims get sources, in the post. The video names one source on screen (author, year) and the post links it.
- Errors get fixed in both places: a dated correction at the top of the post, and a pinned comment on the video.
- No em dashes in scripts or posts. Exploratory tone, student not therapist.

## Fact checks carried over from the social plan

- Frankl: say "Frankl, who founded logotherapy," not "later founded." He developed it in the 1930s, before the camps. Fix this before Video 10 and its post.
- Epictetus born enslaved: widely reported, confirm before it goes on screen or in the post.
- Rawls 1971, Camus 1942 (French original), Crenshaw 1989, White and Epston 1990, Beck and Ellis on Stoic influence: look right, check against your course texts.

## Before the series starts

- [ ] Merge PR #83 so hoto.lol/links/ is live for the bio
- [ ] Write the Epictetus post (due Sun 11-08)
- [ ] Decide whether Video 1 posts this week or on Mon 11-09
- [ ] Add a tracking sheet: video, post, posted date, views, watch time, shares, link clicks, and which post got the click
