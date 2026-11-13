#!/usr/bin/env python3
"""Builds the Project Hoto site (hoto.lol) into ./docs. Run: python3 build.py

To add a blog post: write the body HTML in content/posts/<slug>.html,
then add an entry to POSTS below (newest first).
To add an episode: put the audio in podcasts/ and add an entry to EPISODES.
"""
import hashlib
import html
import math
import pathlib
import re
import difflib
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"  # GitHub Pages serves main:/docs

SITE = "otohay blog"
# Versioned stylesheet link. Cloudflare tells browsers to keep site.css for 4 hours,
# while pages are kept for 10 minutes. Putting a hash of the CSS in the link means a
# new page always loads the matching styles, and an unchanged stylesheet stays cached.
import sys
sys.path.insert(0, str(ROOT))
import social_location as SL  # the social location interview (no script)
import where_you_stand as WS  # the "Where do you stand?" questionnaire (no script)
assert SL.css_block() in (ROOT / "site.css").read_text(encoding="utf-8"), \
    "site.css interview rules are out of date: run python3 social_location.py, then build again"
assert WS.css_block() in (ROOT / "site.css").read_text(encoding="utf-8"), \
    "site.css questionnaire rules are out of date: run python3 where_you_stand.py, then build again"
CSS_VERSION = hashlib.sha256((ROOT / "site.css").read_bytes()).hexdigest()[:10]
CSS_LINK = f'<link rel="stylesheet" href="/site.css?v={CSS_VERSION}">'

POSTS = [
    {
        "slug": "what-i-mean-by-capitalism",
        "title": "What I mean when I say capitalism",
        "date": "2026-11-13",
        "summary": "Part one of \"Capitalism, explained plainly\": private ownership, wage labor, profit and accumulation, how it differs from trade, what socialists propose, and what Adam Smith and Milton Friedman argue.",
    },
    {
        "slug": "we-made-it-okay-to-talk",
        "title": "We made it okay to talk. Getting help is still too hard.",
        "date": "2026-11-10",
        "summary": "A student on the gap between talking about mental health and finding care: 137 million people in shortage areas, providers with full caseloads, and four small things to try this week.",
    },
    {
        "slug": "the-queue-is-the-policy",
        "title": "The queue is the policy: who pays the hidden time tax?",
        "date": "2026-11-10",
        "summary": "A student's argument that waiting quietly decides who can use a system: Social Security phone wait times, who can afford to hold, my own disability insurance paperwork, and one redesign.",
    },
    {
        "slug": "what-the-panthers-and-king-both-saw-about-poverty",
        "title": "What the Black Panthers and Dr. King both saw about poverty",
        "date": "2026-11-10",
        "summary": "Why I think the Black Panther Party and Martin Luther King Jr. belong in one story: free breakfast, a guaranteed income, why the FBI went after both, and what I'm trying.",
    },
    {
        "slug": "why-i-think-everyone-should-try-therapy",
        "title": "Why I think everyone should try therapy",
        "date": "2026-11-07",
        "summary": "Why I think everyone should try therapy at least once, what surprised me in school, and three things I'm trying.",
    },
    {
        "slug": "why-so-many-of-us-feel-lonely",
        "title": "Why so many of us feel lonely",
        "date": "2026-11-06",
        "summary": "What the Surgeon General's report on loneliness found, what couples therapy says about needing people, and three things I'm trying.",
    },
    {
        "slug": "what-fights-are-really-asking",
        "title": "What fights are really asking",
        "date": "2026-11-06",
        "summary": "What Emotionally Focused Therapy taught me about fights: why many fights are a protest, the negative cycle, what's under the anger, and three things I'm trying.",
    },
    {
        "slug": "who-was-your-secure-base",
        "title": "Who was your secure base? What attachment theory taught me",
        "date": "2026-11-06",
        "summary": "What attachment theory says about love: Bowlby's report, Ainsworth's Strange Situation, the love quiz, earned security, the feminist critique, and three things I'm trying.",
    },
    {
        "slug": "why-mental-health-matters",
        "title": "Why mental health matters",
        "date": "2026-11-06",
        "summary": "Half of mental health conditions start by age 14, many people wait years for help, and three things I'm trying.",
    },
    {
        "slug": "learning-to-apologize-and-move-on",
        "title": "Learning how to apologize, and how to move on",
        "date": "2026-11-06",
        "summary": "What couples research and restorative justice taught me about apologizing, guilt versus shame, and letting myself move on.",
    },
    {
        "slug": "why-we-blame-the-person-instead-of-the-situation",
        "title": "Why we blame the person instead of the situation",
        "date": "2026-11-06",
        "summary": "Why we judge others harder than ourselves: the Castro essays, the Good Samaritan study, how culture shapes blame, and three things I'm trying.",
    },
    {
        "slug": "how-competition-wears-down-the-people-at-the-bottom",
        "title": "How competition wears down the people at the bottom",
        "date": "2026-11-06",
        "summary": "Survival of the fittest, Adam Smith's sympathy, the Matthew effect, the Whitehall study, mutual aid, and three things I'm trying.",
    },
    {
        "slug": "why-therapists-learn-cultural-humility",
        "title": "Why therapists learn cultural humility",
        "date": "2026-11-06",
        "summary": "Some history first: the Tuskegee study, cultural competence, two doctors in Oakland who offered the word humility, and three things I'm trying.",
    },
    {
        "slug": "socialism-starts-with-culture-philadelphia",
        "title": "Socialism starts with culture: Philadelphia",
        "date": "2026-11-06",
        "summary": "Why I think neighbors practice sharing before a country votes for it, Gramsci's war of position, and what Philly has shared since 1731.",
    },
    {
        "slug": "who-raises-a-kid",
        "title": "Who raises a kid? Bronfenbrenner's circles",
        "date": "2026-11-05",
        "summary": "Urie Bronfenbrenner's map of everything that raises a kid, what it changed about how I think about blame, and three things I'm trying.",
    },
    {
        "slug": "the-person-is-not-the-problem",
        "title": "The person is not the problem: what narrative therapy taught me",
        "date": "2026-11-05",
        "summary": "Michael White and David Epston's narrative therapy, how it changed the way I talk about homelessness, and three things I'm trying.",
    },
    {
        "slug": "the-identified-patient",
        "title": "The identified patient: what one struggling kid can be carrying",
        "date": "2026-11-05",
        "summary": "The family therapy idea of the identified patient, where I see it outside the therapy room, and three things I'm trying.",
    },
    {
        "slug": "who-gets-to-be-the-thinker",
        "title": "Who gets to be called a thinker? Gramsci and Collins",
        "date": "2026-11-05",
        "summary": "Gramsci on who gets the title of thinker, Patricia Hill Collins on knowledge built outside universities, and three steps I'm trying.",
    },
    {
        "slug": "intergenerational-trauma-vietnamese-americans",
        "title": "My parents never had a word for it: intergenerational trauma",
        "date": "2026-11-05",
        "summary": "Intergenerational trauma as a Vietnamese American: the rules of my house, why they made sense, and three things I'm trying.",
    },
    {
        "slug": "somewhere-to-put-it",
        "title": "Somewhere to put it: what society owes kids with nowhere to go",
        "date": "2026-11-03",
        "summary": "Why so many kids have nowhere to put their anger: who public space is for, how Bronx kids invented hip hop as their own outlet, and what we choose to pay for.",
    },
    {
        "slug": "the-story-my-family-handed-me",
        "title": "The story my family handed me",
        "date": "2026-11-03",
        "summary": "My story in scenes: growing up Vietnamese American in Pennsylvania, moving to San Diego, a role-play in therapy school, and what's helping me.",
    },
    {
        "slug": "do-you-know-the-number-988",
        "title": "Do you know the number for a mental health emergency?",
        "date": "2026-11-03",
        "summary": "988, the free and confidential crisis line most people still haven't heard of.",
    },
    {
        "slug": "where-power-and-identity-cross",
        "title": "Where power and identity cross: intersectionality through Foucault",
        "date": "2026-11-02",
        "summary": "A student reads Kimberl\u00e9 Crenshaw's intersectionality next to Michel Foucault's ideas about power, knowledge and categories. Foucault never used the word. Putting them together is my own reading.",
    },
    {
        "slug": "who-gets-measured-and-who-does-the-measuring",
        "title": "Who Gets Measured, and Who Does the Measuring",
        "date": "2026-10-28",
        "summary": "A reading of two school debates, behavior scores and AI glasses at exams, through Michel Foucault's idea of the examination. My own reading, not his voice.",
    },
    {
        "slug": "the-rules-nobody-said-out-loud",
        "title": "The rules nobody said out loud",
        "date": "2026-10-27",
        "summary": "A student on the unspoken rules families run on: a quick test to find yours, why they made sense once, where I caught myself running mine, and three ways to spot your own.",
    },
    {
        "slug": "what-therapy-ethics-codes-miss-about-culture",
        "title": "What therapy ethics codes get right and miss about culture",
        "date": "2026-10-27",
        "summary": "A student's read of the AAMFT and CAMFT codes of ethics through a multicultural lens: where they ask for respect and awareness, and where they stop short on power, privilege and systems.",
    },
    {
        "slug": "is-there-a-perfect-income",
        "title": "Is there a perfect income? Why happiness seems to level off",
        "date": "2026-10-27",
        "summary": "A student reads the research on money and happiness: the famous $75,000 plateau, the studies that challenged it, and why more income matters less the more you have.",
    },
    {
        "slug": "love-that-showed-up-as-food",
        "title": "Love that showed up as food: growing up in a quiet Vietnamese American home",
        "date": "2026-10-27",
        "summary": "A student's story about a home where love came through cooking and fixing things instead of words, where that came from, and what I'm still working on as a future therapist.",
    },
    {
        "slug": "privilege-is-everything-you-never-had-to-think-about",
        "title": 'Privilege is everything you never had to think about',
        "date": "2026-10-27",
        "summary": "A blunt student take on privilege: the list of things that were easy that you never noticed were easy, and how to start seeing your own.",
    },
    {
        "slug": "one-roll-of-toilet-paper",
        "title": "One roll of toilet paper: what a week of scarcity taught me",
        "date": "2026-10-27",
        "summary": "A student's honest look at a class assignment where one roll had to last a week: how scarcity takes up headspace, why my frugality is a choice, and what it means for the clients I want to help.",
    },
    {
        "slug": "the-i-am-poem-who-we-say-we-are",
        "title": 'The "I Am" poem and who we say we are',
        "date": "2026-10-27",
        "summary": "A student on writing an \"I Am\" poem for a capstone class: where people start, why heritage lines carry so much, and why reading it out loud was the hard part.",
    },
    {
        "slug": "we-didnt-all-start-at-the-same-line",
        "title": "Social privilege: we didn't all start at the same line",
        "date": "2026-10-27",
        "summary": "A student's honest take on social privilege: a privilege-walk video, the statement that caught me off guard, why effort isn't the whole story, and a short exercise to find your own line.",
    },
    {
        "slug": "social-location-where-you-stand",
        "title": 'Social location: where you stand decides what you see',
        "date": "2026-10-27",
        "summary": "A blunt student take on social location: the stack of race, class, family and culture that decides what you notice, what you miss, and what you call normal.",
    },
    {
        "slug": "what-a-freudian-slip-can-and-cannot-tell-us",
        "title": 'What a Freudian slip can and cannot tell us',
        "date": "2026-10-27",
        "summary": "A student's look at Freud, slips of the tongue, and the unconscious: what Freud claimed, what researchers found since, and where schemas and attachment theory fit.",
    },
    {
        "slug": "what-arendt-meant-by-the-banality-of-evil",
        "title": 'What Arendt meant by the banality of evil',
        "date": "2026-10-27",
        "summary": "Hannah Arendt watched Adolf Eichmann's trial and coined a phrase people still misread. What she claimed, what critics say, and why thinking matters.",
    },
    {
        "slug": "philly-protests-and-rallies-this-week",
        "title": 'Philadelphia protests and rallies, late October to early November',
        "date": "2026-10-27",
        "summary": "A sourced, plain list of public protests, rallies, and vigils in Philadelphia through November 7, with what is uncertain.",
    },
    {
        "slug": "what-we-teach-men-about-pain",
        "title": 'What we teach men about pain: stigma, silence, and the help that misses them',
        "date": "2026-10-27",
        "summary": "Why help so often fails to reach men: what the CDC and NIMH numbers show, what may be missed, and the rules many of us inherit.",
    },
    {
        "slug": "fearless-speech-for-regular-people",
        "title": 'Fearless speech for regular people: parrhesia meets boundary scripts',
        "date": "2026-10-28",
        "summary": "Foucault's idea of parrhesia, what it is not, and four short boundary sentences for work and family.",
    },
    {
        "slug": "you-are-not-the-problem-but-the-label-might-be",
        "title": 'When a label becomes the problem: power/knowledge meets diagnosis',
        "date": "2026-10-27",
        "summary": 'Foucault on power, knowledge and norms: labels can help people, and it is still fair to ask who decided where the line goes.',
    },
    {
        "slug": "the-watcher-in-your-pocket",
        "title": 'The watcher in your pocket: the panopticon meets social media',
        "date": "2026-10-26",
        "summary": 'How a prison design from 1786 explains why we edit ourselves online, and one small thing to try this week.',
    },
    {
        "slug": "when-watching-students-becomes-the-lesson",
        "title": "When Watching Students Becomes the Lesson",
        "date": "2026-10-24",
        "summary": "Schools collect more data on students than ever. They should have to show it helps, explain it, and let people push back when it is wrong.",
    },
    {
        "slug": "a-school-should-be-a-harbor",
        "title": "A school should be a harbor",
        "date": "2026-10-24",
        "summary": "Eight small, testable ways to make a school feel safe: private help, a calm start, a quiet room, meals without shame, and rules that listen.",
    },
    {
        "slug": "a-most-agreeable-war",
        "title": "A Most Agreeable War",
        "date": "2026-10-23",
        "summary": "An essay in the manner of an old drawing-room novel: on the pride of the men who start wars and the prejudice of the people asked to cheer them on.",
    },
    {
        "slug": "what-im-learning-about-third-parties",
        "title": "What I'm Learning About Third Parties",
        "date": "2026-10-23",
        "summary": "Most Americans say they want a third major party and almost none vote for one. A sourced explainer on why third parties lose, what they win anyway, and the reforms already changing the rules.",
    },
    {
        "slug": "a-rest-from-happiness",
        "title": "A Rest From Happiness",
        "date": "2026-10-23",
        "summary": "Being happy is good. Being expected to be happy all the time is work, and work needs breaks. On giving yourself permission to just be okay.",
    },
    {
        "slug": "how-great-thinkers-are-made",
        "title": "How great thinkers are made",
        "date": "2026-10-23",
        "summary": "Six habits that build a sharper mind, from reading the originals to arguing with people who disagree.",
    },
]

