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
import shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"  # GitHub Pages serves main:/docs

SITE = "Project Hoto"
# Versioned stylesheet link. Cloudflare tells browsers to keep site.css for 4 hours,
# while pages are kept for 10 minutes. Putting a hash of the CSS in the link means a
# new page always loads the matching styles, and an unchanged stylesheet stays cached.
CSS_VERSION = hashlib.sha256((ROOT / "site.css").read_bytes()).hexdigest()[:10]
CSS_LINK = f'<link rel="stylesheet" href="/site.css?v={CSS_VERSION}">'

POSTS = [
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
        "slug": "a-president-who-understands-how-systems-feel",
        "title": "A President Who Understands How Systems Feel",
        "date": "2026-10-25",
        "summary": "Why I might support Alexandria Ocasio-Cortez if she runs for president in 2028: social location, her record, and a politics that connects housing, health, climate, and daily costs.",
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
        "slug": "the-watcher-in-your-pocket-audio",
        "title": 'Why You Police Your Own Behavior',
        "date": "2026-10-28",
        "length": "4 min",
        "summary": 'The panopticon meets social media: why we edit ourselves when we might be watched. Audio version of the essay The Watcher in Your Pocket.',
        "listen_url": "https://speechify.app.link/1ZBUHMzzx7b",
        "note": "AI-generated audio made with Speechify from the essay text, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "you-are-not-the-problem-audio",
        "title": 'Who Built Your Diagnostic Labels?',
        "date": "2026-10-27",
        "length": "6 min",
        "summary": 'Foucault on power, knowledge and norms. Labels can help, and it is still fair to ask who decided where the line goes. Audio version of the essay.',
        "listen_url": "https://speechify.app.link/Atf111yzx7b",
        "note": "AI-generated audio made with Speechify from the essay text, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-your-memory-is-constantly-editing",
        "title": "Why Your Memory Is Constantly Editing",
        "date": "2026-10-27",
        "length": "",
        "summary": "How memory works, from sensory and working memory to long-term storage, sleep and forgetting.",
        "listen_url": "https://speechify.app.link/efY5swmUv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-your-brain-deletes-memories",
        "title": "Why Your Brain Deletes Memories",
        "date": "2026-10-27",
        "length": "",
        "summary": "Why forgetting is a normal part of how memory works.",
        "listen_url": "https://speechify.app.link/geO23fZUv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-winning-the-lottery-ruins-your-brain",
        "title": "Why Winning The Lottery Ruins Your Brain",
        "date": "2026-10-27",
        "length": "",
        "summary": "The hedonic treadmill and why big wins fade fast.",
        "listen_url": "https://speechify.app.link/Y13QLmNuv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-you-can-never-be-satisfied",
        "title": "Why You Can Never Be Satisfied",
        "date": "2026-10-27",
        "length": "",
        "summary": "Why wanting keeps moving the goalposts.",
        "listen_url": "https://speechify.app.link/iVrayivUv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "is-toxic-positivity-making-us-miserable",
        "title": "Is Toxic Positivity Making Us Miserable?",
        "date": "2026-10-27",
        "length": "",
        "summary": "When forced cheer backfires.",
        "listen_url": "https://speechify.app.link/TgDv4BvUv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-modern-happiness-is-broken",
        "title": "Why Modern Happiness Is Broken",
        "date": "2026-10-27",
        "length": "",
        "summary": "Why chasing happiness can leave us emptier.",
        "listen_url": "https://speechify.app.link/hQGMfYvUv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "mastering-the-5-am-club",
        "title": "Mastering the 5 AM Club",
        "date": "2026-10-27",
        "length": "",
        "summary": "A look at early-morning routines and whether they work for everyone.",
        "listen_url": "https://speechify.app.link/GoqC8AZUv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "the-hidden-rules-of-belonging",
        "title": "The Hidden Rules of Belonging",
        "date": "2026-10-27",
        "length": "",
        "summary": "The unwritten rules about who counts as professional or respectful, and how to make them fairer.",
        "listen_url": "https://speechify.app.link/8lsvG7vXv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "who-gets-believed-at-the-front-desk",
        "title": "Who Gets Believed at the Front Desk",
        "date": "2026-10-27",
        "length": "",
        "summary": "How schools and agencies treat people who ask for help, and what a clear appeal path could look like.",
        "listen_url": "https://speechify.app.link/fkLQ8CwXv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "the-invisible-cost-of-commuting",
        "title": "The Invisible Cost of Commuting",
        "date": "2026-10-27",
        "length": "",
        "summary": "The travel time, fares, transfers and care duties behind getting to a service.",
        "listen_url": "https://speechify.app.link/QKmyY5wXv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "translation-is-a-form-of-welcome",
        "title": "Translation Is a Form of Welcome",
        "date": "2026-10-27",
        "length": "",
        "summary": "Who gets clear information, and why language access should be community reviewed and paid.",
        "listen_url": "https://speechify.app.link/iVeJExxXv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-your-feedback-gets-ignored",
        "title": "Why Your Feedback Gets Ignored",
        "date": "2026-10-27",
        "length": "",
        "summary": "How people can reach their representatives, see what happened to their input, and disagree without being dismissed.",
        "listen_url": "https://speechify.app.link/nhbkp0xXv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-you-are-always-exhausted",
        "title": "Why You Are Always Exhausted",
        "date": "2026-10-27",
        "length": "",
        "summary": "A look at burnout, how modern work culture keeps us on edge, and what Stoic thinking says about the choices we do have.",
        "listen_url": "https://speechify.app.link/6Sy6Eemux7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-you-feel-lonely-online",
        "title": "Why You Feel Lonely Online",
        "date": "2026-10-27",
        "length": "",
        "summary": "Why being constantly connected can still leave us feeling alone, and how social media shapes isolation.",
        "listen_url": "https://speechify.app.link/FtKZTlkux7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-authenticity-is-not-performance",
        "title": "Why Authenticity Is Not Performance",
        "date": "2026-10-27",
        "length": "",
        "summary": "What existentialist ideas about authenticity can tell us about the curated selves we present online.",
        "listen_url": "https://speechify.app.link/gNqjItjux7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "who-are-you-really",
        "title": "Who Are You, Really?",
        "date": "2026-10-27",
        "length": "",
        "summary": "What philosophers like Locke and Parfit, and psychology research on self-concept, say about who we are over time.",
        "listen_url": "https://speechify.app.link/pk4H5KnBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-chasing-happiness-keeps-you-unhappy",
        "title": "Why Chasing Happiness Keeps You Unhappy",
        "date": "2026-10-27",
        "length": "",
        "summary": "Should happiness be the goal of a life? A look at utilitarianism, hedonism, and positive psychology.",
        "listen_url": "https://speechify.app.link/MH7H33nBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "rewriting-your-personal-narrative",
        "title": "Rewriting Your Personal Narrative",
        "date": "2026-10-27",
        "length": "",
        "summary": "How narrative ideas and existentialist thought place meaning-making at the center of how people understand hard experiences.",
        "listen_url": "https://speechify.app.link/SyAdSppBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "are-you-really-in-control",
        "title": "Are You Really In Control?",
        "date": "2026-10-27",
        "length": "",
        "summary": "What brain science does and does not show about free will, and what that could mean for responsibility.",
        "listen_url": "https://speechify.app.link/z64n6IpBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-you-are-not-your-peers",
        "title": "Why You Are Not Your Peers",
        "date": "2026-10-27",
        "length": "",
        "summary": "Social comparison theory meets the philosophy of envy, and why measuring ourselves against others is so hard to stop.",
        "listen_url": "https://speechify.app.link/L5kjMxrBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-smart-people-believe-nonsense",
        "title": "Why Smart People Believe Nonsense",
        "date": "2026-10-27",
        "length": "",
        "summary": "Cognitive bias and the philosophy of knowledge: why sharp people can still hold beliefs that do not hold up.",
        "listen_url": "https://speechify.app.link/47R5FAPBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "why-death-makes-life-meaningful",
        "title": "Why Death Makes Life Meaningful",
        "date": "2026-10-27",
        "length": "",
        "summary": "What Epicurus and Buddhist thought say about mortality and grief. Gentle pace.",
        "listen_url": "https://speechify.app.link/H1csxbPBx7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "fearless-speech-audio",
        "title": 'The Courage of Fearless Speech',
        "date": "2026-10-26",
        "length": "4 min",
        "summary": "Foucault's parrhesia, what it is not, and four short boundary sentences. Audio version of the essay.",
        "listen_url": "https://speechify.app.link/2JKZh9xzx7b",
        "note": "AI-generated audio made with Speechify from the essay text, for general education and opinion. Not therapy. In the US, call or text 988 if you are in crisis.",
        "overview": [],
    },
    {
        "slug": "aoc-does-background-dictate-governance",
        "title": "AOC: Does Background Dictate Governance?",
        "date": "2026-10-24",
        "length": "8 min",
        "summary": "A look at how a leader's social location might shape the questions they ask in power, using Alexandria Ocasio-Cortez's possible 2028 run as the example.",
        "listen_url": "https://speechify.app.link/RnX8Xf1Vv7b",
        "note": "AI-generated audio overview made with Speechify, for general education and opinion. Personal opinion; not affiliated with her or any campaign.",
        "overview": [],
    },
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
#   kind:     Essay, Opinion, or Sourced explainer (opinion is always labeled)
#   sit:      one question for the reader to sit with at the end
#   related:  slug of one essay to read next
#   voices:   thinkers the essay itself names (never add names it doesn't use)
#   corrections: optional list of ("YYYY-MM-DD", "what changed"), shown at the top
# ---------------------------------------------------------------------------
THEMES = ["Politics and civic life", "Schools", "Mind and how to live", "Mental health"]

