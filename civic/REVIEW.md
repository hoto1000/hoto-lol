# Where do my political views sit? Prototype review notes

Status: live at https://hoto.lol/civic/ (source: `civic/quiz.html`, built by `build.py` into `docs/civic/index.html`).

Live-version changes from the prototype:
- No AdSense. The page is built outside `page()`, and `build.py` fails the build if an ad script or a missing no-network CSP ever appears on it.
- No "save on this device" option. Other hoto.lol pages load Google ad scripts on the same origin, and those scripts could read browser storage. Answers now live only in the open tab, and any old prototype key is deleted on load.
- Site header, nav, crisis line, and colors match the rest of hoto.lol. CSP allows only same-origin `site.css` and favicon.
- Labeled an independent civic tool.
- Reviewer tests show only at https://hoto.lol/civic/#review.

## 1. What it is

- 21 questions, 7 areas, 3 questions each: economic policy, public services, civil liberties, social policy, climate and energy, immigration, government power.
- Each question shows two statements (A and B). Answer options: much closer to A, a bit closer to A, in between, a bit closer to B, much closer to B, not sure, skip. Skip is the default.
- Results show each area on its own line with a dot (average), a band (lowest to highest answer), a plain-language verdict, and how many answers it rests on.
- An optional, collapsed "rough left–right summary" uses only 5 areas and needs at least 3 of them answered.
- An optional social-location reflection page sits after results. It has checkboxes and prompts only. No text entry, nothing saved, nothing scored.

## 2. Methods note (also shown in the page)

- Scoring: each answer becomes a value from −1 to +1 toward one end of that area. "Much closer" = full step (±1), "a bit closer" = half step (±0.5), "in between" = 0.
- Reverse coding: in every area, statement A points to the low end on some items and the high end on others, so always picking A does not push toward one end.
- "Not sure" and skipped answers are excluded, never treated as middle, and reported separately.
- Area labels:
  - Not placed: no counted answers.
  - Mixed: at least one answer ≥ 0.5 toward each end.
  - Near the middle: average within ±0.25.
  - Leans somewhat / leans clearly: average beyond ±0.25 / ±0.75.
- Confidence: one answer = "very rough"; all three answered with range ≤ 0.5 = "fairly consistent"; otherwise "rough."
- Rough summary: averages economic, public services, social, climate, and immigration, using conventional US left/right readings. Civil liberties and government power are excluded because people across the usual spectrum land on both sides. Marked "split" if areas sit ≥ 0.4 toward both sides.
- Limits: few items per area, US-focused framing, wording effects, a snapshot rather than a measure of stable identity. Not validated against any external instrument.

## 3. Privacy design

| Check | How it is met | Verified |
|---|---|---|
| No transmission | CSP `default-src 'none'; connect-src 'none'; form-action 'none'`. No external scripts, fonts, or images. The only URLs are plain citation links in the methods note, opened in a new tab with `noreferrer`, carrying no answer data. | Checked |
| No analytics, ads, accounts | None present; CSP would block them if added | Yes |
| No saving (live) | Answers kept in memory only. Saving was removed for the live site because ad scripts share the origin's storage. | Simulated run: 0 storage keys |
| Saved data is minimal | Payload is `{v, answers}` with valid item IDs only. Tampered or junk values are dropped on load. | Test 11 |
| Social location never stored or scored | Reflection choices live in a memory-only Set, never read by scoring or storage | Simulated run |
| Easy reset | "Reset all answers" on every screen, inline confirm, clears memory and storage | Simulated run |
| Not indexed | `robots noindex, nofollow`, `referrer no-referrer` | In file |

If this later moves onto the site, keep these true:
- Serve the same CSP as an HTTP header on that route.
- Turn off any site-wide analytics injection for that path (for example Cloudflare Web Analytics or a Next.js analytics component).
- Never put answers in the URL, query string, or share links.
- Render it client-only, with no server actions and no API routes touching answers.

## 4. Accessibility checks

