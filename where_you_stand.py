"""The "Where do you stand?" questionnaire on /where-do-you-stand/ and its ask on the homepage.

Built like the social location interview: no script and no form. Every answer is a radio button
that stays in the open page. Nothing is typed, saved or sent. The "Your answers" box is pure CSS:
each statement has a line that only shows while "That's me" is picked (generated rules, written
into site.css by `python3 where_you_stand.py`). There is no score and no label for the visitor.
"""
import html
import re

esc = html.escape

ANSWERS = ["That's me", "Not sure", "Not me"]

# (part id, title, statements, read-more links). Each statement: (what the visitor reads, the idea it points to).
PARTS = [
    ("sharing", "Sharing", [
        ("If a friend couldn't pay rent this month, I'd help.", "Mutual aid: neighbors helping each other directly."),
        ("I'd rather borrow a ladder from a neighbor than buy one I'll use once.", "Sharing what we own in common."),
        ("Food that would go to waste should go to people who need it.", "Need comes before profit."),
        ("I've given time or money without expecting anything back.", "Giving without a price tag."),
        ("I feel better when my whole block is doing okay, and not only me.", "My wellbeing is tied to my neighbors'."),
    ], [("/philly/#fridges", "Stock a community fridge")]),
    ("work", "Work", [
        ("The people who do the work should have a say in how it's run.", "Workplace democracy."),
        ("Owners often make more from workers' labor than the workers do.", "The value of work should go to the people who do it."),
        ("A full-time job should be enough to live on.", "A living wage."),
        ("Coworkers sticking together makes everyone safer.", "Solidarity at work, the idea behind unions."),
        ("Nobody should have to work sick to keep their job.", "Rest and sick time as a right."),
    ], [("/blog/how-competition-wears-down-the-people-at-the-bottom/", "How competition wears down the people at the bottom")]),
    ("home", "Home", [
        ("A home is for living in first, and for making money second.", "Housing as a human need."),
        ("Renters in one building should be able to bargain together.", "Tenant unions."),
        ("Nobody should have to sleep outside.", "Shelter for everyone."),
        ("Rent shouldn't eat most of a paycheck.", "Affordable housing."),
        ("Neighbors should have a say in what gets built on their block.", "Community control."),
    ], [("/philly/#rent", "Organize where you rent")]),
    ("care", "Care", [
        ("Healthcare shouldn't depend on having a job.", "Care as something we all hold in common."),
        ("Therapy should be affordable for anyone who needs it.", "Mental health care for everyone."),
        ("Caring for kids and elders is real work that deserves support.", "Care work is work."),
        ("A health crisis shouldn't push a family into debt.", "Nobody should go broke getting well."),
        ("People who are struggling need care more than punishment.", "Care before punishment."),
    ], [("/blog/we-made-it-okay-to-talk/", "We made it okay to talk. Getting help is still too hard.")]),
    ("power", "Power", [
        ("Very rich people have more say in politics than I do.", "Money buys a louder voice."),
        ("Big money in elections drowns out regular voters.", "Elections should belong to voters."),
        ("Who gets called \"lazy\" or \"crazy\" often depends on who's doing the labeling.", "Labels can serve the people in charge."),
        ("Some people got a head start that had nothing to do with hard work.", "We didn't all start at the same line."),
        ("Things are this way because people made choices, so people can make new ones.", "The system was built, so it can be rebuilt."),
    ], [("/blog/privilege-is-everything-you-never-had-to-think-about/", "Privilege is everything you never had to think about")]),
    ("hope", "Hope", [
        ("Regular people working together have changed things before.", "Organized people have power."),
        ("I'd read and talk about this with a few friends.", "Learning together."),
        ("I'd show up for a neighbor's problem even if it isn't mine.", "Solidarity."),
        ("A fairer way to live is possible, even if I can't picture all of it yet.", "A fairer world can be built."),
        ("Change can start small, with the people already around me.", "Building from the bottom up."),
    ], [("/blog/what-the-panthers-and-king-both-saw-about-poverty/", "What the Black Panthers and Dr. King both saw about poverty"),
        ("/reading-circle/", "Start a reading circle")]),
]