FRAMING = {
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
    "a-president-who-understands-how-systems-feel": {
        "question": "Can where a leader comes from shape what they see?",
        "theme": "Politics and civic life",
        "kind": "Opinion",
        "note": "Personal opinion; not affiliated with her or any campaign.",
        "sit": "Which parts of your own life shape what you notice about how the country works, and what might they hide from you?",
        "related": "what-im-learning-about-third-parties",
        "voices": [],
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
        "related": "a-president-who-understands-how-systems-feel",
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

# Open questions: topics still being thought through. No essay yet, no deadline.
OPEN_QUESTIONS = [
    ("Who pays the paperwork tax?", "Forms, deadlines and repeat documents make people spend hours just to reach help. Which step could we remove?"),
    ("Can a bus route decide who gets care?", "A service only helps the people who can actually reach it."),
    ("Who gets heard at a public meeting?", "Meeting times, childcare, transit, disability access and language decide who is in the room."),
    ("Is the public library part of the safety net?", "Internet, job searches, a cool room and company, without pretending it can replace housing or health care."),
    ("Who does the hidden second shift?", "School forms, appointments and office hours quietly assume someone has time for unpaid care."),
    ("What does a second chance need?", "One practical barrier after incarceration, like a housing application, without reducing anyone to their record."),
    ("Who shows up after the storm?", "When a tornado or ice storm hits, how much rests on neighbors and local volunteers, and how should everyone else back them up?"),
    ("Can getting help include giving it?", "One Ozarks charity's holiday program has parents pick gifts for their kids and kids pick gifts for their parents, so everyone has something to give. Could public programs protect dignity that way?"),
]

RULES = [
    ("Opinion is labeled.", "When a piece is my view, it says so. Opinion pieces are marked on the index."),
    ("Claims get sources.", "Facts link to where they come from. Uncertain parts are marked as uncertain."),
    ("Disagreement is welcome.", "The strongest fair objection belongs inside the essay, not outside it."),
    ("Errors get fixed.", "If something turns out wrong, I correct it at the top of the post, with the date and what changed."),
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
                 "in Springfield, Missouri, that pairs emergency help with tools for the long run. Project Hoto is not affiliated with them.")

NAV = [("/blog/", "Blog"), ("/podcasts/", "Podcast"), ("/civic/", "Civic guide"), ("/how-i-argue/", "How I argue")]

BLUNT = ("<strong>Heads up: these posts are blunt.</strong> That is a style choice, not a judgment of you. "
         "If a post stirs up something heavy, you can stop reading any time.")

UNOFFICIAL = ("<strong>Independent and unofficial.</strong> Project Hoto is a personal project. It is not affiliated with, "
              "endorsed by, or paid for by Alexandria Ocasio-Cortez, any campaign, party, or political committee. "
              "Essays are opinion. Sourced claims are linked where they appear.")


def esc(s):
    return html.escape(s, quote=True)


def q(text):
    """Escape a question."""
    return esc(text)


def kind_badge(kind):
    """Type label coded by shape as well as words: Opinion is filled, Sourced explainer is boxed, Essay has a square bullet."""
    cls = {"Opinion": "opinion", "Sourced explainer": "sourced"}.get(kind, "essay")
    return f'<span class="kind kind-{cls}">{esc(kind)}</span>'


def site_header(path):
    """The shared desktop and phone header, used by page() and by the standalone civic guide."""
    def cur(href):
        # Writing covers the front page, /blog/ and every post; the others cover their own section.
        on = path.startswith("/blog/") or path == "/" if href == "/blog/" else path.startswith(href)
        return ' aria-current="page"' if on else ""

    links = "".join(f'<a href="{href}"{cur(href)}>{label}</a>' for href, label in NAV)
    return (f'<header class="top">\n'
            f'<a class="wordmark" href="/" aria-label="Project Hoto, home">Project <span>Hoto</span></a>\n'
            f'<nav class="main nav-wide" aria-label="Main">{links}</nav>\n'
            f'<details class="menu"><summary>Menu</summary><nav class="nav-menu" aria-label="Main">{links}</nav></details>\n'
            f'</header>')


def page(path, title, description, body, script=""):
    foot_nav = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    full_title = f"{SITE}: hard questions about how we live together" if title is None else f"{title} · {SITE}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="google-adsense-account" content="ca-pub-2462240112532447">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151a1e" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{CSS_LINK}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="crisis" aria-label="Crisis help">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</aside>
{site_header(path)}
<main id="main" tabindex="-1">
{body}
</main>
<footer>
<p class="foot-mark">Ask the hard questions. Argue them fairly.</p>
<nav aria-label="Footer">{foot_nav}</nav>
<p>Independent and unofficial. Not affiliated with AOC or any campaign.</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p>This site currently shows no ads. <a href="/privacy/">Privacy</a>.</p>
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
    ask = f'<p class="row-q">{esc(f["question"])}</p>' if f["question"] else ""
    return (f'<li class="row"><div class="row-meta">{kind_badge(f["kind"])}<span>{esc(f["theme"])}</span>'
            f'<time datetime="{p["date"]}">{nice(p["date"])}</time><span>{minutes(p["slug"])} min read</span></div>'
            f'<h3 class="row-title"><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a></h3>'
            f'{ask}<p class="row-sum">{esc(p["summary"])}</p></li>')


def archive_row(p):
    f = frame(p["slug"])
    return (f'<li class="arow"><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a>'
            f'<span class="row-meta">{kind_badge(f["kind"])}<time datetime="{p["date"]}">{nice(p["date"])}</time></span></li>')


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

    latest = "".join(latest_row(p) for p in POSTS[:6])
    themes, side = [], []
    for t in THEMES:
        items = [p for p in POSTS if frame(p["slug"])["theme"] == t]
        tid = "subject-" + slugify(t)
        themes.append(f'<div class="theme"><h3 id="{tid}">{esc(t)}</h3>'
                      f'<ul class="alist">{"".join(archive_row(p) for p in items)}</ul></div>')
        side.append(f'<li><a href="#{tid}">{esc(t)} ({len(items)})</a></li>')

    shelf = "".join(f"<li><h3>{q(a)}</h3><p>{esc(b)}</p></li>" for a, b in OPEN_QUESTIONS)

    return f"""<div class="frame">
<section class="hero" aria-labelledby="hero-h">
<div class="hero-text">
<p class="kicker">An independent journal of hard questions about society</p>
<h1 id="hero-h">Ask the hard questions. Argue them fairly.</h1>
<p class="lede">Essays, a podcast and a private civic self-check about power, school and how to live together. One person thinking in public, with sources, and room for you to disagree.</p>
<p class="unofficial">{UNOFFICIAL}</p>
</div>
</section>

<div class="index-grid">
<div class="index-main">
<section class="section" id="latest" aria-labelledby="latest-h">
<div class="section-head"><h2 id="latest-h">Latest writing</h2><a class="jump" href="#questions">Browse by subject</a></div>
<ul class="rows">{latest}</ul>
</section>

<section class="section" id="questions" aria-labelledby="questions-h">
<div class="section-head"><h2 id="questions-h">By subject</h2></div>
{"".join(themes)}
<p class="aside-note">{BLUNT}</p>
</section>
</div>
<aside class="index-side" aria-labelledby="side-h">
<h2 id="side-h">Browse by subject</h2>
<ul>{"".join(side)}</ul>
</aside>
</div>

<div class="index-main">
<section class="section" id="start" aria-labelledby="start-h">
<div class="section-head"><h2 id="start-h">Start here</h2><p>Three doors in. Pick the question that pulls at you.</p></div>
<ul class="doors">{"".join(doors)}</ul>
<p class="civic-callout">Or try the civic guide, <a href="/civic/">Where do my political views sit?</a> Seven policy areas, no labels, no voting advice. Your answers never leave your device.</p>
</section>

<section class="section" id="open" aria-labelledby="open-h">
<div class="section-head"><h2 id="open-h">Open questions</h2><p>Things I am still thinking through. No essay yet, and no deadline.</p></div>
<ul class="shelf">{shelf}</ul>
</section>

<section class="section" id="about" aria-labelledby="about-h">
<div class="section-head"><h2 id="about-h">About this journal</h2></div>
<ul class="about">
<li><a href="/how-i-argue/#ideals"><span class="about-t">Where I start from</span><span class="about-d">Five ideals behind the questions. When hard times hit, neighbors help each other through.</span></a></li>
<li><a href="/how-i-argue/"><span class="about-t">How I argue here</span><span class="about-d">Rules I hold myself to, so you can see where fact ends and opinion begins.</span></a></li>
</ul>
</section>
</div>
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


def essay_page(p):
    f = frame(p["slug"])
    slug = p["slug"]
    question = f'<p class="essay-q">{q(f["question"])}</p>' if f["question"] else ""
    voices = (f'<p class="voices">Ideas from <b>{esc(", ".join(f["voices"]))}</b></p>' if f["voices"] else "")
    corrections = ""
    if f["corrections"]:
        items = "".join(f'<li><time datetime="{d}">{nice(d)}</time>: {esc(t)}</li>' for d, t in f["corrections"])
        corrections = f'<div class="corrections"><p class="label">Corrections</p><ul>{items}</ul></div>'
    after = []
    if f["sit"]:
        after.append(f'<aside class="sit-with" aria-labelledby="sit-h"><p class="label" id="sit-h">Sit with this</p>'
                     f'<p class="sit-q">{q(f["sit"])}</p></aside>')
    if f["related"]:
        r = post(f["related"])
        rq = frame(r["slug"])["question"] or r["title"]
        after.append(f'<nav class="read-next" aria-label="Read next"><p class="label">Read next</p>'
                     f'<a href="/blog/{r["slug"]}/"><span class="q-text">{q(rq)}</span><cite>{esc(r["title"])}</cite></a></nav>')
    after.append('<p class="disagree"><strong>Disagree? Good.</strong> Read the other side\'s best case too.</p>')
    body, parts = with_outline(body_of(slug))
    POST_BODIES.append(body)
    toc_phone = toc_wide = ""
    if len(parts) >= 3:
        links = "".join(f'<li><a href="#{hid}">{html.escape(text)}</a></li>' for hid, text in parts)
        toc_phone = f'<details class="toc-phone"><summary>The argument</summary><ol>{links}</ol></details>'
        toc_wide = f'<nav class="toc-wide" aria-label="The argument"><p class="toc-title">The argument</p><ol>{links}</ol></nav>'

    return f"""<article class="essay">
<header class="essay-head">
<a class="back" href="/blog/">← All writing</a>
<p class="label essay-kind">{esc(f["theme"])}{kind_badge(f["kind"])}</p>
<h1>{esc(p['title'])}</h1>
{question}
<p class="essay-meta"><time datetime="{p['date']}">{nice(p['date'])}</time> · {minutes(slug)} min read</p>
{voices}
{corrections}
{toc_phone}
</header>
<div class="essay-body">
<div class="prose">
{body}
</div>
{toc_wide}
</div>
<div class="after">
{"".join(after)}
<p class="essay-end"><a class="back" href="/blog/">← All writing</a><a class="back" href="/how-i-argue/">How I argue here</a></p>
</div>
</article>
"""


def episode_card(e, full=True):
    overview = ""
    if full and e["overview"]:
        paras = "".join(f"<p>{esc(x)}</p>" for x in e["overview"])
        overview = f"<details><summary>Read the episode overview</summary>{paras}</details>"
    if e.get("listen_url"):
        player = f'<p class="player"><a href="{e["listen_url"]}" target="_blank" rel="noopener noreferrer">Listen on Speechify (opens in a new tab)</a></p>'
    else:
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
    k = f'<p class="kicker">{kicker}</p>' if kicker else ""
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
    shutil.copytree(ROOT / "podcasts", OUT / "podcasts")
    shutil.copytree(ROOT / "fonts", OUT / "fonts")
    (OUT / "CNAME").write_text("hoto.lol\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "ads.txt").write_text("google.com, pub-2462240112532447, DIRECT, f08c47fec0942fa0\n")
    (OUT / "robots.txt").write_text("User-agent: Mediapartners-Google\nAllow: /\n\nUser-agent: *\nDisallow: /\n")

    for slug, f in FRAMING.items():
        assert any(p["slug"] == slug for p in POSTS), f"framing for unknown post {slug}"
        assert f["theme"] in THEMES, f"unknown theme for {slug}"
        assert not f.get("related") or any(p["slug"] == f["related"] for p in POSTS), f"bad related link in {slug}"

    desc = "An independent, personal journal of hard questions about society: essays, a podcast, and a private civic self-check."
    # The home page and /blog/ are the same front page. hoto.lol/ currently redirects to /blog/.
    write("index.html", page("/", None, desc, front_page()))
    write("blog/index.html", page("/blog/", "Writing", desc, front_page()))

    for p in POSTS:
        write(f"blog/{p['slug']}/index.html", page(f"/blog/{p['slug']}/", p["title"], p["summary"], essay_page(p)))

    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcast", "Podcast episodes: thinking out loud about hard questions.", simple(
        "Project Hoto podcast", "Podcast",
        "These episodes are personal reflections and opinions. They are conversation, not therapy. Nothing plays until you press Play.",
        cards)))

    shape = "".join(f"<li><div><b>{esc(a)}</b><span>{esc(b)}</span></div></li>" for a, b in [
        ("Why it matters", "Why this question is worth your time, and mine."),
        ("What we know", "What is documented, what is uncertain, and what I think, kept apart."),
        ("Who decides", "Who has the power to change it."),
        ("Who pays", "Who benefits, and who bears the costs."),
        ("Who gets missed", "Who falls through the cracks, and what it would take to reach them."),
        ("The best objection", "The strongest fair case against my view."),
        ("One change", "A specific proposal, its trade-offs, and how we would know if it helped."),
        ("Sources and corrections", "Every source, plus a dated note on anything I fixed."),
    ])
    rules = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in RULES)
    ideals = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in IDEALS)
    write("how-i-argue/index.html", page("/how-i-argue/", "How I argue here", "The rules this blog holds itself to.", simple(
        "The method", "How I argue here",
        "Project Hoto is one person thinking in public about hard questions. These are the rules I hold myself to, so you can tell where fact ends and opinion begins.",
        f"""<h2 id="ideals">Where I start from</h2>
<p>Five ideals sit under every question here. They come from a simple picture of a good community: when hard times hit, neighbors help each other through.</p>
<div class="rules-page">{ideals}</div>
<p>{IDEALS_CREDIT}</p>
<h2>Four commitments</h2>
<div class="rules-page">{rules}</div>
<h2>The shape of a question</h2>
<p>This is the order I am building new essays around. Each step answers something a fair reader would ask.</p>
<ol class="shape">{shape}</ol>
<h2>What this is not</h2>
<p>{UNOFFICIAL}</p>
<p>Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.</p>
<p class="aside-note">{BLUNT}</p>
<p><a class="more" href="/blog/">← Back to the questions</a></p>""")))

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
    assert not any(f'>{label}</a>' in civic_html for label in ("Start here", "Questions")), "civic guide has a stale menu link"
    assert 'href="/blog/#start"' not in civic_html and 'aria-current="page">Civic guide</a>' in civic_html, "civic guide header is out of date"
    write("civic/index.html", civic_html)

    # Privacy
    write("privacy/index.html", page("/privacy/", "Privacy", "How this site handles your data and ads.", simple(
        None, "Privacy", None, """<p>No accounts. No forms. Nothing you type here is sent to this site.</p>
<h2>Ads</h2>
<p>This site does not currently show ads. If that changes, this page will be updated before any ads appear.</p>
<h2>Civic guide</h2>
<p>The <a href="/civic/">civic guide</a> has no ads, trackers, or analytics. It blocks all network requests, so your answers cannot be sent anywhere. Answers are kept only in the open page, never saved to your browser, and disappear when you leave or press “Reset all answers.” Your political answers are never used for ads, accounts, or retargeting.</p>
<h2>Podcast audio</h2>
<p>Episodes are hosted on this site and only load when you press Play.</p>
<h2>Fonts</h2>
<p>The fonts are stored on this site too. Showing text never contacts a font service or any other outside server.</p>""")))

    # 404
    write("404.html", page("/404", "Not found", "Page not found.", simple(
        None, "Nothing here?", None,
        '<p>That page does not exist, or it moved.</p>'
        '<p class="actions"><a class="cta" href="/blog/">Go to the questions</a></p>')))


CRISIS = ('In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.')
FOOTER_LINES = [
    "Independent and unofficial. Not affiliated with AOC or any campaign.",
    "Everything here is education and opinion. It is not therapy, diagnosis, or treatment, and it is not a substitute for a licensed professional.",
    'This site currently shows no ads. <a href="/privacy/">Privacy</a>.',
]
# The civic guide is a standalone page with its own two-line footer, written for its no-ads, no-network promise.
OWN_FOOTER = {"civic/index.html"}
EXTERNAL_ASSET = re.compile(r'<(?:link|script|img)\b[^>]*?\b(?:src|href)\s*=\s*["\']?(?:https?:)?//', re.I)
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
        if m := EXTERNAL_ASSET.search(text):
            errors.append(f"{rel}: external URL in a link, script or img tag: {m.group(0)[:80]}")
        if CRISIS not in text:
            errors.append(f"{rel}: crisis strip text is missing or changed")
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