EPISODES = [
    {
        "slug": "is-toxic-happiness-making-us-miserable",
        "title": "Is Toxic Happiness Making Us Miserable?",
        "date": "2026-10-24",
        "length": "7 min",
        "summary": "Is the pressure to always be happy making us miserable? An audio episode.",
        "audio": "/podcasts/is-toxic-happiness-making-us-miserable.m4a",
        "overview": [],
    },
    {
        "slug": "a-study-on-happiness",
        "title": "A Study on Happiness",
        "date": "2026-10-23",
        "length": "9 min",
        "summary": "What happiness really is, why change matters, and why learning every side of politics can help us know ourselves.",
        "audio": "/podcasts/why-modern-happiness-is-broken.m4a",
        "overview": [
            "Hi, and welcome to a study on happiness. I believe happiness is worth studying as carefully as we study anything else, because it shapes every part of how we live.",
            "We often think happiness means feeling joyful all the time. But real happiness is quieter than that. It's contentment. It's being at peace with your own life, even when that life is hard. Every generation in history has faced turmoil, loss, and struggle. The people who found happiness didn't escape those things. They learned to carry them.",
            "I believe God built change into the world. Change can feel frightening, but it's also how we grow. Maybe change is part of a larger design, one meant to protect us and move us toward something better.",
            "If happiness can be studied, then so can the society around us. I'll be honest. I don't know where I stand on politics yet. But I know I don't want to be apolitical. I believe every ideology has its strengths and its blind spots. And if more of us took the time to really understand them, I think we'd gain something powerful: self-awareness, and a clearer sense of who we are.",
            "That's what this country is supposed to be about. Freedom. The freedom to be whoever we want to be. So I want to ask hard questions, like whether the Constitution should be updated to reflect who we are today. Over the past century, America has become far more diverse. Maybe our founding rules should grow with the people they serve.",
            "So let's ask the big questions together. What makes a life feel full? And how can we build a country where more people get to feel that way?",
        ],
    },
]

# ---------------------------------------------------------------------------
# Editorial framing. Kept separate from POSTS and EPISODES so adding a post or
# an episode stays a one-place edit. Every essay is led by the question it asks.
#   question: the hard question the essay works on (shown above the title)
#   theme:    which shelf it sits on in the question index
#   kind:     Essay, Opinion, Sourced explainer, or Video script (opinion is always labeled)
#   sit:      one question for the reader to sit with at the end
#   related:  slug of one essay to read next
#   voices:   thinkers the essay itself names (never add names it doesn't use)
#   corrections: optional list of ("YYYY-MM-DD", "what changed"), shown at the top
# ---------------------------------------------------------------------------
THEMES = ["Politics and civic life", "Schools", "Mind and how to live", "Mental health"]

FRAMING = {
    "what-i-mean-by-capitalism": {
        "question": "What do people actually mean when they say capitalism?",
        "theme": "Politics and civic life",
        "kind": "Sourced explainer",
        "note": "Drafted with AI help from the original texts and published sources, then reviewed by me.",
        "sit": "When you hear the word capitalism, what picture comes to mind first, and where did you get it?",
        "related": "how-competition-wears-down-the-people-at-the-bottom",
        "voices": ["Karl Marx", "Friedrich Engels", "Adam Smith", "Milton Friedman", "Chiara Cordelli"],
    },
    "we-made-it-okay-to-talk": {
        "question": "What happens after someone finally asks for help?",
        "theme": "Mental health",
        "kind": "Essay",
        "note": "Organized with AI help and checked against published government sources.",
        "sit": "When you or someone close to you tried to find help, what got in the way?",
        "related": "why-i-think-everyone-should-try-therapy",
        "voices": [],
    },
    "the-queue-is-the-policy": {
        "question": "Who gets screened out when the only way in is a long wait?",
        "theme": "Politics and civic life",
        "kind": "Essay",
        "note": "My own argument and experience, organized with AI help and checked against published sources.",
        "sit": "What wait, form or phone line has worn you down, and who could afford to skip it?",
        "related": "privilege-is-everything-you-never-had-to-think-about",
        "voices": ["Annie Lowrey"],
    },
    "what-the-panthers-and-king-both-saw-about-poverty": {
        "question": "What did the Black Panthers and Dr. King have in common?",
        "theme": "Politics and civic life",
        "kind": "Sourced explainer",
        "note": "Drafted with AI help from published sources, then reviewed by me.",
        "sit": "What need on your block could neighbors meet together?",
        "related": "socialism-starts-with-culture-philadelphia",
        "voices": ["Martin Luther King Jr.", "Huey P. Newton", "Bobby Seale", "Fred Hampton", "Alondra Nelson"],
    },
    "somewhere-to-put-it": {
        "question": "Where is a kid supposed to put the anger?",
        "theme": "Mental health",
        "kind": "Essay",
        "note": "Drafted with AI help from my voice memo and published sources, then reviewed by me.",
        "sit": "When you were a teenager and had nowhere to be, where did you go, and who was there?",
        "related": "what-we-teach-men-about-pain",
        "voices": ["Henri Lefebvre", "Robert Merton", "Elijah Anderson", "Avery Gordon", "\u00c9mile Durkheim"],
    },
    "where-power-and-identity-cross": {
        "question": "Who decides which boxes a person gets sorted into?",
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "note": "Drafted with AI help from published sources and my earlier posts, then reviewed by me.",
        "sit": "Which parts of your life cross in a way no form has ever asked about?",
        "related": "social-location-where-you-stand",
        "voices": ["Kimberl\u00e9 Crenshaw", "Michel Foucault", "Nancy Fraser"],
    },
    "is-there-a-perfect-income": {
        "question": "Is there an amount of money after which more stops making us happier?",
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "sit": "If you have a number in your head, what would it actually protect you from?",
        "related": "one-roll-of-toilet-paper",
        "voices": ["Daniel Kahneman", "Angus Deaton", "Matthew Killingsworth", "Barbara Mellers", "Andrew Jebb", "Erzo Luttmer"],
    },
    "what-a-freudian-slip-can-and-cannot-tell-us": {
        "question": "When a word slips out, does it mean anything?",
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "sit": "Think of a time a word slipped out. Were you tired or rushing, or was something else on your mind?",
        "related": "what-arendt-meant-by-the-banality-of-evil",
        "voices": ["Sigmund Freud", "John Bowlby", "Mary Ainsworth"],
    },
    "what-arendt-meant-by-the-banality-of-evil": {
        "question": "How do ordinary people take part in terrible things without deciding anything?",
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "sit": "When did you last repeat a phrase from your workplace or school without checking what it meant?",
        "related": "the-watcher-in-your-pocket",
        "voices": ["Hannah Arendt", "Bettina Stangneth"],
    },
    "philly-protests-and-rallies-this-week": {
        "question": "What does taking part in public life look like in my city this week?",
        "theme": "Politics and civic life",
        "kind": "Sourced explainer",
        "note": "A list, not an endorsement; not affiliated with any group listed.",
        "sit": "What is one way you take part in your community, and what would it take to try another?",
        "related": "what-im-learning-about-third-parties",
        "voices": [],
    },
    "what-we-teach-men-about-pain": {
        "question": "Why does help so often fail to reach men?",
        "theme": "Mental health",
        "kind": "Sourced explainer",
        "sit": "What did you learn, growing up, about what to do with a hard feeling?",
        "related": "you-are-not-the-problem-but-the-label-might-be",
        "voices": [],
    },
    "the-watcher-in-your-pocket": {
        "question": 'Do you act differently when you think someone might be watching?',
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "sit": 'Which of your habits would change if nobody could see them?',
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ['Michel Foucault', 'Jeremy Bentham'],
    },
    "you-are-not-the-problem-but-the-label-might-be": {
        "question": 'Who decides what counts as normal?',
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "sit": 'Which labels do you carry, and what do they leave out?',
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ['Michel Foucault'],
    },
    "fearless-speech-for-regular-people": {
        "question": 'What does it cost you to say the true thing, and is it worth it?',
        "theme": "Mind and how to live",
        "kind": "Sourced explainer",
        "sit": 'What is one sentence you have been rehearsing, and what would it cost to say it?',
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ['Michel Foucault'],
    },
    "when-watching-students-becomes-the-lesson": {
        "question": "What do students learn when someone is always watching?",
        "theme": "Schools",
        "kind": "Essay",
        "sit": "Who should get to decide what counts as a warning sign in a student's life?",
        "related": "a-school-should-be-a-harbor",
        "voices": ["Michel Foucault"],
    },
    "a-school-should-be-a-harbor": {
        "question": "What should school feel like?",
        "theme": "Schools",
        "kind": "Essay",
        "sit": "Think of a school you went to. What small thing made you feel wanted, or unwanted, and did anyone in charge know?",
        "related": "when-watching-students-becomes-the-lesson",
        "voices": [],
    },
    "a-most-agreeable-war": {
        "question": "Who starts wars, and who pays for them?",
        "theme": "Politics and civic life",
        "kind": "Essay",
        "sit": "When did you last change your mind about people you had judged from far away, and what changed it?",
        "related": "when-watching-students-becomes-the-lesson",
        "voices": ["Jane Austen"],
    },
    "what-im-learning-about-third-parties": {
        "question": "Why do Americans want a third party but almost never vote for one?",
        "theme": "Politics and civic life",
        "kind": "Sourced explainer",
        "sit": "If your vote could never be wasted, who would you vote for?",
        "related": "fearless-speech-for-regular-people",
        "voices": ["Maurice Duverger", "Richard Hofstadter"],
    },
    "a-rest-from-happiness": {
        "question": "Is the pressure to be happy making us less happy?",
        "theme": "Mind and how to live",
        "kind": "Essay",
        "sit": "Where in your week are you performing a feeling you don't have, and who is it for?",
        "related": "how-great-thinkers-are-made",
        "voices": ["Arlie Hochschild"],
    },
    "how-great-thinkers-are-made": {
        "question": "How does anyone learn to think well?",
        "theme": "Mind and how to live",
        "kind": "Essay",
        "sit": "What is the one problem you could spend twenty years thinking about?",
        "related": "a-rest-from-happiness",
        "voices": ["Aristotle", "Hobbes", "Madison", "Arendt", "Rawls"],
    },
    "why-i-think-everyone-should-try-therapy": {
        "question": "What keeps people from trying therapy?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "What's one thing that has kept you from trying therapy?",
        "related": "what-we-teach-men-about-pain",
        "voices": ["John Norcross", "Kenneth Howard"],
    },
    "why-so-many-of-us-feel-lonely": {
        "question": "Why do so many of us feel lonely?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "Who's someone you could reach out to today?",
        "related": "what-we-teach-men-about-pain",
        "voices": ["Vivek Murthy", "Sue Johnson", "John Bowlby", "James Coan"],
    },
    "what-fights-are-really-asking": {
        "question": "When someone you love yells about the dishes, what are they really asking?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "What do you think your last argument was really asking?",
        "related": "the-rules-nobody-said-out-loud",
        "voices": ["Sue Johnson", "Les Greenberg"],
    },
    "who-was-your-secure-base": {
        "question": "Who was a secure base for you?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "Who was a secure base for you?",
        "related": "what-a-freudian-slip-can-and-cannot-tell-us",
        "voices": ["John Bowlby", "Mary Ainsworth", "Cindy Hazan", "Phillip Shaver", "Michael Rutter"],
    },
    "why-mental-health-matters": {
        "question": "Why do so many of us wait years to get help?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "What's one thing you wish someone had told you about mental health when you were 14?",
        "related": "what-we-teach-men-about-pain",
        "voices": ["Ronald Kessler", "Philip Wang"],
    },
    "learning-to-apologize-and-move-on": {
        "question": "What did your family teach you about saying sorry?",
        "theme": "Mind and how to live",
        "kind": "Video script",
        "sit": "What did your family teach you about saying sorry?",
        "related": "the-rules-nobody-said-out-loud",
        "voices": ["John Gottman", "Ed Tronick", "Bren\u00e9 Brown", "Howard Zehr"],
    },
    "why-we-blame-the-person-instead-of-the-situation": {
        "question": "Why do we call other people jerks and ourselves just having a bad day?",
        "theme": "Mind and how to live",
        "kind": "Video script",
        "sit": "When's a time someone gave you the benefit of the doubt?",
        "related": "you-are-not-the-problem-but-the-label-might-be",
        "voices": ["Lee Ross", "John Darley", "Daniel Batson", "Joan Miller"],
    },
    "how-competition-wears-down-the-people-at-the-bottom": {
        "question": "If competition makes us better, why does it wear down the people at the bottom?",
        "theme": "Politics and civic life",
        "kind": "Video script",
        "sit": "Where in your life do you feel like you're always competing?",
        "related": "we-didnt-all-start-at-the-same-line",
        "voices": ["Herbert Spencer", "Adam Smith", "Robert Merton", "Michael Marmot", "Peter Kropotkin"],
    },
    "why-therapists-learn-cultural-humility": {
        "question": "Can you ever finish learning about someone else's culture?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "What's something you had to unlearn about another culture?",
        "related": "what-therapy-ethics-codes-miss-about-culture",
        "voices": ["Melanie Tervalon", "Jann Murray-Garc\u00eda", "Terry Cross"],
    },
    "socialism-starts-with-culture-philadelphia": {
        "question": "Can a culture get more socialist before its politics do?",
        "theme": "Politics and civic life",
        "kind": "Video script",
        "sit": "What does your block already share?",
        "related": "what-im-learning-about-third-parties",
        "voices": ["Antonio Gramsci"],
    },
    "who-raises-a-kid": {
        "question": "When a kid struggles, who should we look at?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "Which circle are you part of?",
        "related": "a-school-should-be-a-harbor",
        "voices": ["Urie Bronfenbrenner"],
    },
    "the-person-is-not-the-problem": {
        "question": "What changes when we separate a person from their problem?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "Which words do you use for people that make a hard moment sound like who they are?",
        "related": "you-are-not-the-problem-but-the-label-might-be",
        "voices": ["Michael White", "David Epston"],
    },
    "the-identified-patient": {
        "question": "What is the person we call the problem carrying for everyone else?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "Who gets called the problem in your family, school or city, and what might they be carrying?",
        "related": "you-are-not-the-problem-but-the-label-might-be",
        "voices": ["Don D. Jackson", "Virginia Satir"],
    },
    "who-gets-to-be-the-thinker": {
        "question": "Who gets to be called a thinker?",
        "theme": "Politics and civic life",
        "kind": "Video script",
        "sit": "Whose work in your community deserves more credit?",
        "related": "where-power-and-identity-cross",
        "voices": ["Antonio Gramsci", "Patricia Hill Collins"],
    },
    "intergenerational-trauma-vietnamese-americans": {
        "question": "What gets passed down when a family never had a word for it?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "What rule did your family live by?",
        "related": "love-that-showed-up-as-food",
        "voices": [],
    },
    "the-story-my-family-handed-me": {
        "question": "What would you name the story your family handed you?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "What would you name the story your family handed you?",
        "related": "love-that-showed-up-as-food",
        "voices": ["Michael White"],
    },
    "do-you-know-the-number-988": {
        "question": "What do you call when your mind is the emergency?",
        "theme": "Mental health",
        "kind": "Video script",
        "sit": "Who is one person you could tell about 988 this week?",
        "related": "what-we-teach-men-about-pain",
        "voices": [],
    },
}