| Check | Result |
|---|---|
| axe-core scan: intro, area page, results, reflection | 0 violations on each (contrast checked separately) |
| Color contrast, light theme | Text 16.5:1, muted 6.8:1, links/buttons 6.9:1 (AA pass, mostly AAA) |
| Color contrast, dark theme | Text 13.9:1, muted 7.3:1, links/buttons 7.6–8.3:1 |
| Grouping | Each question is a `fieldset` with a `legend`. Radio group is described by both statements. |
| Keyboard | All native controls. Visible 3px focus ring. Focus moves to the page heading on each step. |
| Screen readers | `aria-live` announces step changes, results ready, save on/off, and reset. Result lines have text labels with numbers. |
| Not color-only | Every result has a written verdict and answer count; bars are a supplement. |
| Touch targets | Options and buttons ≥ 44px tall |
| Motion | Transitions only with `prefers-reduced-motion: no-preference` |
| Dark mode | Follows system setting |
| Plain language | Longest statement is 24 words. Everyday wording, no jargon labels. |
| Mobile | Single column under 620px, 16px side gutter |

Still to check by hand: VoiceOver (iOS/macOS) and NVDA pass-through, 200% zoom, Windows high-contrast mode.

## 5. Neutral wording review

Rules applied to every item:
1. Both statements give a reason, stated the way its own supporters would put it.
2. Both statements are about policy, not about kinds of people.
3. Roughly equal length and strength in each pair.
4. Neither end of any area is labeled as good, extreme, or "correct."
5. No party, candidate, or ideology names in questions or per-area results.

| Item | Concern considered | Choice made |
|---|---|---|
| e1 Minimum wage | "Left to markets" could read as uncaring | Paired with job-loss reason so the value is explicit |
| e2 Taxes | Avoided loaded terms like "tax the rich" and "job creators" | "High earners and large companies" on both sides |
| p1 Health coverage | Universal side admits cost ("even if taxes go up") | Private side admits a tradeoff by naming targeted help |
| p3 Work requirements | "Cut off" could feel emotive | Kept, since the other side's "have to work" is equally direct |
| c2 Online speech | Not a clean left/right issue | Kept in civil liberties, which is excluded from the summary |
| s1 Abortion | Most charged item | Each side states its core moral reason in under 10 words |
| s2 Drug use | Named drugs to avoid "drugs" meaning only cannabis | Both sides framed around protecting people |
| s3 Religion in schools | "Voluntary" added so A is not read as coercive | B framed as neutrality, not hostility to religion |
| i2 Status | Avoided "illegal aliens" and "undocumented immigrants" | Neutral "people without legal status" |
| i3 Asylum | Each side names its cost ("even if…") | Symmetric structure |
| g2 Emergency powers | Avoided naming any current officeholder | Framed as "the president," office not person |

Known residual issues for a human reviewer:
- The low/high pole labels for social policy ("traditional rules" vs "update") may still feel tilted to some readers. Worth testing with people across the spectrum.
- "Climate and energy" low pole leads with affordability; some may want "energy security" too.
- No item covers guns, trade, or foreign policy. Add an area or note the gap.
- US framing only.

## 6. Sample tests

Run in the page under "For reviewers: run sample tests," or in Node by evaluating the CORE block. Current result: 12 of 12 pass.

| # | Input | Expected | Result |
|---|---|---|---|
| 1 | Everything skipped | All 7 areas "not placed," 3 skipped each | Pass |
| 2 | Everything skipped | No rough summary | Pass |
| 3 | Everything "not sure" | Not placed; unsure counted apart from skipped | Pass |
| 4 | e1 much closer to A, e3 much closer to B (contradictory) | Economic = "mixed," range −1 to +1, not averaged to middle | Pass |
| 5 | e2 much closer to A only (reverse-coded) | Leans clearly toward "more government-guided" | Pass |
| 6 | One answer in an area | Marked "very rough" | Pass |
| 7 | All "in between" | Every area near the middle, fairly consistent | Pass |
| 8 | Strong one way on econ/services, strong the other on immigration/climate | Summary "split," value about 0 | Pass |
| 9 | Only 2 summary areas answered | No summary | Pass |
| 10 | Only civil liberties and government power answered | Summary uses 0 areas | Pass |
| 11 | Save payload with junk value, unknown key, reflection data | Only valid answers saved | Pass |
| 12 | Item design | Each area mixes which end A points to | Pass |

End-to-end simulated run (headless DOM): opted into saving, gave contradictory econ answers, all "not sure" on services, then results. Econ showed "Mixed," services "Not placed," summary correctly withheld, reflection choice not in storage, and reset left storage empty and returned to the intro.

## 7. Sources

Each source was checked against the publisher or a university record page. The visitor-facing ones are also in the page's methods note.