def _id(part, i, a=None):
    return f"ws-{part}-{i}" if a is None else f"ws-{part}-{i}-{a}"


def questionnaire_html():
    """Six parts of five statements, then the live "Your answers" box."""
    out = []
    for n, (pid, title, items, _) in enumerate(PARTS, 1):
        out.append(f'<section class="sl-level ws-part" id="{pid}" aria-labelledby="{pid}-h">'
                   f'<h2 id="{pid}-h"><span class="sl-tag">Part {n} of {len(PARTS)}</span> {esc(title)}</h2>')
        for i, (statement, _) in enumerate(items):
            chips = "".join(
                f'<label class="chip"><input type="radio" name="{_id(pid, i)}" id="{_id(pid, i, a)}">{esc(ans)}</label>'
                for a, ans in enumerate(ANSWERS))
            out.append(f'<fieldset class="sl-step"><legend>{esc(statement)}</legend>'
                       f'<p class="sl-hint">Pick one, or skip.</p><div class="chips">{chips}</div></fieldset>')
        out.append("</section>")
    cols = []
    for pid, title, items, links in PARTS:
        lines = "".join(f'<li class="sl-pick" data-pick="{_id(pid, i)}">{esc(idea)}</li>' for i, (_, idea) in enumerate(items))
        more = " · ".join(f'<a href="{h}">{esc(t)}</a>' for h, t in links)
        cols.append(f'<div class="sl-col ws-col-{pid}"><h3>{esc(title)}</h3><ul>{lines}</ul>'
                    f'<p class="sl-empty">No "That\'s me" here yet.</p><p class="ws-more">Read more: {more}</p></div>')
    out.append('<section class="sl-map" id="your-answers" aria-labelledby="ans-h"><h2 id="ans-h">Your answers</h2>'
               '<p>Every time you said "That\'s me," the idea behind it shows up here. There\'s no score and no label. '
               'It lives only on this open page and is gone when you leave.</p>'
               f'<div class="sl-cols">{"".join(cols)}</div>'
               '<p class="sl-old">If your answers don\'t show up here, your browser is too old for this part. The questions above still work.</p>'
               '</section>')
    return "\n".join(out)


def questionnaire_css():
    """One rule per statement: show its idea while "That's me" is picked."""
    shows = [f'main:has(#{_id(pid, i, 0)}:checked) [data-pick="{_id(pid, i)}"]'
             for pid, _, items, _ in PARTS for i in range(len(items))]
    empties = [f'main:has(#{pid} input[id$="-0"]:checked) .ws-col-{pid} .sl-empty' for pid, _, _, _ in PARTS]
    return ("\n/* Where do you stand questionnaire: generated by where_you_stand.py, do not edit by hand. */\n"
            + ",\n".join(shows) + " { display: list-item; }\n"
            + ",\n".join(empties) + " { display: none; }\n")


HOME_ASK = """<section class="sl-ask" aria-labelledby="ask-h">
<h2 id="ask-h">Where do you stand?</h2>
<p>Thirty questions about sharing, work, home, care, power and hope, about seven minutes. Most people believe in sharing more than they think. There's no score.</p>
<p class="btn-grid"><a class="btn btn-main" href="/where-do-you-stand/#sharing">Start the questions</a><a class="btn" href="/start-here/">See all 7 steps</a></p>
</section>"""


def statement_count():
    return sum(len(items) for _, _, items, _ in PARTS)


assert statement_count() == 30
assert all(re.fullmatch(r"[a-z]+", pid) for pid, _, _, _ in PARTS)

START = "/* BEGIN where-you-stand generated */"
END = "/* END where-you-stand generated */"


def css_block():
    return START + questionnaire_css() + END


def sync_css(path):
    """Write the generated block into site.css. Run: python3 where_you_stand.py"""
    text = path.read_text(encoding="utf-8")
    block = css_block()
    if START in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, text, flags=re.S)
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    import pathlib
    sync_css(pathlib.Path(__file__).parent / "site.css")
    print("site.css questionnaire rules updated")