# The question each episode works on, by episode slug (optional).
EPISODE_QUESTIONS = {
    "a-study-on-happiness": "What makes a life feel full?",
}

# Start here: three doors into what is already live.
DOORS = [
    ("How do I think better?", "/blog/how-great-thinkers-are-made/", "Essay", "how-great-thinkers-are-made"),
    ("What should school feel like?", "/blog/a-school-should-be-a-harbor/", "Essay", "a-school-should-be-a-harbor"),
    ("What makes a life feel full?", "/podcasts/#a-study-on-happiness", "Podcast", "a-study-on-happiness"),
]

RULES = [
    ("I try to label my opinions.", "When a piece is my view, it says so. Opinion pieces are marked on the index."),
    ("I try to link my sources.", "Facts link to where they come from. Uncertain parts are marked as uncertain."),
    ("I try to make room for disagreement.", "The strongest fair objection belongs inside the essay, not outside it."),
    ("I fix mistakes when I catch them.", "If something turns out wrong, I correct it at the top of the post, with the date and what changed."),
]

# Where I start from: ideals borrowed from Heart of the Ozarks (hoto.org), a community
# nonprofit in Springfield, Missouri. Project Hoto is not affiliated with them.
IDEALS = [
    ("Neighbors look after neighbors.", "Storms, layoffs, hunger and family crises hit whole towns at once. I start from the belief that we owe each other help when they do."),
    ("Help now, and a way forward.", "Good help meets the urgent need today and leaves people more able to run their own lives tomorrow. I try to judge policies by both."),
    ("Watch for who falls through the cracks.", "Every rule and program misses someone. I try to name who, and why."),
    ("Everyone has something to give.", "Nobody is only a receiver. A good system leaves room for people to give back, in time, skill or care."),
    ("Start local.", "Big questions land on real streets. Neighbors, local businesses, libraries, faith groups and volunteers are often the first to show up, and I want to learn from them."),
]

IDEALS_CREDIT = ('These ideals borrow from <a href="https://hoto.org/" rel="noopener">Heart of the Ozarks</a>, a community nonprofit '
                 "in Springfield, Missouri, that pairs emergency help with tools for the long run. otohay blog is not affiliated with them.")

# My background: taken only from Nick's own resume (shared 2026-11-09). Plain and humble, no hour counts or titles stacked up.
BACKGROUND = """<h2 id="background">My background</h2>
<p>Here's a little about where I've been, so you know where my opinions come from.</p>
<ul>
<li>I studied psychology at San Diego State University, with a minor in Counseling and Social Change. Now I'm working toward a master's in Marriage and Family Therapy at Alliant International University.</li>
<li>For almost two years, I worked one on one with kids and their families as a behavior interventionist at Easterseals Southern California.</li>
<li>At San Diego State, I was a teaching assistant at the Children's Center, a research assistant in a lab that studies stress and bonding, and a student representative on the psychology department's DEI committee.</li>
<li>One summer, I volunteered at a women's resource center in Malvern, Pennsylvania. I kept a list of local resources and helped connect people with shelters.</li>
<li>In 2026, I joined the Kaiser Permanente Mental Health Scholars Academy for supervised training.</li>
</ul>
<p>None of this makes me an expert. It's where I learned most of what I write about, and I'm still learning.</p>
<p>If you want the details, my full resume is on <a href="https://www.linkedin.com/in/nicholastho/" rel="noopener">LinkedIn</a>.</p>"""


# Nick's TikTok profile. A plain link only: no embed, no script, nothing loads from TikTok.
TIKTOK_URL = "https://www.tiktok.com/@hotolosophy.com"
TIKTOK_LINK = f'<a href="{TIKTOK_URL}" rel="noopener">TikTok</a>'

NAV = [("/start-here/", "Start here"), ("/blog/", "Blog"), ("/blog/archive/", "Archive"), ("/podcasts/", "Podcast"), ("/civic/", "Civic guide"),
       ("/how-i-argue/", "About")]
# The phone menu has room for more: everything the homepage buttons reach, minus the subject pages
# (the archive lists those at the top).
MENU = [("/start-here/", "Start here, 7 steps"), ("/where-do-you-stand/", "Where do you stand?"),
        ("/blog/", "Blog"), ("/blog/archive/", "Archive"), ("/series/therapy-school/", "Therapy school series"),
        ("/social-location/", "Map your social location"), ("/philly/", "Get organized in Philly"),
        ("/reading-circle/", "Start a reading circle"), ("/reading-list/", "Reading list"), ("/podcasts/", "Podcast"), ("/civic/", "Civic guide"),
        ("/how-i-argue/", "About")]

BLUNT = ("<strong>Heads up: I write bluntly.</strong> If a post brings up something heavy, it's okay to stop reading.")

UNOFFICIAL = ("<strong>Independent and unofficial.</strong> otohay blog is a personal project. It is not affiliated with, "
              "endorsed by, or paid for by any politician, campaign, party, or political committee. "
              "Essays are opinion. Sourced claims are linked where they appear.")

# The site's stand, said plainly on every page (Nick, 2026-11-11: a dissident blog, no single politician).
BANNER = "Against the rich running everything. For people sharing what they have."
STAND_FOOT = "otohay blog is a dissident blog by Nick. Unpaid commentary. No donations, no sponsors, and no politician to follow. I speak only for myself, not for any group I belong to or link to."
STAND = ('<aside class="where-i-stand" aria-labelledby="stand-h"><p class="label" id="stand-h">Where I stand</p>'
         "<p>I side with workers, renters and neighbors over the people who profit from them, and I write from there. "
         "I don't follow any one politician. I'm against antisemitism, and against AIPAC's money in our elections.</p>"
         "<p>I could be wrong, so read the other side's best case too.</p>"
         '<p class="actions"><a class="cta" href="/start-here/">Next step: start here</a></p></aside>')

TEACHERS = "Most of these ideas aren't mine. I'm passing on what I learned from my professors at San Diego State."


# Related reading: picked offline with the open model sentence-transformers/all-MiniLM-L6-v2 (title, summary and
# first 250 words of each essay, cosine similarity), then filtered to matches scoring 0.30 or more. No code runs for visitors.
RELATED = {
    "what-the-panthers-and-king-both-saw-about-poverty": [
        "social-location-where-you-stand",
        "we-didnt-all-start-at-the-same-line",
        "one-roll-of-toilet-paper"
    ],
    "where-power-and-identity-cross": [
        "social-location-where-you-stand",
        "you-are-not-the-problem-but-the-label-might-be",
        "we-didnt-all-start-at-the-same-line"
    ],
    "the-rules-nobody-said-out-loud": [
        "love-that-showed-up-as-food",
        "we-didnt-all-start-at-the-same-line",
        "what-we-teach-men-about-pain"
    ],
    "what-therapy-ethics-codes-miss-about-culture": [
        "what-we-teach-men-about-pain",
        "what-a-freudian-slip-can-and-cannot-tell-us",
        "we-didnt-all-start-at-the-same-line"
    ],
    "is-there-a-perfect-income": [
        "a-rest-from-happiness",
        "we-didnt-all-start-at-the-same-line",
        "what-we-teach-men-about-pain"
    ],
    "love-that-showed-up-as-food": [
        "the-rules-nobody-said-out-loud",
        "social-location-where-you-stand",
        "we-didnt-all-start-at-the-same-line"
    ],
    "privilege-is-everything-you-never-had-to-think-about": [
        "we-didnt-all-start-at-the-same-line",
        "when-watching-students-becomes-the-lesson",
        "one-roll-of-toilet-paper"
    ],
    "one-roll-of-toilet-paper": [
        "we-didnt-all-start-at-the-same-line",
        "a-school-should-be-a-harbor",
        "privilege-is-everything-you-never-had-to-think-about"
    ],
    "the-i-am-poem-who-we-say-we-are": [
        "social-location-where-you-stand",
        "how-great-thinkers-are-made"
    ],
    "we-didnt-all-start-at-the-same-line": [
        "privilege-is-everything-you-never-had-to-think-about",
        "social-location-where-you-stand",
        "is-there-a-perfect-income"
    ],
    "social-location-where-you-stand": [
        "we-didnt-all-start-at-the-same-line",
        "the-i-am-poem-who-we-say-we-are"
    ],
    "what-a-freudian-slip-can-and-cannot-tell-us": [
        "the-rules-nobody-said-out-loud",
        "what-we-teach-men-about-pain",
        "how-great-thinkers-are-made"
    ],
    "what-arendt-meant-by-the-banality-of-evil": [
        "how-great-thinkers-are-made",
        "what-a-freudian-slip-can-and-cannot-tell-us"
    ],
    "what-we-teach-men-about-pain": [
        "the-rules-nobody-said-out-loud",
        "we-didnt-all-start-at-the-same-line",
        "what-therapy-ethics-codes-miss-about-culture"
    ],
    "fearless-speech-for-regular-people": [
        "you-are-not-the-problem-but-the-label-might-be",
        "what-a-freudian-slip-can-and-cannot-tell-us",
        "the-rules-nobody-said-out-loud"
    ],
    "you-are-not-the-problem-but-the-label-might-be": [
        "how-great-thinkers-are-made",
        "fearless-speech-for-regular-people",
        "what-a-freudian-slip-can-and-cannot-tell-us"
    ],
    "the-watcher-in-your-pocket": [
        "when-watching-students-becomes-the-lesson",
        "how-great-thinkers-are-made"
    ],
    "when-watching-students-becomes-the-lesson": [
        "a-school-should-be-a-harbor",
        "the-watcher-in-your-pocket",
        "privilege-is-everything-you-never-had-to-think-about"
    ],
    "a-school-should-be-a-harbor": [
        "when-watching-students-becomes-the-lesson",
        "the-rules-nobody-said-out-loud",
        "one-roll-of-toilet-paper"
    ],
    "a-most-agreeable-war": [
        "how-great-thinkers-are-made"
    ],
    "a-rest-from-happiness": [
        "is-there-a-perfect-income",
        "what-we-teach-men-about-pain"
    ],
    "how-great-thinkers-are-made": [
        "you-are-not-the-problem-but-the-label-might-be",
        "what-arendt-meant-by-the-banality-of-evil",
        "what-a-freudian-slip-can-and-cannot-tell-us"
    ]
}


def esc(s):
    return html.escape(s, quote=True)


def q(text):
    """Escape a question."""
    return esc(text)


def sc(text):
    """Class for labels longer than two words: they read as sentence case; shorter ones stay uppercase."""
    return " sc" if len(text.split()) > 2 else ""


def kind_badge(kind):
    """Type label coded by shape as well as words: Opinion is filled, Sourced explainer is boxed, Essay has a square bullet."""
    cls = {"Opinion": "opinion", "Sourced explainer": "sourced"}.get(kind, "essay")
    label = {"Video script": "From my videos"}.get(kind, kind)
    return f'<span class="kind kind-{cls}">{esc(label)}</span>'


# Planet Hoto: one small planet mark for the header and footer, lit blue on the day side and red on the dusk side.
# Decorative only (aria-hidden), so screen readers hear the same names as before.
GLYPH = ('<svg class="glyph" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
         '<circle class="g-body" cx="12" cy="12" r="9"/>'
         '<path class="g-day" d="M12 3a9 9 0 0 0 0 18"/><path class="g-dusk" d="M12 3a9 9 0 0 1 0 18"/></svg>')