**Why score each area separately**
- Feldman, S., & Johnston, C. (2014). Understanding the determinants of political ideology: Implications of structural complexity. *Political Psychology, 35*(3), 337–358. https://doi.org/10.1111/pops.12055
  - Finds a single left–right scale is an incomplete basis. Economic and social ideology are both needed, and they have different causes.
- Treier, S., & Hillygus, D. S. (2009). The nature of political ideology in the contemporary electorate. *Public Opinion Quarterly, 73*(4), 679–703. https://doi.org/10.1093/poq/nfp067
  - Finds the public's views stay multidimensional. Many people are liberal on one dimension and conservative on another, and often call themselves "moderate" or "don't know" on a single scale. This supports the "mixed" label.

**Why paired statements instead of agree/disagree**
- Pew Research Center. (n.d.). Writing survey questions. https://www.pewresearch.org/our-methods/about-our-us-surveys/writing-survey-questions/
  - Says agree/disagree items invite acquiescence and recommends a choice between alternative statements. Also advises randomizing unordered lists and allows reversing scale order for part of a sample.
- Saris, W., Revilla, M., Krosnick, J. A., & Shaeffer, E. M. (2010). Comparing questions with agree/disagree response options to questions with item-specific response options. *Survey Research Methods, 4*(1), 61–79. https://doi.org/10.18148/srm/2010.v4i1.2682
  - Finds agree/disagree answers are much lower quality than item-specific formats.
- Pew Research Center. (2014). Why the typology quiz questions are asked the way they are. https://www.pewresearch.org/short-reads/2014/06/27/why-the-typology-quiz-questions-are-asked-the-way-they-are/
  - Pew uses paired opposing statements, and no single answer decides a result. This matches the averaging approach here.
- Pew Research Center. (2026). About the political typology. https://www.pewresearch.org/about-the-political-typology/
  - The 2026 typology, released June 2026, is the best-known comparable tool. Its quiz places people in one of nine groups. This prototype deliberately avoids group labels.

**The "not sure" option (a caution)**
- Krosnick, J. A., et al. (2002). The impact of "no opinion" response options on data quality: Non-attitude reduction or an invitation to satisfice? *Public Opinion Quarterly, 66*(3), 371–403. https://doi.org/10.1086/341394
  - Found that no-opinion options did not improve answer quality, and that low-effort respondents chose them more. The prototype keeps "not sure" because the brief requires it and a self-reflection tool shouldn't pressure people. It never scores "not sure" as middle and shows it in every result.

**Accessibility**
- W3C. (2023). Web Content Accessibility Guidelines (WCAG) 2.2. https://www.w3.org/TR/WCAG22/
  - Became a W3C Recommendation on October 5, 2023, adding nine success criteria. It's the right target for the site.

**Privacy (background, not legal advice)**
- UK Information Commissioner's Office. Special category data (political campaigning guidance). https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-for-the-use-of-personal-data-in-political-campaigning-1/special-category-data/
  - Political opinions are special category data under UK GDPR. Inferred opinions count too, even if the inference is uncertain. A results screen is an inference, which supports keeping everything on the device.
- IAPP. Top 10 operational impacts of the CPRA, Part 3. https://iapp.org/news/a/top-10-operational-impacts-of-the-cpra-part-3-the-cpras-new-provisions-regarding-the-right-to-correct-and-the-treatment-of-sensitive-personal-informal
  - Its list of California "sensitive personal information" includes racial or ethnic origin, religious or philosophical beliefs, and health. Political opinions don't appear on that list. Several of the social-location topics would still be sensitive in California if they were ever collected, which supports collecting none of them.

**Design gaps the sources point to**
- Pew advises randomizing order. The prototype alternates which end statement A points to, but doesn't randomize A/B position per visitor or reverse the scale for half of visitors. That's a possible improvement.
- None of these sources validate this specific 21-item set. The methods note says so, and it shouldn't be described as a validated measure.

## 8. Open decisions for you

- Age focus: if the site may reach teens, decide whether this tool belongs there at all.
- Whether to add guns, trade, or foreign policy areas.
- Whether to get 3 to 5 reviewers with different politics to read every pair before launch.

## Update: social location lens (Oct 25, 2026)

