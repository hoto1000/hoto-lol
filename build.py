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
CSS_VERSION = hashlib.sha256((ROOT / "site.css").read_bytes()).hexdigest()[:10]
CSS_LINK = f'<link rel="stylesheet" href="/site.css?v={CSS_VERSION}">'

POSTS = [
    {
        "slug": "why-i-think-everyone-should-try-therapy",
        "title": "Why I think everyone should try therapy",
        "date": "2026-11-07",
        "summary": "A video script: why I think everyone should try therapy at least once, what surprised me in school, and three things I'm trying.",
    },
    {
        "slug": "why-so-many-of-us-feel-lonely",
        "title": "Why so many of us feel lonely",
        "date": "2026-11-06",
        "summary": "A video script: what the Surgeon General's report on loneliness found, what couples therapy says about needing people, and three things I'm trying.",
    },
    {
        "slug": "what-fights-are-really-asking",
        "title": "What fights are really asking",
        "date": "2026-11-06",
        "summary": "A video script on Emotionally Focused Therapy: why many fights are a protest, the negative cycle, what's under the anger, and three things I'm trying.",
    },
    {
        "slug": "who-was-your-secure-base",
        "title": "Who was your secure base? What attachment theory taught me",
        "date": "2026-11-06",
        "summary": "A video script on attachment theory: Bowlby's report, Ainsworth's Strange Situation, the love quiz, earned security, the feminist critique, and three things I'm trying.",
    },
    {
        "slug": "why-mental-health-matters",
        "title": "Why mental health matters",
        "date": "2026-11-06",
        "summary": "A video script: half of mental health conditions start by age 14, many people wait years for help, and three things I'm trying.",
    },
    {
        "slug": "learning-to-apologize-and-move-on",
        "title": "Learning how to apologize, and how to move on",
        "date": "2026-11-06",
        "summary": "A video script on repair: what couples research and restorative justice taught me about apologizing, guilt versus shame, and letting myself move on.",
    },
    {
        "slug": "why-we-blame-the-person-instead-of-the-situation",
        "title": "Why we blame the person instead of the situation",
        "date": "2026-11-06",
        "summary": "A video script on the fundamental attribution error: the Castro essays, the Good Samaritan study, how culture shapes blame, and three things I'm trying.",
    },
    {
        "slug": "how-competition-wears-down-the-people-at-the-bottom",
        "title": "How competition wears down the people at the bottom",
        "date": "2026-11-06",
        "summary": "A video script: survival of the fittest, Adam Smith's sympathy, the Matthew effect, the Whitehall study, mutual aid, and three things I'm trying.",
    },
    {
        "slug": "why-therapists-learn-cultural-humility",
        "title": "Why therapists learn cultural humility",
        "date": "2026-11-06",
        "summary": "A video script with some history: the Tuskegee study, cultural competence, two doctors in Oakland who offered the word humility, and three things I'm trying.",
    },
    {
        "slug": "socialism-starts-with-culture-philadelphia",
        "title": "Socialism starts with culture: Philadelphia",
        "date": "2026-11-06",
        "summary": "A video script: why I think neighbors practice sharing before a country votes for it, Gramsci's war of position, and what Philly has shared since 1731.",
    },
    {
        "slug": "who-raises-a-kid",
        "title": "Who raises a kid? Bronfenbrenner's circles",
        "date": "2026-11-05",
        "summary": "A video script on Urie Bronfenbrenner's map of everything that raises a kid, what it changed about how I think about blame, and three things I'm trying.",
    },
    {
        "slug": "the-person-is-not-the-problem",
        "title": "The person is not the problem: what narrative therapy taught me",
        "date": "2026-11-05",
        "summary": "A video script on Michael White and David Epston's narrative therapy, how it changed the way I talk about homelessness, and three things I'm trying.",
    },
    {
        "slug": "the-identified-patient",
        "title": "The identified patient: what one struggling kid can be carrying",
        "date": "2026-11-05",
        "summary": "A video script on the family therapy idea of the identified patient, where I see it outside the therapy room, and three things I'm trying.",
    },
    {
        "slug": "who-gets-to-be-the-thinker",
        "title": "Who gets to be called a thinker? Gramsci and Collins",
        "date": "2026-11-05",
        "summary": "A short video script: Gramsci on who gets the title of thinker, Patricia Hill Collins on knowledge built outside universities, and three steps I'm trying.",
    },
    {
        "slug": "intergenerational-trauma-vietnamese-americans",
        "title": "My parents never had a word for it: intergenerational trauma",
        "date": "2026-11-05",
        "summary": "A video script about intergenerational trauma as a Vietnamese American: the rules of my house, why they made sense, and three things I'm trying.",
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
        "summary": "A video script telling my story in scenes: growing up Vietnamese American in Pennsylvania, moving to San Diego, a role-play in therapy school, and what's helping me.",
    },
    {
        "slug": "do-you-know-the-number-988",
        "title": "Do you know the number for a mental health emergency?",
        "date": "2026-11-03",
        "summary": "A short video script about 988, the free and confidential crisis line most people still haven't heard of.",
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
<p>None of this makes me an expert. It's where I learned most of what I write about, and I'm still learning.</p>"""


NAV = [("/blog/", "Blog"), ("/podcasts/", "Podcast"), ("/civic/", "Civic guide"), ("/how-i-argue/", "About")]

BLUNT = ("<strong>Heads up: I write bluntly.</strong> If a post brings up something heavy, it's okay to stop reading.")

UNOFFICIAL = ("<strong>Independent and unofficial.</strong> otohay blog is a personal project. It is not affiliated with, "
              "endorsed by, or paid for by Alexandria Ocasio-Cortez, any campaign, party, or political committee. "
              "Essays are opinion. Sourced claims are linked where they appear.")

AI_NOTE = ("I made this site with help from AI. I'm still trying to understand what AI means for writing, "
           "and I want to be honest with you about it while I figure that out.")

AI_NOTE_LONG = ("I built this site with AI tools, and some of the writing here was organized and edited with them too. "
                "I'm still learning what that means for honesty, for craft, and for the people who read this. "
                "I'll keep updating this note as my thinking changes.")

TEACHERS = "Most of these ideas aren't mine. I'm passing on what I learned from my professors at San Diego State."


# Related reading: picked offline with the open model sentence-transformers/all-MiniLM-L6-v2 (title, summary and
# first 250 words of each essay, cosine similarity), then filtered to matches scoring 0.30 or more. No code runs for visitors.
RELATED = {
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
        "a-president-who-understands-how-systems-feel",
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
    "a-president-who-understands-how-systems-feel": [
        "social-location-where-you-stand",
        "we-didnt-all-start-at-the-same-line",
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
    return f'<span class="kind kind-{cls}">{esc(kind)}</span>'


# Planet Hoto: one small planet mark for the header and footer, lit blue on the day side and red on the dusk side.
# Decorative only (aria-hidden), so screen readers hear the same names as before.
GLYPH = ('<svg class="glyph" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">'
         '<circle class="g-body" cx="12" cy="12" r="9"/>'
         '<path class="g-day" d="M12 3a9 9 0 0 0 0 18"/><path class="g-dusk" d="M12 3a9 9 0 0 1 0 18"/></svg>')

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
        on = path.startswith("/blog/") or path == "/" if href == "/blog/" else path.startswith(href)
        return ' aria-current="page"' if on else ""

    links = "".join(f'<a href="{href}"{cur(href)}>{label}</a>' for href, label in NAV)
    return (f'<header class="top">\n'
            f'<a class="wordmark" href="/" aria-label="otohay blog, home">{GLYPH}otohay <span>blog</span></a>\n'
            f'<nav class="main nav-wide" aria-label="Main">{links}</nav>\n'
            f'<details class="menu"><summary>Menu</summary><nav class="nav-menu" aria-label="Main">{links}</nav></details>\n'
            f'</header>')


SITE_URL = "https://hoto.lol"
# Pages search engines may list. The civic guide and voting demo are standalone pages with their
# own "noindex" tag and are never listed; the 404 page is noindex too.
NOINDEX_PATHS = {"/404"}


def canonical(path):
    """The one full address search engines should use. The home page and /blog/ are the same page."""
    return SITE_URL + ("/blog/" if path == "/" else path)


SHARE_IMAGE = "/share.png"  # made by scripts/make_share_image.py, 1200 x 630
SHARE_ALT = "otohay blog, hoto.lol, above a planet lit blue on one side and red on the other"


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
<meta name="theme-color" content="#f5f7fb" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#05070d" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{CSS_LINK}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<aside class="crisis" aria-label="Crisis help">In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.</aside>
<aside class="ai-note" aria-label="About AI on this site">{esc(AI_NOTE)}</aside>
{site_header(path)}
<main id="main" tabindex="-1">
{body}
</main>
<footer>
<div class="foot-top">
<p class="foot-mark">{GLYPH}Thanks for reading. Nick</p>
<nav aria-label="Footer">{foot_nav}</nav>
<p class="foot-follow">Follow along with the <a href="/feed.xml">RSS feed</a>.</p>
</div>
<div class="foot-fine">
<p>Independent and unofficial. Not affiliated with AOC or any campaign.</p>
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
        cls = ' class="sc"' if sc(t) else ""
        themes.append(f'<div class="theme"><h3 id="{tid}"{cls}>{esc(t)}</h3>'
                      f'<ul class="alist">{"".join(archive_row(p) for p in items)}</ul></div>')
        side.append(f'<li><a href="#{tid}">{esc(t)} ({len(items)})</a></li>')

    return f"""<div class="frame">
<section class="hero" aria-labelledby="hero-h">
<div class="hero-text">
<h1 id="hero-h">Welcome to otohay blog.</h1>
<p class="lede">Hi, I'm Nick. This is my blog where I share my compassion for social justice issues and what I've learned in school. I'm a grad student in marriage and family therapy, so I'm still learning, and I link my sources when I can.</p>
<p class="start-jump"><a class="jump" href="#start">New here? Start here</a></p>
<p class="unofficial">{UNOFFICIAL}</p>
</div>
{HORIZON}
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
<div class="section-head"><h2 id="start-h">Start here</h2><p>These are the three I'd read first.</p></div>
<ul class="doors">{"".join(doors)}</ul>
<p class="civic-callout">Or try the civic guide, <a href="/civic/">Where do my political views sit?</a> Seven policy areas, no labels, no voting advice. Your answers never leave your device.</p>
</section>

<section class="section" id="about" aria-labelledby="about-h">
<div class="section-head"><h2 id="about-h">About me</h2></div>
<ul class="about">
<li><a href="/how-i-argue/#ideals"><span class="about-t">Where I start from</span></a></li>
<li><a href="/how-i-argue/"><span class="about-t">About this blog</span></a></li>
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
            f'Your browser cannot play this audio. The full text is below.</audio></div>'
            f'<p class="aside-note">The essay below is the transcript.</p></section>')


# A short "written by" card at the end of every post, like the author box on Substack or
# LinkedIn articles. The words come from the home page intro Nick approved.
AUTHOR_CARD = ('<aside class="author-card" aria-labelledby="author-h">'
               '<span class="avatar avatar-lg" aria-hidden="true">N</span>'
               '<div><p class="label" id="author-h">Written by Nick</p>'
               '<p class="author-bio">I\'m a Vietnamese American grad student training to be a marriage and family therapist. '
               'I write about the things in our society that frustrate me, why they might be that way, and what could help.</p>'
               '<p class="author-more"><a href="/how-i-argue/">More about me</a></p></div></aside>')


def echoes_title(title, question):
    """True when the framing question nearly repeats the post title (for example
    "Why so many of us feel lonely" and "Why do so many of us feel lonely?")."""
    words = lambda s: re.sub(r"[^a-z ]", "", s.lower()).split()
    return difflib.SequenceMatcher(None, words(title), words(question)).ratio() >= 0.8


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
        after.append(f'<aside class="sit-with" aria-labelledby="sit-h"><p class="label sc" id="sit-h">Sit with this</p>'
                     f'<p class="sit-q">{q(f["sit"])}</p></aside>')
    if f["related"]:
        r = post(f["related"])
        rq = frame(r["slug"])["question"] or r["title"]
        after.append(f'<nav class="read-next" aria-label="Read next"><p class="label">Read next</p>'
                     f'<a href="/blog/{r["slug"]}/"><span class="q-text">{q(rq)}</span><cite>{esc(r["title"])}</cite></a></nav>')
    rel = [s for s in RELATED.get(slug, []) if s != f["related"]]
    if rel:
        links = "".join(f'<a href="/blog/{s}/"><span class="q-text">{q(frame(s)["question"] or post(s)["title"])}</span>'
                        f'<cite>{esc(post(s)["title"])}</cite></a>' for s in rel)
        after.append(f'<nav class="read-next" aria-label="Related reading"><p class="label">Related reading</p>{links}'
                     f'<p class="aside-note">Matches picked with an open AI model that compares the essays\' text, not by a person.</p></nav>')
    after.append(AUTHOR_CARD)
    after.append('<p class="disagree"><strong>Disagree? That\'s okay.</strong> I could be wrong, so read the other side\'s best case too.</p>')
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
<p class="label essay-kind{sc(f["theme"])}">{esc(f["theme"])}{kind_badge(f["kind"])}</p>
<h1>{esc(p['title'])}</h1>
{question}
<div class="byline"><span class="avatar" aria-hidden="true">N</span><p class="byline-text"><span class="byline-name">By Nick</span><span class="essay-meta"><time datetime="{p['date']}">{nice(p['date'])}</time> · {minutes(slug)} min read</span></p></div>
{voices}
{corrections}
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
<p class="essay-end"><a class="back" href="/blog/">← All writing</a><a class="back" href="/how-i-argue/">About</a></p>
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
    shutil.copytree(ROOT / "podcasts", OUT / "podcasts")
    if (ROOT / "audio").is_dir():  # essay narrations made by scripts/make_audio.py
        shutil.copytree(ROOT / "audio", OUT / "audio")
    shutil.copytree(ROOT / "fonts", OUT / "fonts")
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

    desc = "An independent, personal journal of hard questions about society: essays, a podcast, and a private civic self-check."
    # The home page and /blog/ are the same front page. hoto.lol/ currently redirects to /blog/.
    write("index.html", page("/", None, desc, front_page()))
    write("blog/index.html", page("/blog/", "Writing", desc, front_page()))

    for p in POSTS:
        write(f"blog/{p['slug']}/index.html", page(f"/blog/{p['slug']}/", p["title"], p["summary"], essay_page(p), published=p["date"]))

    cards = "".join(episode_card(e) for e in EPISODES)
    write("podcasts/index.html", page("/podcasts/", "Podcast", "Podcast episodes: thinking out loud about hard questions.", simple(
        "otohay blog podcast", "Podcast",
        "These episodes are my reflections on the same questions I write about. They're my opinion, and they aren't therapy. Nothing plays until you press Play. "
        "Every essay also has its own Listen player at the top of the page.",
        cards)))

    rules = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in RULES)
    ideals = "".join(f"<h3>{esc(a)}</h3><p>{esc(b)}</p>" for a, b in IDEALS)
    write("how-i-argue/index.html", page("/how-i-argue/", "About this blog", "What this blog is, a few things I try to do here, and a note on AI.", simple(
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
<h2 id="ai">A note on AI</h2>
<p>{esc(AI_NOTE_LONG)}</p>
<h2>What this is not</h2>
<p>{UNOFFICIAL}</p>
<p>{TEACHERS}</p>
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

    # Voting demo: a standalone page like the civic guide (own no-network CSP, one inline script,
    # no AdSense). vote/voting.js holds the counting code and is tested by vote/test.js (node).
    demo = (ROOT / "vote" / "demo.html").read_text(encoding="utf-8")
    assert "googlesyndication" not in demo and "connect-src 'none'" in demo, "voting demo must stay ad-free and no-network"
    assert demo.count("<!--SITE_HEADER-->") == 1 and demo.count("/*VOTING_JS*/") == 1 and demo.count(plain_link) == 1
    vote_html = (demo.replace("<!--SITE_HEADER-->", site_header("/vote/"))
                 .replace(plain_link, CSS_LINK)
                 .replace("/*VOTING_JS*/", (ROOT / "vote" / "voting.js").read_text(encoding="utf-8")))
    write("vote/index.html", vote_html)

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


SITEMAP_PAGES = ["/blog/", "/podcasts/", "/how-i-argue/", "/privacy/"]


def write_sitemap():
    """sitemap.xml: every page search engines may list. Never the civic guide or voting demo."""
    newest = max(p["date"] for p in POSTS)
    rows = [(path, newest if path == "/blog/" else None) for path in SITEMAP_PAGES]
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
    subjects = "".join(f'<li><a href="/blog/#subject-{slugify(t)}">{esc(t)}</a></li>' for t in THEMES)
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
        "<description>An independent, personal journal of hard questions about society. Education and opinion, not therapy or advice.</description>"
        "<language>en-us</language>\n" + items + "</channel></rss>\n", encoding="utf-8")


CRISIS = ('In crisis? Call or text <a href="tel:988">988</a> (U.S.) or call <a href="tel:911">911</a> for an emergency.')
FOOTER_LINES = [
    "Independent and unofficial. Not affiliated with AOC or any campaign.",
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