# Nick's own hand-drawn face logo, used in the header next to the name. Made from his ink drawing
# (black ink on a white disk so it reads on light and dark). Decorative: the link already has a name.
LOGO = '<img class="logo" src="/logo.png" width="36" height="36" alt="">'

# The hero horizon: the top of one large planet, seen from orbit, with a thin orbit and a small moon.
# It sits below the hero text, never behind it. Colors come from the --planet-* tokens in site.css.
HORIZON = """<div class="horizon" aria-hidden="true">
<svg viewBox="0 0 1200 260" focusable="false">
<defs>
<linearGradient id="ph-rim" x1="0" x2="1" y1="0" y2="0"><stop offset="0" class="s-day"/><stop offset=".42" class="s-day s-fade"/><stop offset=".58" class="s-dusk s-fade"/><stop offset="1" class="s-dusk"/></linearGradient>
<linearGradient id="ph-body" x1="0" x2="0" y1="0" y2="1"><stop offset="0" class="s-top"/><stop offset="1" class="s-bottom"/></linearGradient>
</defs>
<g class="stars"><circle cx="140" cy="62" r="1.6"/><circle cx="250" cy="150" r="1.2"/><circle cx="470" cy="28" r="1.4"/><circle cx="742" cy="60" r="1.2"/><circle cx="1012" cy="34" r="1.6"/><circle cx="1120" cy="150" r="1.2"/></g>
<path class="orbit" d="M40 230Q600-190 1160 230"/>
<path class="body" d="M28 260A1000 1000 0 0 1 1172 260Z"/>
<path class="halo" d="M28 260A1000 1000 0 0 1 1172 260"/>
<path class="rim" d="M28 260A1000 1000 0 0 1 1172 260"/>
<path class="lat" d="M200 260Q600 172 1000 260"/>
<circle class="moon" cx="914" cy="86" r="6"/>
</svg>
</div>"""


def site_header(path):
    """The shared desktop and phone header, used by page() and by the standalone civic guide."""
    def cur(href):
        # Writing covers the front page, /blog/ and every post; the others cover their own section.
        if href == "/blog/":
            on = (path.startswith("/blog/") and not path.startswith("/blog/archive/")) or path == "/"
        else:
            on = path.startswith(href)
        return ' aria-current="page"' if on else ""

    links = "".join(f'<a href="{href}"{cur(href)}>{label}</a>' for href, label in NAV)
    menu_links = "".join(f'<a href="{href}"{cur(href)}>{label}</a>' for href, label in MENU)
    return (f'<header class="top">\n'
            f'<a class="wordmark" href="/" aria-label="otohay blog, a dissident blog, home">{LOGO}<span class="wm-text"><span class="wm-name">otohay <span>blog</span></span><small class="stamp">a dissident blog</small></span></a>\n'
            f'<nav class="main nav-wide" aria-label="Main">{links}</nav>\n'
            f'<details class="menu"><summary>Menu</summary><nav class="nav-menu" aria-label="Main">{menu_links}</nav></details>\n'
            f'</header>')


SITE_URL = "https://hoto.lol"
# Pages search engines may list. The civic guide and voting demo are standalone pages with their
# own "noindex" tag and are never listed; the 404 page is noindex too.
NOINDEX_PATHS = {"/404"}


def canonical(path):
    """The one full address search engines should use. The home page and /blog/ are the same page."""
    return SITE_URL + ("/blog/" if path == "/" else path)


SHARE_IMAGE = "/share.png"  # made by scripts/make_share_image.py, 1200 x 630
SHARE_ALT = "otohay blog, hoto.lol, next to Nick's hand-drawn ink logo, in black and white"


def share_tags(path, title, description, published=None):
    """Link preview tags (Open Graph and social cards) for pages search engines may list.
    They only describe the page; nothing here loads from another site."""
    og_title = SITE if title is None else title
    tags = [
        ("property", "og:site_name", SITE),
        ("property", "og:type", "article" if published else "website"),
        ("property", "og:title", og_title),
        ("property", "og:description", description),
        ("property", "og:url", canonical(path)),
        ("property", "og:image", SITE_URL + SHARE_IMAGE),
        ("property", "og:image:width", "1200"),
        ("property", "og:image:height", "630"),
        ("property", "og:image:alt", SHARE_ALT),
        ("property", "og:locale", "en_US"),
    ]
    if published:
        tags += [("property", "article:published_time", published)]
    tags.append(("name", "twitter:card", "summary_large_image"))
    return "".join(f'<meta {k}="{v}" content="{esc(c)}">\n' for k, v, c in tags)


def page(path, title, description, body, script="", published=None):
    hidden = path in NOINDEX_PATHS
    robots = "noindex, nofollow" if hidden else "index, follow"
    canon = "" if hidden else f'<link rel="canonical" href="{canonical(path)}">\n' + share_tags(path, title, description, published)
    foot_nav = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    full_title = "otohay blog" if title is None else f"{title} · {SITE}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="{robots}">
{canon}<link rel="alternate" type="application/rss+xml" title="{SITE}" href="/feed.xml">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-adsense-account" content="ca-pub-2462240112532447">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0b0b0b" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{CSS_LINK}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="crisis" aria-label="Crisis help">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</aside>
{site_header(path)}
<aside class="stand-banner" aria-label="Where this blog stands">{BANNER}</aside>
<main id="main" tabindex="-1">
{body}
</main>
<footer>
<div class="foot-top">
<p class="foot-mark">{GLYPH}Thanks for reading. Nick</p>
<nav aria-label="Footer">{foot_nav}</nav>
<p class="foot-follow">See every post in the <a href="/blog/archive/">archive</a>. Follow along on {TIKTOK_LINK} or the <a href="/feed.xml">RSS feed</a>.</p>
</div>
<div class="foot-fine">
<p>{STAND_FOOT}</p>
<p>Independent and unofficial. Not affiliated with any politician, party or campaign.</p>
<p>{TEACHERS}</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p>This site currently shows no ads. <a href="/privacy/">Privacy</a>.</p>
</div>
</footer>
{script}
</body>
</html>
"""


POST_BODIES = []  # essay bodies as written into pages; they are the author's text and are exempt from the em dash check


def write(rel, text):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def nice(d):
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m) - 1]} {int(dd)}, {y}"


def balance_sections(html):
    """Some post files carry a closing </section> with no opening tag, and leave the
    sources section open. Drop unmatched closers and close anything left open, so the
    page nests cleanly. The post text itself is never changed."""
    out, depth, pos = [], 0, 0
    for m in re.finditer(r"<(/?)section\b[^>]*>", html):
        out.append(html[pos:m.start()])
        if m.group(1):
            if depth:
                depth -= 1
                out.append(m.group(0))
        else:
            depth += 1
            out.append(m.group(0))
        pos = m.end()
    out.append(html[pos:])
    return "".join(out).rstrip() + "\n" + "</section>\n" * depth


def body_of(slug):
    return balance_sections((ROOT / "content" / "posts" / f"{slug}.html").read_text(encoding="utf-8"))


def minutes(slug):
    """Reading time for the essay text, not counting the sources list."""
    text = body_of(slug).split('id="sources"')[0]
    words = len(re.sub(r"<[^>]+>", " ", html.unescape(text)).split())
    return max(1, math.ceil(words / 230))


def post(slug):
    return next(p for p in POSTS if p["slug"] == slug)


def frame(slug):
    """Framing for a post. Posts added without framing still build."""
    return {"question": None, "theme": THEMES[-1], "kind": "Essay", "sit": None, "related": None, "voices": [],
            "note": "", "corrections": [], **FRAMING.get(slug, {})}


def latest_row(p):
    f = frame(p["slug"])
    return (f'<li class="row"><div class="row-meta">{kind_badge(f["kind"])}<span>{esc(f["theme"])}</span>'
            f'<time datetime="{p["date"]}">{nice(p["date"])}</time><span>{minutes(p["slug"])} min read</span></div>'
            f'<h3 class="row-title"><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a></h3>'
            f'<p class="row-sum">{esc(p["summary"])}</p></li>')


def archive_row(p):
    f = frame(p["slug"])
    return (f'<li class="arow"><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a>'
            f'<span class="row-meta">{kind_badge(f["kind"])}<time datetime="{p["date"]}">{nice(p["date"])}</time></span></li>')


def subject_path(theme):
    return f"/topics/{slugify(theme)}/"


def archive_page():
    """Every post on one page, newest first, grouped by year, like the archive on most blogs."""
    by_year = {}
    for p in sorted(POSTS, key=lambda p: p["date"], reverse=True):
        by_year.setdefault(p["date"][:4], []).append(p)
    years = "".join(f'<section class="section" aria-labelledby="y{y}"><h2 id="y{y}">{y}</h2>'
                    f'<ul class="alist">{"".join(archive_row(p) for p in ps)}</ul></section>'
                    for y, ps in by_year.items())
    chips = [(subject_path(t), t) for t in THEMES] + [(SERIES_PATH, "Therapy school series")]
    chips += [(f"#y{y}", y) for y in by_year] if len(by_year) > 1 else []
    jump = ('<nav class="btn-grid archive-jump" aria-label="Jump to a subject">'
            + "".join(f'<a class="btn" href="{h}">{esc(t)}</a>' for h, t in chips) + '</nav>')
    return simple(None, "Archive", f"All {len(POSTS)} posts, newest first.", jump + years + subject_links())


# A series: posts meant to be read in order. Each part shows "Part X of Y" and Next / Previous,
# and the series has its own page. Order follows the video episodes; edit "parts" to change it.
SERIES = {
    "slug": "therapy-school",
    "title": "Things therapy school taught me about society",
    "lede": "Scripts from my video series, in order. Each one is something I learned in my marriage and family therapy program.",
    "parts": [
        "the-identified-patient",
        "the-person-is-not-the-problem",
        "who-raises-a-kid",
        "why-therapists-learn-cultural-humility",
        "why-so-many-of-us-feel-lonely",
        "how-competition-wears-down-the-people-at-the-bottom",
        "why-we-blame-the-person-instead-of-the-situation",
        "what-fights-are-really-asking",
        "who-was-your-secure-base",
    ],
}
SERIES_PATH = f"/series/{SERIES['slug']}/"


def series_page():
    rows = "".join(f'<li class="arow"><span class="part-no">Part {i}</span><a href="/blog/{s}/">{esc(post(s)["title"])}</a>'
                   f'<span class="row-meta">{minutes(s)} min read</span></li>'
                   for i, s in enumerate(SERIES["parts"], 1))
    return simple("Series", esc(SERIES["title"]), f'{esc(SERIES["lede"])} {len(SERIES["parts"])} parts.',
                  f'<nav class="btn-grid series-start" aria-label="Start the series"><a class="btn btn-main" href="/blog/{SERIES["parts"][0]}/">Start with Part 1</a>'
                  f'<a class="btn" href="/blog/{SERIES["parts"][-1]}/">Newest part</a></nav>'
                  f'<ol class="alist series-list">{rows}</ol>' + subject_links())


def series_bits(slug):
    """For a post in the series: the "Part X of Y" line for the header and the Next / Previous nav."""
    parts = SERIES["parts"]
    if slug not in parts:
        return "", ""
    i = parts.index(slug)
    line = (f'<p class="series-line">Part {i + 1} of {len(parts)} in '
            f'<a href="{SERIES_PATH}">{esc(SERIES["title"])}</a></p>')
    links = []
    if i > 0:
        links.append(f'<a class="series-prev" href="/blog/{parts[i - 1]}/"><span class="label">Previous, part {i}</span>'
                     f'<span class="series-t">{esc(post(parts[i - 1])["title"])}</span></a>')
    if i + 1 < len(parts):
        links.append(f'<a class="series-next" href="/blog/{parts[i + 1]}/"><span class="label">Next, part {i + 2}</span>'
                     f'<span class="series-t">{esc(post(parts[i + 1])["title"])}</span></a>')
    nav = f'<nav class="series-nav" aria-label="More in this series">{"".join(links)}</nav>'
    return line, nav


def subject_links(current=None):
    links = "".join(f'<li><a href="{subject_path(t)}">{esc(t)}</a></li>' for t in THEMES if t != current)
    head = "Other subjects" if current else "Browse by subject"
    links += f'<li><a href="{SERIES_PATH}">Series: Things therapy school taught me</a></li>'
    return (f'<nav class="subjects" aria-labelledby="subj-h"><h2 id="subj-h">{head}</h2><ul>{links}</ul>'
            f'<p><a href="/blog/archive/">See every post in the archive</a></p></nav>')


def subject_page(theme):
    items = sorted((p for p in POSTS if frame(p["slug"])["theme"] == theme), key=lambda p: p["date"], reverse=True)
    n = len(items)
    return simple("Subject", esc(theme), f"{n} post{'s' if n != 1 else ''}, newest first.",
                  f'<ul class="alist">{"".join(archive_row(p) for p in items)}</ul>' + subject_links(theme))


LATEST_ON_HOME = 8


def front_page():
    doors = []
    for question, href, kind, slug in DOORS:
        if kind == "Podcast":
            e = next(x for x in EPISODES if x["slug"] == slug)
            meta, name = f"Podcast · {esc(e['length'])}", esc(e["title"])
        else:
            meta, name = f"{kind_badge(kind)}{minutes(slug)} min read", esc(post(slug)["title"])
        doors.append(f'<li class="door"><a href="{href}"><h3 class="door-q">{q(question)}</h3>'
                     f'<span class="door-meta">{meta}<b>{name}</b></span></a></li>')

    newest = sorted(POSTS, key=lambda p: p["date"], reverse=True)
    lead = newest[0]
    featured = (f'<article class="featured" aria-labelledby="feat-h"><p class="label">Newest</p>'
                f'<h3 id="feat-h" class="feat-q"><a href="/blog/{lead["slug"]}/">{esc(lead["title"])}</a></h3>'
                f'<p class="feat-s">{esc(lead["summary"])}</p>'
                f'<p class="feat-meta">{minutes(lead["slug"])} min read · <span aria-hidden="true">Read the post →</span></p></article>')
    latest = "".join(latest_row(p) for p in newest[1:LATEST_ON_HOME])
    subjects = "".join(f'<li><a href="{subject_path(t)}">{esc(t)} ({sum(frame(p["slug"])["theme"] == t for p in POSTS)})</a></li>'
                       for t in THEMES)
    subjects += f'<li><a href="/blog/archive/">All posts ({len(POSTS)})</a></li>'
    subjects += f'<li><a href="{SERIES_PATH}">Series: Things therapy school taught me ({len(SERIES["parts"])})</a></li>'

    btns = [(f'/blog/{lead["slug"]}/', "Read the newest post", True), ("/blog/archive/", f"All {len(POSTS)} posts", True)]
    btns += [(subject_path(t), t, False) for t in THEMES]
    btns += [("/start-here/", "Start here, 7 steps", False), (SERIES_PATH, "Therapy school series", False),
             ("/social-location/", "Map your social location", False),
             ("/philly/", "Get organized in Philly", False), ("/civic/", "Civic guide", False),
             ("/podcasts/", "Podcasts", False), ("/how-i-argue/", "About", False), ("/feed.xml", "Follow by RSS", False)]
    buttons = "\n".join(f'<a class="btn{" btn-main" if main else ""}" href="{h}">{esc(t)}</a>' for h, t, main in btns)

    # Like most blogs: a short hello, then the newest writing on the first screen. The full lists
    # live on /blog/archive/ and the subject pages; the planet and the notice close the page.
    return f"""<div class="frame">