**What changed.** The optional reflection page became a fuller "social location lens," linked from the top of the results and from the button at the bottom.
- **Definition and framing.** The page defines social location, says it shapes experience and access to power and resources, and says plainly that it does not decide anyone's views.
- **Broad, optional checkboxes.** Nine parts of life to reflect on, now including gender and family roles, and race, ethnicity, and how others treat me. Nothing to type.
- **Area by area.** For each of the 7 areas:
  - The visitor's own result.
  - One optional question: how much does this area touch your life, or the lives of people close to you? Options: a lot, some, not much, rather not say. It never asks which experience or why.
  - A list of whose lives the area touches, described by situation only, never by what anyone thinks.
  - Three perspective-taking questions.
  - A short neutral note that responds to the visitor's stake. Example: "close to home" plus mixed answers gives "That can happen when a policy's costs and benefits both land on you."
- **On the results page.** An area the visitor marked shows "Close to home: a lot (your answer…; not scored)." It never moves a dot, band, label, or summary.
- **Methods note.** Explains the approach and cites Crenshaw (1989) and Watts-Jones (2010).

**Why it isn't scored.** The brief says never to infer ideology from social location and to keep it separate from scoring. Research on ideology also shows people who share a background often disagree. So the tool takes social location into account by helping people reflect on it, not by adjusting results.

**New tests (20 total, all pass)**

| # | Check | Result |
|---|---|---|
| 13 | Stake answers and reflection choices never change any score | Pass |
| 14 | Social location never included in saved data | Pass |
| 15 | Skipped or "rather not say" adds no note | Pass |
| 16 | Each answered stake gets its own note | Pass |
| 17 | "A lot" with mixed answers gets the mixed note | Pass |
| 18 | Bad stake values are dropped | Pass |
| 19 | Every area lists at least 4 positions | Pass |
| 20 | Lens wording never uses predictive or partisan words (tend to, usually, more likely, believe, support, oppose, vote, left, right, liberal, conservative, party names) | Pass |

Simulated run: the dots and bands were identical before and after using the lens, a tag appeared only where a stake was given, nothing was written to storage, and reset cleared the tags. The accessibility scan shows 0 problems on the lens and results screens.

**Open question for a human reviewer:** do the "whose lives this touches" lists feel balanced to readers across the spectrum? Each one was written to name positions on both sides of the policy's costs and benefits.

## Update: recommended changes applied (Oct 25, 2026)

**1. Randomized statement order (Pew advice).** Each visitor sees a random A/B order for every question, chosen fresh each visit and on reset, and never stored. Answers are always stored in the same internal orientation, so scoring can't depend on what someone saw as "A." "Show my answers" now names the statement ("Much closer to: '…'") instead of a letter.

**2. Three new areas, for 10 areas and 30 questions.** Each area has 3 items, with statement A pointing different ways.
- Gun policy (background checks, concealed carry, semi-automatic rifles). Included in the rough summary, since it maps onto the usual US left/right.
- Trade (tariffs, trade deals, making key products at home). Left out of the summary because it cuts across the usual sides.
- Foreign policy (commitments abroad, military aid, acting alone or with others). Left out of the summary for the same reason.

Each new area also has a social-location lens entry that passes the wording check.

**3. Rebalanced pole labels.**
- Social policy: "More weight on shared norms and protections" vs "More room for personal choice." It was "Keep or restore traditional rules" vs "Loosen or update traditional rules."
- Climate: the low end is now "Prioritize affordable, reliable, secure energy."

**4. "Where these ideas come from" panel.** This is optional and collapsed, on the results page. Each area lists thinkers and texts drawn on toward each end, plus ones claimed by both sides: Locke, Burke, Mill, Rawls, Nozick, Smith, Hamilton, Washington, Polybius, the Federalist, the Bible, Rerum Novarum, Quadragesimo Anno, the Catechism, Heller, NATO Article 5, and the just war tradition.
- It is never matched to the visitor's answers.
- A test requires that no area shows only one side. Climate and gun policy show only the "both sides" sources.

**Tests: 26 of 26 pass.** New checks cover the random-order round trip, equal scores under either order, 10 areas with 30 questions, summary inclusion and exclusion, and the ideas panel showing both sides.

In a simulated run, the same intended answers given under the normal order and the fully reversed order produced identical results on all 10 areas. The accessibility scan shows 0 problems on the intro, question, results, and lens screens, and nothing was written to storage.

**Still needs people, not code**
- Have 3 to 5 reviewers with different politics read all 30 pairs, the pole labels, the lens lists, and the ideas panel.
- Test by hand with VoiceOver and NVDA, at 200% zoom, and in Windows high-contrast mode.
- The new items name current-debate examples (the AR-15, chips, medicines). Recheck them yearly.