<section class="hero" aria-labelledby="hero-h">
<div class="hero-text">
<h1 id="hero-h">A blog for the people who do the work.</h1>
<p class="lede">What therapy school is teaching me about people, what money and power do to our heads, and what we can build together instead. Short posts from my TikTok videos, plus longer essays.</p>
{WS.HOME_ASK}
<nav class="btn-grid" aria-label="Jump in">
{buttons}
</nav>
</div>
</section>

<div class="index-grid">
<div class="index-main">
<section class="section" id="latest" aria-labelledby="latest-h">
<div class="section-head"><h2 id="latest-h">Latest writing</h2><a class="jump" href="/blog/archive/">See all {len(POSTS)} posts</a></div>
{featured}
<ul class="rows">{latest}</ul>
<p class="more-row"><a class="more" href="/blog/archive/">See every post in the archive</a></p>
<p class="aside-note">{BLUNT}</p>
</section>

</div>
<aside class="index-side" aria-labelledby="side-h">
<h2 id="side-h">Browse by subject</h2>
<ul>{subjects}</ul>
</aside>
</div>

<div class="index-main">
<section class="section" id="start" aria-labelledby="start-h">
<div class="section-head"><h2 id="start-h">Start here</h2><p>These are the three I'd read first.</p></div>
<ul class="doors">{"".join(doors)}</ul>
<p class="civic-callout">Or try the civic guide, <a href="/civic/">Where do my political views sit?</a> Seven policy areas, no labels, no voting advice. Your answers never leave your device.</p>
</section>

<section class="section" id="about" aria-labelledby="about-h">
<div class="section-head"><h2 id="about-h">About</h2></div>
<ul class="about">
<li><a href="/how-i-argue/#ideals"><span class="about-t">Where I start from</span></a></li>
<li><a href="/how-i-argue/"><span class="about-t">About this blog</span></a></li>
</ul>
</section>
</div>
{HORIZON}
</div>
"""


def slugify(text):
    t = re.sub(r"<[^>]+>", "", html.unescape(text)).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "part"


def with_outline(body):
    """Give each h2 an id and return (body, outline items). The source files stay untouched."""
    items, seen = [], set(re.findall(r'id="([^"]+)"', body))

    def tag(m):
        attrs, inner = m.group(1), m.group(2)
        if "id=" in attrs:
            hid = re.search(r'id="([^"]+)"', attrs).group(1)
        else:
            hid = base = slugify(inner)
            n = 2
            while hid in seen:
                hid, n = f"{base}-{n}", n + 1
            attrs = f'{attrs} id="{hid}"'
        seen.add(hid)
        items.append((hid, html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()))
        return f"<h2{attrs}>{inner}</h2>"

    return re.sub(r"<h2([^>]*)>(.*?)</h2>", tag, body, flags=re.S), items


def narration(p):
    """Player for an essay's AI voice file.

    Nick's own ElevenLabs voice clone wins when audio/<slug>.mp3 exists; otherwise the Kokoro
    file audio/<slug>.opus made by scripts/make_audio.py. No player when neither exists."""
    slug = p["slug"]
    if (OUT / "audio" / f"{slug}.mp3").is_file():
        src, kind = f"/audio/{slug}.mp3", "audio/mpeg"
        label = "Listen · AI clone of my own voice (ElevenLabs)"
    elif (OUT / "audio" / f"{slug}.opus").is_file():
        src, kind = f"/audio/{slug}.opus", "audio/ogg; codecs=opus"
        label = "Listen · AI-generated voice (Kokoro)"
    else:
        return ""
    return (f'<section class="narration" aria-label="Listen to this essay">'
            f'<p class="label sc">{label}</p>'
            f'<div class="player"><audio controls preload="none" aria-label="Listen to: {esc(p["title"])}">'
            f'<source src="{src}" type="{kind}">'
            f'Your browser cannot play this audio. The full text is below.</audio></div></section>')


# A short "written by" card at the end of every post, like the author box on Substack or
# LinkedIn articles. The words come from the home page intro Nick approved.
AUTHOR_CARD = ('<aside class="author-card" aria-labelledby="author-h">'
               '<span class="avatar avatar-lg" aria-hidden="true">N</span>'
               '<div><p class="label" id="author-h">Written by Nick</p>'
               '<p class="author-bio">I\'m a Vietnamese American grad student training to be a marriage and family therapist. '
               'I write about the things in our society that frustrate me, why they might be that way, and what could help.</p>'
               '<p class="author-more"><a href="/how-i-argue/">More about me</a></p>'
               f'<p class="author-more"><a href="{TIKTOK_URL}" rel="noopener">Watch my videos on TikTok</a></p></div></aside>')


def echoes_title(title, question):
    """True when the framing question nearly repeats the post title (for example
    "Why so many of us feel lonely" and "Why do so many of us feel lonely?")."""
    words = lambda s: re.sub(r"[^a-z ]", "", s.lower()).split()
    return difflib.SequenceMatcher(None, words(title), words(question)).ratio() >= 0.8


def teaser(question, title):
    """A link's text in "Read next" and "Related reading": the question, then the title under it,
    or the title alone when the question only says the title again."""
    if question == title or echoes_title(title, question):
        return f'<span class="q-text">{esc(title)}</span>'
    return f'<span class="q-text">{q(question)}</span><cite>{esc(title)}</cite>'


def older_newer(slug):
    """Older / Newer post links at the end of a post, by date. Series parts already get
    Previous / Next in series order, so they skip this."""
    if slug in SERIES["parts"]:
        return ""
    order = sorted(POSTS, key=lambda p: p["date"])  # stable, so same-day posts keep their POSTS order
    i = next(n for n, p in enumerate(order) if p["slug"] == slug)
    links = []
    if i > 0:
        o = order[i - 1]
        links.append(f'<a class="series-prev" href="/blog/{o["slug"]}/"><span class="label">← Older post</span>'
                     f'<span class="series-t">{esc(o["title"])}</span></a>')
    if i + 1 < len(order):
        n = order[i + 1]
        links.append(f'<a class="series-next" href="/blog/{n["slug"]}/"><span class="label">Newer post →</span>'
                     f'<span class="series-t">{esc(n["title"])}</span></a>')
    return f'<nav class="series-nav post-nav" aria-label="Older and newer posts">{"".join(links)}</nav>'


def essay_page(p):
    f = frame(p["slug"])
    slug = p["slug"]
    # The framing question sits under the title, unless it only says the title again.
    question = (f'<p class="essay-q">{q(f["question"])}</p>'
                if f["question"] and not echoes_title(p["title"], f["question"]) else "")
    voices = (f'<p class="voices">Ideas from <b>{esc(", ".join(f["voices"]))}</b></p>' if f["voices"] else "")
    corrections = ""
    if f["corrections"]:
        items = "".join(f'<li><time datetime="{d}">{nice(d)}</time>: {esc(t)}</li>' for d, t in f["corrections"])
        corrections = f'<div class="corrections"><p class="label">Corrections</p><ul>{items}</ul></div>'
    after = []
    if f["sit"]:
        after.append(f'<aside class="sit-with" aria-labelledby="sit-h"><svg class="bulb" viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.2h5c0-.9.4-1.7 1.1-2.2A6 6 0 0 0 12 3z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg><p class="label sc" id="sit-h">Sit with this</p>'
                     f'<p class="sit-q">{q(f["sit"])}</p></aside>')
    if f["related"]:
        r = post(f["related"])
        rq = frame(r["slug"])["question"] or r["title"]
        after.append(f'<nav class="read-next" aria-label="Read next"><p class="label">Read next</p>'
                     f'<a href="/blog/{r["slug"]}/">{teaser(rq, r["title"])}</a></nav>')
    rel = [s for s in RELATED.get(slug, []) if s != f["related"]]
    if rel:
        links = "".join(f'<a href="/blog/{s}/">{teaser(frame(s)["question"] or post(s)["title"], post(s)["title"])}</a>'
                        for s in rel)
        after.append(f'<nav class="read-next" aria-label="Related reading"><p class="label">Related reading</p>{links}'
                     f'<p class="aside-note">Matches picked with an open AI model that compares the essays\' text, not by a person.</p></nav>')
    series_line, series_nav = series_bits(slug)
    if series_nav:
        after.insert(0, series_nav)
    after.append(AUTHOR_CARD)
    after.append(older_newer(slug))
    after.append(STAND)
    body, parts = with_outline(body_of(slug))
    POST_BODIES.append(body)
    toc_phone = toc_wide = ""
    if len(parts) >= 3:
        links = "".join(f'<li><a href="#{hid}">{html.escape(text)}</a></li>' for hid, text in parts)
        # Headings that already carry their own number ("1. A school should be a harbor") skip the
        # list's counter, so a number never shows twice.
        ol = '<ol class="own-numbers">' if any(re.match(r"\d+[.)]\s", t) for _, t in parts) else "<ol>"
        toc_phone = (f'<details class="toc-phone"><summary>In this post <span class="toc-count">· {len(parts)} sections</span>'
                     f'</summary>{ol}{links}</ol></details>')
        toc_wide = f'<nav class="toc-wide" aria-label="In this post"><p class="toc-title">In this post</p>{ol}{links}</ol></nav>'

    return f"""<article class="essay">
<header class="essay-head">
<a class="back" href="/blog/">← All writing</a>
<p class="label essay-kind{sc(f["theme"])}"><a href="{subject_path(f["theme"])}">{esc(f["theme"])}</a>{kind_badge(f["kind"])}</p>
<h1>{esc(p['title'])}</h1>
{question}
<div class="byline"><span class="avatar" aria-hidden="true">N</span><p class="byline-text"><span class="byline-name">By Nick</span><span class="essay-meta"><time datetime="{p['date']}">{nice(p['date'])}</time> · {minutes(slug)} min read</span></p></div>
{voices}
{corrections}
{series_line}
{toc_phone}{narration(p)}
</header>
<div class="essay-body">
<div class="prose">
{body}
</div>
{toc_wide}
</div>
<div class="after">
{"".join(after)}
<p class="essay-end"><a class="back" href="#main">↑ Back to top</a><a class="back" href="/blog/">← All writing</a><a class="back" href="/how-i-argue/">About</a></p>
</div>
</article>
"""


def episode_card(e, full=True):
    overview = ""
    if full and e["overview"]:
        paras = "".join(f"<p>{esc(x)}</p>" for x in e["overview"])
        overview = f"<details><summary>Read the episode overview</summary>{paras}</details>"
    # Every episode is hosted on this site (podcasts/). Outside players such as Speechify are not used.
    assert e["audio"].startswith("/podcasts/") and (ROOT / e["audio"].lstrip("/")).is_file(), f"episode audio missing: {e['slug']}"
    player = f"""<div class="player"><audio controls preload="none" src="{e['audio']}" aria-label="{esc(e['title'])}"></audio></div>"""
    note = f'<p class="meta">{esc(e["note"])}</p>' if e.get("note") else ""
    question = EPISODE_QUESTIONS.get(e["slug"])
    asks = f'<p class="label">The question</p><p class="ep-q">{q(question)}</p>' if question else ""
    return f"""<section class="episode" id="{e['slug']}" aria-labelledby="{e['slug']}-h">
{asks}
<h2 id="{e['slug']}-h">{esc(e['title'])}</h2>
<p class="meta"><time datetime="{e['date']}">{nice(e['date'])}</time>{' · ' + e['length'] if e.get('length') else ''}</p>
<p>{esc(e['summary'])}</p>
{player}{note}
{overview}
</section>"""


def simple(kicker, h1, lede, inner):
    k = f'<p class="kicker{sc(kicker)}">{kicker}</p>' if kicker else ""
    l = f'<p class="lede">{lede}</p>' if lede else ""
    return f"""<div class="page">
<header class="page-head">{k}<h1>{h1}</h1>{l}</header>
<div class="page-body">
{inner}
</div>
</div>
"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "site.css", OUT / "site.css")
    shutil.copy(ROOT / "favicon.svg", OUT / "favicon.svg")
    shutil.copy(ROOT / "share.png", OUT / "share.png")
    shutil.copy(ROOT / "logo.png", OUT / "logo.png")
    shutil.copy(ROOT / "apple-touch-icon.png", OUT / "apple-touch-icon.png")
    shutil.copytree(ROOT / "podcasts", OUT / "podcasts")
    if (ROOT / "audio").is_dir():  # essay narrations made by scripts/make_audio.py
        shutil.copytree(ROOT / "audio", OUT / "audio")
    shutil.copytree(ROOT / "fonts", OUT / "fonts")
    # Printable handouts (PDF worksheets), served from this site only.
    shutil.copytree(ROOT / "handouts", OUT / "handouts")
    (OUT / "CNAME").write_text("hoto.lol\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "ads.txt").write_text("google.com, pub-2462240112532447, DIRECT, f08c47fec0942fa0\n")
    # Search engines may crawl the site. The civic guide and voting demo stay out of search
    # through their own "noindex" tag (crawlers must be allowed in to read it), and are left
    # out of the sitemap.
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

    for slug, f in FRAMING.items():
        assert any(p["slug"] == slug for p in POSTS), f"framing for unknown post {slug}"
        assert f["theme"] in THEMES, f"unknown theme for {slug}"
        assert not f.get("related") or any(p["slug"] == f["related"] for p in POSTS), f"bad related link in {slug}"

    desc = "Nick's blog about mental health, family, and fairness, from a therapy student who's still learning."
    # The home page and /blog/ are the same front page. hoto.lol/ currently redirects to /blog/.
    write("index.html", page("/", None, desc, front_page()))
    write("blog/index.html", page("/blog/", "Writing", desc, front_page()))

    for p in POSTS:
        write(f"blog/{p['slug']}/index.html", page(f"/blog/{p['slug']}/", p["title"], p["summary"], essay_page(p), published=p["date"]))
    assert all(any(p["slug"] == x for p in POSTS) for x in SERIES["parts"]), "series lists an unknown post"
    write(SERIES_PATH.lstrip("/") + "index.html", page(SERIES_PATH, SERIES["title"], SERIES["lede"], series_page()))
    write("blog/archive/index.html", page("/blog/archive/", "Archive", f"Every post on otohay blog, newest first, grouped by year.", archive_page()))
    for t in THEMES:
        write(subject_path(t).lstrip("/") + "index.html",
              page(subject_path(t), t, f"Every otohay blog post about {t.lower()}, newest first.", subject_page(t)))

    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcast", "Podcast episodes: thinking out loud about hard questions.", simple(
        "otohay blog podcast", "Podcast",
        "These episodes are my reflections on the same questions I write about. They're my opinion, and they aren't therapy. Nothing plays until you press Play. "
        "Every essay also has its own Listen player at the top of the page.",
        cards)))

    rules = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in RULES)
    ideals = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in IDEALS)
    write("how-i-argue/index.html", page("/how-i-argue/", "About this blog", "What this blog is and a few things I try to do here.", simple(
        "About", "About this blog",
        "I'm Nick. This is my personal blog, where I share what I care about in social justice and what I've learned in school. Most of it is my opinion.",
        f"""{BACKGROUND}
<h2 id="ideals">Where I start from</h2>
<p>These are a few beliefs I keep coming back to. I borrowed them from a community nonprofit I look up to.</p>
<div class="rules-page">{ideals}</div>
<p>{IDEALS_CREDIT}</p>
<h2>A few things I try to do</h2>
<div class="rules-page">{rules}</div>
<h2>Try it yourself</h2>
<p>The same votes can produce different winners under different counting rules. <a href="/vote/">See how with made-up ballots</a>.</p>
<h2 id="philly">In Philly?</h2>
<p>I put together a list of <a href="/philly/">places to get organized in Philadelphia</a>, from block captains to tenant unions.</p>
<h2>What this is not</h2>
<p>{UNOFFICIAL}</p>
<p>{TEACHERS}</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p class="aside-note">{BLUNT}</p>
<h2 id="contact">Contact</h2>
<p>You can reach me at <a href="mailto:1000hoto1000@gmail.com">1000hoto1000@gmail.com</a>. I read everything, but I may be slow to reply. If you're in crisis, please call or text 988 instead.</p>
<p>I also make short videos about what I'm learning in therapy school. You can watch them on {TIKTOK_LINK}.</p>
<p><a class="more" href="/blog/">← Back to all posts</a></p>""")))

    # Civic guide: a standalone page, deliberately NOT built with page(), so it never
    # loads the AdSense script. Its own CSP blocks all network requests. Political and
    # social-location answers must never reach ads, analytics, or storage.
    quiz = (ROOT / "civic" / "quiz.html").read_text(encoding="utf-8")
    assert "googlesyndication" not in quiz and "adsbygoogle" not in quiz, "civic guide must not load ads"
    assert "connect-src 'none'" in quiz, "civic guide must keep its no-network CSP"
    plain_link = '<link rel="stylesheet" href="/site.css">'
    assert quiz.count(plain_link) == 1, "civic guide should link /site.css exactly once"
    placeholder = "<!--SITE_HEADER-->"
    assert quiz.count(placeholder) == 1, "civic guide must have exactly one header placeholder"
    civic_html = quiz.replace(placeholder, site_header("/civic/")).replace(plain_link, CSS_LINK)
    assert 'class="menu"' in civic_html, "civic guide must include the phone menu"
    assert not any(f'>{label}</a>' in civic_html for label in ("Questions",)), "civic guide has a stale menu link"
    assert 'href="/blog/#start"' not in civic_html and 'aria-current="page">Civic guide</a>' in civic_html, "civic guide header is out of date"
    write("civic/index.html", civic_html)

    # Voting demo: a standalone page like the civic guide (own no-network CSP, one inline script,
    # no AdSense). vote/voting.js holds the counting code and is tested by vote/test.js (node).
    demo = (ROOT / "vote" / "demo.html").read_text(encoding="utf-8")
    assert "googlesyndication" not in demo and "connect-src 'none'" in demo, "voting demo must stay ad-free and no-network"
    assert demo.count("<!--SITE_HEADER-->") == 1 and demo.count("/*VOTING_JS*/") == 1 and demo.count(plain_link) == 1
    vote_html = (demo.replace("<!--SITE_HEADER-->", site_header("/vote/"))
                 .replace(plain_link, CSS_LINK)
                 .replace("/*VOTING_JS*/", (ROOT / "vote" / "voting.js").read_text(encoding="utf-8")))
    write("vote/index.html", vote_html)


    # How to get organized in Philadelphia: a hand-checked list of local groups (no ads, no asks for money).
    # Every group was checked against its own page or local news in November 2026.
    write("philly/index.html", page("/philly/", "How to get organized in Philadelphia", "Local groups in Philadelphia where neighbors organize together: blocks, renters, fridges, co-ops, libraries and community groups.", simple(
        "Philadelphia", "How to get organized in Philadelphia",
        "I grew up in Philadelphia and live in San Diego now. A lot of what makes the city work is neighbors doing things together, and most of it is easy to miss from the outside.",
        """<p>I'm still learning how organizing works, so this is the list I wish I'd had. Each section says what the group does, who can join, and one first step you can take this week.</p>
<p>Every group here is real, and I checked each one against its own page or local news in November 2026. Contacts change, so open the link before you go. Listing a group isn't an endorsement, and nothing on this page asks you for money.</p>
<h2 id="start">Where to start</h2>
<ol>
<li><a href="#block">Become a block captain</a></li>
<li><a href="#rent">Organize where you rent</a></li>
<li><a href="#fridges">Stock a community fridge</a></li>
<li><a href="#coops">Join a food co-op</a></li>
<li><a href="#library">Get a library card</a></li>
<li><a href="#community">Find your community</a></li>
<li><a href="#work">Talk with your coworkers</a></li>
<li><a href="#political">Learn with a political group</a></li>
</ol>
<h2 id="block">Become a block captain</h2>
<p>A block captain is a neighbor who organizes cleanups, block parties and trash-day reminders, with tools and help from the City's Philadelphia More Beautiful Committee. Any resident can do it.</p>
<p><strong>First step:</strong> call <a href="tel:+12156853971">(215) 685-3971</a> to ask for a petition or to find out if your block already has a captain. Then get signatures from half your block plus one and mail it back.</p>
<p class="actions"><a class="cta" href="https://phila.gov/services/trash-recycling-city-upkeep/become-a-block-captain">Become a block captain</a></p>
<h2 id="rent">Organize where you rent</h2>
<p>Most tenant organizing starts with neighbors in one building talking to each other about repairs, rent and how they're treated. Tenant unions are growing here. <a href="https://whyy.org/articles/philadelphia-tenant-unions-organizing-landlords-accountability/">WHYY reported</a> that Philly went from about five known tenant associations before the pandemic to more than twenty.</p>
<p>Philly DSA's Renters' Justice Collective helps tenants organize their buildings to push for repairs, and it holds open monthly meetings.</p>
<p><strong>First step:</strong> knock on one neighbor's door and ask how repairs have been going for them.</p>
<p class="actions"><a class="cta" href="https://www.phillydsa.org/tenant_organizing">Meet the Renters' Justice Collective</a></p>
<h3 id="rent-help">If you need help right now</h3>
<p>PhillyTenant.org is a free guide made by legal aid and tenant groups in the city, including Community Legal Services, Philadelphia Legal Assistance and the Tenant Union Representative Network (TURN). It covers evictions, repairs, moving out, help paying back rent, and subsidized housing, in English, Spanish and Chinese.</p>
<p>The same site runs the Philly Tenant Hotline: <a href="tel:+12674432500">(267) 443-2500</a>. You can talk with a housing counselor at TURN, get free legal information, and get connected to free lawyers. TURN also runs free Know Your Rights webinars every day.</p>
<p>In some zip codes, low-income tenants facing eviction can get a free lawyer through Right to Counsel. The hotline can tell you if you qualify.</p>
<p class="actions"><a class="cta" href="https://phillytenant.org/">Know your rights as a renter</a></p>
<p><a href="https://phillytenant.org/legal-help/">Philly Tenant Hotline and legal help</a></p>
<h2 id="fridges">Stock a community fridge</h2>
<p>Community fridges are free fridges and pantries on the sidewalk, open all day, stocked by neighbors. Anyone can take food, and anyone can give.</p>
<p><strong>First step:</strong> drop off food that follows the fridge's posted rules, or sign up to help clean and restock.</p>
<ul>
<li><a href="https://www.mamateefridge.com/volunteer">Mama-Tee Community Fridge</a>, about 18 fridges across the city</li>
<li><a href="https://southphillyfridge.com/take-action">South Philadelphia Community Fridge</a></li>
<li><a href="https://www.germantowncommunityfridge.com/get-involved">Germantown Community Fridge</a></li>
<li><a href="https://coralstreetfridge.com/">Coral Street Fridge</a>, Kensington</li>
<li><a href="https://www.northwestmutualaidcollective.org/volunteerwithus">Northwest Mutual Aid Collective</a>, meal deliveries to older neighbors</li>
</ul>
<h2 id="coops">Join a food co-op</h2>
<p>A food co-op is a grocery store owned by the people who shop there. Anyone can shop. Owning a share is a one-time investment you can pay off slowly, and each of these has a program that lowers the cost if money is tight.</p>
<p><strong>First step:</strong> shop there once and ask at the register how membership works.</p>
<ul>
<li><a href="https://weaversway.coop/membership/membership-opportunities">Weavers Way</a>, Mt. Airy, Chestnut Hill and Germantown. $400 over time, $30 a year.</li>
<li><a href="https://mariposa.coop/join">Mariposa Food Co-op</a>, West Philly. $200 with payment plans.</li>
<li><a href="https://southphillyfoodcoop.nationbuilder.com/join">South Philly Food Co-op</a>. $300, and you can start with $5.</li>
</ul>
<h2 id="library">Get a library card</h2>
<p>In 1731, Ben Franklin and his friends started the Library Company so people could share books none of them could afford alone. The Free Library carries that idea today. A card is free if you live, work, pay taxes or go to school in the city, and branches host free programs.</p>
<p class="actions"><a class="cta" href="https://know.freelibrary.org/MyResearch/register/policy">Get a free library card</a></p>
<p><a href="https://libwww.freelibrary.org/branches/brnlist.cfm">Find your branch</a></p>
<h2 id="community">Find your community</h2>
<p>Some groups organize around who you are and where you're from. As a Vietnamese American, these are the ones I'd look at first.</p>
<ul>
<li><a href="https://www.vietlead.org">VietLead</a>, South Philly. Vietnamese and Southeast Asian community organizing: healing, youth leadership, health and civic work.</li>
<li><a href="https://aaunited.org/">Asian Americans United</a>, Chinatown. Youth leadership, the Mid-Autumn Festival, and know-your-rights help.</li>
<li><a href="https://phillythrive.nationbuilder.com/campaign">Philly Thrive</a>, Grays Ferry. Neighbors of the old refinery site pushing for clean air and a real say in what gets built there.</li>
</ul>
<h2 id="work">Talk with your coworkers</h2>
<p>If you have a job, the closest group is the people you already work with.</p>
<p><strong>First step:</strong> if your workplace has a union, go to one meeting. If it doesn't, talk with one coworker about what's hard at work.</p>
<h2 id="political">Learn with a political group</h2>
<p>Some people want to organize through politics too. Philly DSA runs a monthly series of New Member 101, Socialism 101 and Organizing 101, and says curious people are welcome. Dues are pay what you can, or you can ask for a waiver. I'm listing it because it's active in the city. I'm not telling anyone how to vote or what to join.</p>
<p class="actions"><a class="cta" href="https://www.phillydsa.org/getinvolved">See where Philly DSA says to start</a></p>
<p>If you'd rather start by learning with friends, here's <a href="/reading-circle/">how to start a reading circle</a>.</p>
<h2 id="hope">What I'm hoping for</h2>
<p>I'll keep this list updated as I learn more, and fix anything that goes out of date. If you're in Philly, I hope one of these fits your week. Picking one is enough.</p>
<p><a class="more" href="/blog/">← Back to the blog</a></p>""")))

    # Start a reading circle: a plain how-to for a small study group (no sign-up, no asks for money).
    write("reading-circle/index.html", page("/reading-circle/", "Start a reading circle", "A simple way to start a small reading group with friends: five steps, four questions for every meeting, and a six-week reading list.", simple(
        "Get organized", "Start a reading circle",
        "A lot of big movements started small, with a few people reading and talking at a kitchen table. You can start one with your friends this week. You don't need to be an expert. I'm still learning too.",
        """<p class="actions"><a class="cta" href="/handouts/reading-circle-packet.pdf">Print the reading circle packet (PDF, 7 pages)</a></p>
<h2 id="start">Where to start</h2>
<ol>
<li><strong>Ask 3 to 5 people you trust.</strong> Friends, classmates, coworkers, family. Small is good, because everyone gets to talk.</li>
<li><strong>Pick a time and a place.</strong> Once a week for an hour. A living room, a library room or a park bench all work.</li>
<li><strong>Read one short piece each week.</strong> A chapter or an essay. If someone didn't finish, they should still come.</li>
<li><strong>Talk with the same four questions.</strong> They're below, and they keep things simple.</li>
<li><strong>After a few weeks, pick one thing to do together.</strong> It could be a need on your block, at school or at work.</li>
</ol>
<h2 id="questions">The four questions</h2>
<ol>
<li>What stood out to you?</li>
<li>Where do you see this in our lives right now?</li>
<li>What confused you, or what do you disagree with?</li>
<li>What's one small thing we could try?</li>
</ol>
<h2 id="list">A six-week starter list</h2>
<p>These are books I'm reading now. Most of them are at the public library.</p>
<ol>
<li><strong>Week 1:</strong> Frantz Fanon, "Racism and Culture," in <cite>Toward the African Revolution</cite>. A short speech from 1956.</li>
<li><strong>Week 2:</strong> Karl Marx and Friedrich Engels, <cite>The Communist Manifesto</cite>, Part I. It's short and still argued about, so read it and decide what you think.</li>
<li><strong>Week 3:</strong> Walter Rodney, <cite>How Europe Underdeveloped Africa</cite>, chapter 1. What "development" means, and who it's measured for.</li>
<li><strong>Week 4:</strong> Johanna Fernández, <cite>The Young Lords</cite>, any one chapter. Young people in East Harlem who started by asking neighbors what they needed.</li>
<li><strong>Week 5:</strong> Gal Beckerman, <cite>The Quiet Before</cite>, the introduction. Why the slow talking before a movement matters.</li>
<li><strong>Week 6:</strong> Thomas Sowell, <cite>Intellectuals and Society</cite>, any one chapter. A view from the other side, and good practice in hearing people you disagree with.</li>
</ol>
<h2 id="rules">A few ground rules</h2>
<ul>
<li>Everyone gets a turn before anyone talks twice.</li>
<li>Push on ideas and stay kind to people.</li>
<li>What people share about their lives stays in the room.</li>
<li>Nobody has to agree, and nobody has to have read everything.</li>
</ul>
<h2 id="next">Then do something together</h2>
<p>When your circle is ready to act, the <a href="/philly/">Philly organizing list</a> has places to plug in, from block captains to tenant groups.</p>
<p>This page doesn't collect anything. There's no sign-up and no ask for money. There's a <a href="/handouts/reading-circle-packet.pdf">printable packet</a> with a one-page handout for each week. Change anything to fit your group.</p>
<p class="actions"><a class="cta" href="/philly/">Get organized in Philly</a></p>
<p><a class="more" href="/blog/">← Back to the blog</a></p>""")))

    # Reading list: Nick's books, grouped, with what each argues and why it's on the path.
    # No buy or affiliate links; sources are plain links to publishers and reference pages.
    write("reading-list/index.html", page("/reading-list/", "Reading list", "Seven books I'm reading to understand capitalism and what people have done about it, with what each one argues and one strong view from the other side.", simple(
        "Get organized", "Reading list",
        "These are the books I'm reading to understand how our economy got this way, and what people have done to change it. I'm still learning, so read them with me and argue with them too.",
        """<p>I grouped them so you can pick a place to start. Six of them are also the six weeks of the <a href="/reading-circle/">reading circle</a>, and there's a <a href="/handouts/reading-circle-packet.pdf">printable packet</a> with a page for each week. Most of them are at the public library.</p>
<h2 id="start">Start here</h2>
<h3 id="manifesto">The Communist Manifesto</h3>
<p><strong>Karl Marx and Friedrich Engels, 1848.</strong> A short pamphlet that says the history of society is a history of conflict between classes. It argues that working people would one day overthrow capitalism and end private property.</p>
<p><strong>Why it's here:</strong> almost every argument about capitalism still circles back to it. It's short, so you can read it yourself and decide what you think. In the reading circle it's <a href="/reading-circle/#list">week 2</a>.</p>
<h3 id="fanon">Toward the African Revolution</h3>
<p><strong>Frantz Fanon, essays from 1952 to 1961, collected in 1964.</strong> Articles, essays and letters, many first printed in the underground newspaper of Algeria's National Liberation Front. They follow his thinking on racism, colonialism and the fight for African independence.</p>
<p><strong>Why it's here:</strong> Fanon treats racism and colonialism as systems that people built, which means people can take them apart. That's how I want to look at capitalism too. Start with "Racism and Culture," a speech he gave in 1956. In the reading circle it's <a href="/reading-circle/#list">week 1</a>.</p>
<h3 id="quiet-before">The Quiet Before: On the Unexpected Origins of Radical Ideas</h3>
<p><strong>Gal Beckerman, 2022.</strong> Beckerman argues that radical ideas usually take shape in small, private spaces where a few people can talk things through. He worries social media is crowding those spaces out.</p>
<p><strong>Why it's here:</strong> it explains why slow conversations in small groups matter before any big change. That's the whole idea behind a reading circle. In the circle it's <a href="/reading-circle/#list">week 5</a>.</p>
<h2 id="history">History</h2>
<h3 id="rodney">How Europe Underdeveloped Africa</h3>
<p><strong>Walter Rodney, 1972.</strong> Rodney argues that the gap between Europe and Africa came from Europe exploiting Africa, and that colonialism left damage that lasts today.</p>
<p><strong>Why it's here:</strong> it shows how one place's wealth can be tied to another place's poverty. It also asks who "development" is measured for. In the reading circle it's <a href="/reading-circle/#list">week 3</a>.</p>
<h3 id="young-lords">The Young Lords: A Radical History</h3>
<p><strong>Johanna Fernández, 2020.</strong> The history of the Young Lords, poor and working-class Puerto Rican young people in Chicago and New York who modeled themselves on the Black Panther Party. Fernández shows how their protests won reforms and helped spread socialist ideas in the U.S.</p>
<p><strong>Why it's here:</strong> it shows people organizing around what their own neighborhood needed. In the reading circle it's <a href="/reading-circle/#list">week 4</a>.</p>
<h2 id="other-side">The other side</h2>
<h3 id="sowell">Intellectuals and Society</h3>
<p><strong>Thomas Sowell, 2009 (expanded in 2011).</strong> Sowell argues that intellectuals shape policy mostly by shaping public opinion, and that they're rarely held to account when their ideas fail. He says their fixes for society have often been badly wrong.</p>
<p><strong>Why it's here:</strong> a lot of his critique lands on people who think the way I do. A reading path that only agrees with itself isn't worth much, and if I can't answer his best points, I want to know that. In the reading circle it's <a href="/reading-circle/#list">week 6</a>.</p>
<h2 id="fiction">Fiction</h2>
<h3 id="vonnegut">Slaughterhouse-Five</h3>
<p><strong>Kurt Vonnegut, 1969.</strong> An antiwar novel about Billy Pilgrim, an American prisoner of war who survives the firebombing of Dresden and comes "unstuck in time." It's funny and grim at once.</p>
<p><strong>Why it's here:</strong> it's about ordinary people getting used up by big systems. One line, from a made-up propaganda pamphlet in the book, says "America is the wealthiest nation on Earth, but its people are mainly poor, and poor Americans are urged to hate themselves." It isn't in the six weeks, so it works as a seventh meeting.</p>
<h2 id="next">What I want to do next</h2>
<p>I'm reading these slowly, and I want to keep adding to this list as I learn, especially history from closer to home. If you want to read with friends, the <a href="/reading-circle/">reading circle page</a> has five steps and four questions, and that's enough to start.</p>
<h2 id="sources">Sources</h2>
<ul class="sources"><li>Encyclopaedia Britannica, <a href="https://www.britannica.com/topic/The-Communist-Manifesto">The Communist Manifesto</a>.</li><li>Grove Atlantic, <a href="https://groveatlantic.com/book/toward-the-african-revolution/">Toward the African Revolution</a> (publisher's description).</li><li>Wikipedia, <a href="https://en.wikipedia.org/wiki/Toward_the_African_Revolution">Toward the African Revolution</a> (French edition of 1964, and the 1956 speech).</li><li>Penguin Random House, <a href="https://www.penguinrandomhouse.com/books/552622/the-quiet-before-by-gal-beckerman/9781524759186">The Quiet Before</a> (publisher's description).</li><li>Verso, How Europe Underdeveloped Africa (publisher's description, via <a href="https://www.harvard.com/book/9781788731188">Harvard Book Store</a>).</li><li>UNC Press, <a href="https://uncpress.org/book/9781469653440/the-young-lords">The Young Lords: A Radical History</a> (publisher's description).</li><li>Basic Books, Intellectuals and Society, revised and expanded edition (publisher's description, via <a href="https://www.harvard.com/book/9780465025220">Harvard Book Store</a>).</li><li>Encyclopaedia Britannica, <a href="https://www.britannica.com/topic/Slaughterhouse-Five">Slaughterhouse-Five</a>.</li><li>Open Culture, <a href="https://openculture.com/2017/05/kurt-vonnegut-ponders-why-poor-americans-are-taught-to-hate-themselves.html">the Slaughterhouse-Five passage on poor Americans</a>.</li></ul>
<p class="actions"><a class="cta" href="/reading-circle/">Start a reading circle</a></p>
<p><a class="more" href="/blog/">← Back to the blog</a></p>""")))

    # Map your social location: a reflection page built on Hays' ADDRESSING framework, Crenshaw's
    # intersectionality and Bronfenbrenner's circles. Nothing is typed in or saved; no script, no form.
    write("social-location/index.html", page("/social-location/", "Map your social location", "A short interview about the groups you belong to, laid out as a map at three levels: micro (you), meso (your communities) and macro (society). Nothing is typed in, saved or sent.", simple(
        "Reflection", "Map your social location",
        "A short interview. Pick the words that fit you, skip anything you like, and see your map at the end. Nothing here is typed in, saved or sent.",
        """<div class="prose">
<p>Your social location is the mix of groups you belong to, like your age, your culture, your class, and your gender. Where you stand shapes what you can see easily, and what's hard to see.</p>
<p>Social workers and therapists often look at a life on three levels. <strong>Micro</strong> is you. <strong>Meso</strong> is the communities and places around you. <strong>Macro</strong> is the larger society: its history, laws, and messages.</p>
</div>
""" + SL.interview_html() + """
<p class="actions"><a class="cta" href="/handouts/map-your-social-location.pdf">Print the handouts (PDF, 4 pages)</a></p>
<h2 id="deeper">Questions to sit with</h2>
<p>The interview is a start. These questions go slower, and they work well on paper.</p>
<div class="prose">
<p>Therapists in training are asked to map their own before they try to understand anyone else's. These questions come from what I'm learning in my program. Go slowly, and skip anything that doesn't feel right today.</p>
<h3 id="parts">The parts of you</h3>
<p>Psychologist Pamela Hays made a list called ADDRESSING. Each letter is one part of who we are. Read each question and notice what comes up.</p>
</div>
<ol class="alist series-list"><li class="arow"><span class="part-no">A · Age and generation</span>What was happening in the world while you grew up, and how did it shape what feels normal to you?</li><li class="arow"><span class="part-no">D · Developmental disability</span>Growing up, were the places around you built for the way your body and mind work?</li><li class="arow"><span class="part-no">D · Disability later in life</span>Has an illness, injury, or change in your body or mind changed how the world treats you?</li><li class="arow"><span class="part-no">R · Religion and spirituality</span>What did your family believe, and what do you believe now?</li><li class="arow"><span class="part-no">E · Ethnic and racial identity</span>How do you describe your ethnicity and race? How do other people describe it?</li><li class="arow"><span class="part-no">S · Socioeconomic status</span>Growing up, did money feel steady or uncertain? What about now?</li><li class="arow"><span class="part-no">S · Sexual orientation</span>When have you felt free, or not free, to be open about who you love?</li><li class="arow"><span class="part-no">I · Indigenous heritage</span>Do you have Indigenous roots? Whose land do you live on now?</li><li class="arow"><span class="part-no">N · National origin</span>Where were you born, where were your parents born, and what language did you hear at home?</li><li class="arow"><span class="part-no">G · Gender</span>What did people expect of you because of your gender?</li></ol>
<div class="prose">
<p>Now look back over your answers. Which parts do you think about almost every day? Which ones rarely cross your mind?</p>
<p>The parts we rarely think about are often the ones where the world was already built for us. Peggy McIntosh wrote about this in 1989 as a kind of invisible backpack of advantages that people don't notice they're carrying.</p>
<details><summary>A question to sit with</summary><p>Pick one part you rarely think about. What might someone who stands in a different place on that part have to think about every day?</p></details>
<h3 id="overlap">Where the parts overlap</h3>
<p>In 1989, law professor Kimberlé Crenshaw gave a name to something people had lived for a long time. She called it intersectionality. It means the parts of us overlap, and the overlap can matter more than any one part alone.</p>
<p>She pointed to a 1976 case where Black women sued General Motors. The court said there was no race discrimination because GM hired Black men, and no sex discrimination because GM hired white women. The women who were both Black and women fell through the gap.</p>
<details><summary>Questions to sit with</summary><p>Has there been a time when two parts of you together changed how you were treated, more than either one would alone?</p><p>Which of your parts seem to get noticed first by other people? Which ones stay hidden?</p></details>
<h3 id="circles">The circles around you</h3>
<p>Psychologist Urie Bronfenbrenner pictured a person in the middle of circles. Family and friends are closest. Farther out are things like a parent's job and the local school board. On the outside are culture and laws. Later he added one more layer, time itself.</p>
<p>I wrote more about his circles in <a href="/blog/who-raises-a-kid/">Who raises a kid?</a></p>
<details><summary>Closest circle</summary><p>Who was around you every day growing up? Who is around you now?</p></details>
<details><summary>The circles you never saw</summary><p>What decisions shaped your life that you weren't in the room for, like a parent's work schedule or a school's budget?</p></details>
<details><summary>The outer circle</summary><p>What did your culture and your country tell you a good life looks like? Do you still believe it?</p></details>
<details><summary>Time</summary><p>What big events happened during your life, and how old were you when they did?</p></details>
<h2 id="after">After you finish</h2>
<p>Some of these questions can bring up heavy things. It's okay to stop. If you're in crisis, you can call or text <a href="tel:988">988</a>.</p>
<p>This page is for reflection. It isn't a test or a diagnosis, and it can't tell you who you are. Only you can do that, and your answers can change over time.</p>
<p>If you want to keep going, these posts build on the same ideas:</p>
<ul><li><a href="/blog/social-location-where-you-stand/">Social location: where you stand decides what you see</a></li><li><a href="/blog/privilege-is-everything-you-never-had-to-think-about/">Privilege is everything you never had to think about</a></li><li><a href="/blog/why-therapists-learn-cultural-humility/">Why therapists learn cultural humility</a></li><li><a href="/blog/what-therapy-ethics-codes-miss-about-culture/">What therapy ethics codes miss about culture</a></li><li><a href="/blog/why-we-blame-the-person-instead-of-the-situation/">Why we blame the person instead of the situation</a></li></ul>
<h2 id="sources">Sources</h2>
<ul class="sources"><li>Hays, P. A. (2016). <i>Addressing Cultural Complexities in Practice</i> (3rd ed.). American Psychological Association.</li><li>Crenshaw, K. (1989). Demarginalizing the intersection of race and sex. <i>University of Chicago Legal Forum</i>, 1989(1), 139–167.</li><li><i>DeGraffenreid v. General Motors</i>, 413 F. Supp. 142 (E.D. Mo. 1976).</li><li>McIntosh, P. (1989). White privilege: Unpacking the invisible knapsack. <i>Peace and Freedom</i>.</li><li>Dimock, M. (2019). Defining generations: Where Millennials end and Generation Z begins. Pew Research Center.</li><li>Office of Management and Budget (2024). Revisions to Statistical Policy Directive No. 15: Standards for maintaining, collecting, and presenting federal data on race and ethnicity.</li><li>Bronfenbrenner, U. (1979). <i>The Ecology of Human Development</i>. Harvard University Press.</li></ul>
</div>
<p><a class="more" href="/blog/">← Back to the blog</a></p>""")))

    # Start here: the seven-step path, smallest step first. Every step is a link the reader chooses.
    write("start-here/index.html", page("/start-here/", "Start here", "Seven steps, smallest first: from what you already believe to doing one thing with your neighbors.", simple(
        "Start here", "Seven steps, smallest first",
        "This blog takes a side. I think a few people own too much, decide too much, and leave everyone else to fight over what's left. Here's the path I'd walk a friend through. Take it at your own pace, skip anything, and argue with me on the way.",
        """<ol class="path">
<li><h2 id="step-1">Where do you stand?</h2><p>Thirty quick questions about sharing, work, home, care, power and hope. Most people believe in sharing more than they think. No score, nothing saved.</p><p class="actions"><a class="cta" href="/where-do-you-stand/">Answer the questions</a></p></li>
<li><h2 id="step-2">Map your social location</h2><p>Where you stand shapes what you can see easily, and what's hard to see.</p><p><a href="/social-location/">Map your social location</a></p></li>
<li><h2 id="step-3">How the system gets inside your head</h2><p>What therapy school is teaching me about how a society shapes the way we see ourselves. A series on Fanon, Freud and Foucault is on the way. For now, start with the therapy school series.</p><p><a href="/series/therapy-school/">Things therapy school taught me about society</a> · <a href="/blog/the-person-is-not-the-problem/">The person is not the problem</a></p></li>
<li><h2 id="step-4">Who pays, who profits</h2><p>Who ends up with less, and why the system keeps working that way.</p><p><a href="/blog/how-competition-wears-down-the-people-at-the-bottom/">How competition wears down the people at the bottom</a> · <a href="/blog/one-roll-of-toilet-paper/">One roll of toilet paper</a> · <a href="/blog/we-didnt-all-start-at-the-same-line/">We didn't all start at the same line</a></p></li>
<li><h2 id="step-5">What people built instead</h2><p>People have always fed, housed and cared for each other when the system wouldn't.</p><p><a href="/blog/what-the-panthers-and-king-both-saw-about-poverty/">What the Black Panthers and Dr. King both saw about poverty</a> · <a href="/philly/#coops">Food co-ops in Philly</a> · <a href="/philly/#fridges">Community fridges</a></p></li>
<li><h2 id="step-6">Read with friends</h2><p>A few people, one short reading a week, four questions. Week six is a writer who disagrees with most of this, on purpose.</p><p><a href="/reading-circle/">Start a reading circle</a></p></li>
<li><h2 id="step-7">Do one thing</h2><p>Talk with a coworker. Knock on a neighbor's door. Stock a fridge. Picking one is enough.</p><p class="actions"><a class="cta" href="/philly/">Get organized in Philly</a></p></li>
</ol>
<p>Nothing on this path asks for money, and nothing you do here is saved. If you think I've got something wrong, that's okay. Read the other side's best case and decide for yourself.</p>
<p><a class="more" href="/blog/">← Back to the blog</a></p>""")))
    # Where do you stand?: thirty statements, no script, no form, no score. Nothing is typed, saved or sent.
    write("where-do-you-stand/index.html", page("/where-do-you-stand/", "Where do you stand?", "Thirty questions about sharing, work, home, care, power and hope. No score, no label, and nothing is saved or sent.", simple(
        "Questions", "Where do you stand?",
        "Thirty statements about sharing, work, home, care, power and hope. Pick \"That's me,\" \"Not sure\" or \"Not me\" for each, or skip it. At the end you'll see the ideas you already agree with.",
        """<div class="prose">
<p>I'll be honest about what this is. This blog takes a side, and these questions come from that side. I think a lot of people already believe in sharing, fair work and care for everyone, and just haven't heard it said out loud. You might not, and that's okay too.</p>
<p>There's no score, no label, and no wrong answer. Nothing is typed in, saved or sent.</p>
</div>
""" + WS.questionnaire_html() + """
<h2 id="next">What now?</h2>
<p>If you said "That's me" a lot, you already believe much of what this blog argues. If you didn't, I'd still like you to stick around and push back.</p>
<p class="actions"><a class="cta" href="/start-here/#step-2">Next step: map your social location</a></p>
<p><a class="more" href="/start-here/">See all 7 steps</a></p>""")))
    # Privacy
    write("privacy/index.html", page("/privacy/", "Privacy", "How this site handles your data and ads.", simple(
        None, "Privacy", None, """<p>I don't want your data. There are no accounts and no forms, and nothing you type here is sent to this site.</p>
<h2>Ads</h2>
<p>This site does not currently show ads. If that changes, this page will be updated before any ads appear.</p>
<h2>Civic guide</h2>
<p>The <a href="/civic/">civic guide</a> has no ads, trackers, or analytics. It blocks all network requests, so your answers cannot be sent anywhere. Answers are kept only in the open page, never saved to your browser, and disappear when you leave or press “Reset all answers.” Your political answers are never used for ads, accounts, or retargeting.</p>
<h2>Podcast audio</h2>
<p>Episodes are hosted on this site and only load when you press Play.</p>
<h2>Fonts</h2>
<p>The fonts are stored on this site too. Showing text never contacts a font service or any other outside server.</p>""")))

    write_sitemap()
    write_feed()

    # 404
    write("404.html", page("/404", "Not found", "Page not found.", simple(
        None, "Sorry, I can't find that page.", None,
        '<p>It may have moved, or the link might be off. Here are some places to start.</p>'
        + not_found_links()
        + '<p class="actions"><a class="cta" href="/blog/">Back to the blog</a></p>')))


SITEMAP_PAGES = ["/blog/", "/blog/archive/", "/start-here/", "/where-do-you-stand/", SERIES_PATH, "/social-location/", "/podcasts/", "/how-i-argue/", "/philly/", "/reading-circle/", "/reading-list/", "/privacy/"]


def write_sitemap():
    """sitemap.xml: every page search engines may list. Never the civic guide or voting demo."""
    newest = max(p["date"] for p in POSTS)
    rows = [(path, newest if path == "/blog/" else None) for path in SITEMAP_PAGES]
    rows += [(subject_path(t), None) for t in THEMES]
    rows += [(f"/blog/{p['slug']}/", p["date"]) for p in POSTS]
    urls = "".join(f"<url><loc>{SITE_URL}{html.escape(path)}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n"
                   for path, d in rows)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n",
                                     encoding="utf-8")


def rfc822(d):
    import datetime
    return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 +0000")


def not_found_links():
    """The 404 page: the newest posts and the subjects, so a wrong link still leads somewhere.
    Links are absolute because the 404 page is served at any address."""
    newest = sorted(POSTS, key=lambda p: p["date"], reverse=True)[:5]
    posts = "".join(f'<li><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a></li>' for p in newest)
    subjects = "".join(f'<li><a href="{subject_path(t)}">{esc(t)}</a></li>' for t in THEMES)
    return (f'<div class="lost"><section aria-labelledby="lost-new"><h2 id="lost-new">Newest writing</h2><ul>{posts}</ul></section>'
            f'<section aria-labelledby="lost-sub"><h2 id="lost-sub">Browse by subject</h2><ul>{subjects}</ul></section></div>')


def feed_body(slug):
    """A post's full text for feed readers, with site links made absolute so they work outside hoto.lol."""
    body = body_of(slug)
    return re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{SITE_URL}/', body)


def write_feed():
    """feed.xml: RSS 2.0 for the essays, newest first, so readers and newsletter tools can follow."""
    items = "".join(
        f"<item><title>{html.escape(p['title'])}</title>"
        f"<link>{SITE_URL}/blog/{p['slug']}/</link><guid>{SITE_URL}/blog/{p['slug']}/</guid>"
        f"<pubDate>{rfc822(p['date'])}</pubDate><description>{html.escape(p['summary'])}</description>"
        f"<content:encoded>{html.escape(feed_body(p['slug']))}</content:encoded></item>\n"
        for p in sorted(POSTS, key=lambda p: p["date"], reverse=True))
    (OUT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
        f"<title>{SITE}</title><link>{SITE_URL}/blog/</link>"
        f'<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>'
        "<description>Nick's blog about mental health, family, and fairness, from a therapy student who's still learning. Education and opinion, not therapy or advice.</description>"
        "<language>en-us</language>\n" + items + "</channel></rss>\n", encoding="utf-8")


CRISIS = ('In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.')
FOOTER_LINES = [
    "Independent and unofficial. Not affiliated with any politician, party or campaign.",
    STAND_FOOT,
    "Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.",
    'This site currently shows no ads. <a href="/privacy/">Privacy</a>.',
]
# The civic guide is a standalone page with its own two-line footer, written for its no-ads, no-network promise.
OWN_FOOTER = {"civic/index.html", "vote/index.html"}
EXTERNAL_ASSET = re.compile(r'<(?:link|script|img)\b[^>]*?\b(?:src|href)\s*=\s*["\']?(?:https?:)?//', re.I)
# A canonical link to this site's own full address is a label for search engines, not a load.
OWN_CANONICAL = re.compile(r'<link rel="canonical" href="https://hoto\.lol/[^"]*">')
PLACEHOLDER = re.compile(r"\[(?:[A-Z]|\d+|TODO|TBD|XX+|\.\.\.|insert[^\]]*|placeholder[^\]]*)\]", re.I)


def check_output():
    """Fail the build on mistakes that are easy to ship and hard to see."""
    errors = []
    for f in sorted(OUT.rglob("*.html")):
        rel = f.relative_to(OUT).as_posix()
        text = f.read_text(encoding="utf-8")
        rest = text
        for b in POST_BODIES:
            rest = rest.replace(b, "")
        if "\u2014" in rest:
            errors.append(f"{rel}: em dash outside an essay body")
        if m := EXTERNAL_ASSET.search(OWN_CANONICAL.sub("", text)):
            errors.append(f"{rel}: external URL in a link, script or img tag: {m.group(0)[:80]}")
        if CRISIS not in text:
            errors.append(f"{rel}: crisis strip text is missing or changed")
        if "speechify" in text.lower():
            errors.append(f"{rel}: links to Speechify; host the audio on this site instead")
        if rel not in OWN_FOOTER:
            errors += [f"{rel}: footer line missing: {line[:40]}" for line in FOOTER_LINES if f"<p>{line}</p>" not in text]
        if m := PLACEHOLDER.search(re.sub(r"<(script|style)\b.*?</\1>", "", rest, flags=re.S)):
            errors.append(f"{rel}: leftover placeholder text {m.group(0)}")
    if errors:
        raise SystemExit("Build checks failed:\n  " + "\n  ".join(errors))


if __name__ == "__main__":
    build()
    check_output()
    print("Built", sum(1 for _ in OUT.rglob("*.html")), "pages into", OUT)
