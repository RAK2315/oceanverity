# What actually gets a deck shortlisted

Collected from people who have judged SIH and from teams who won after being rejected. Simple
points, no theory. Read this before touching [`DECK.md`](DECK.md) or [`script.md`](script.md).

---

## The one fact that shapes everything

**A judge spends 3 to 5 minutes on your PPT in the first screening.** If it does not land in that
window, it is over. Not because the idea was weak - because the deck did not carry it.

A weak deck kills a strong idea. A clean deck carries a simple one. Both happen every year.

---

## The five things that get decks rejected

1. **Text-heavy slides.** Judges do not read paragraphs. They scan.
2. **Feature dumping.** Listing 20 features is not strategy. It reads as "we do not know what
   matters."
3. **Prototype and deck disagreeing.** If the demo does not mirror the slides, the story breaks.
4. **No measurable impact.** "It will help many people" is not impact. A number is.
5. **Ignoring the evaluation criteria.** They are scoring against a lens. Miss it, miss the list.

---

## The four-part structure that works

1. **Solution snapshot** - the problem, a stat, and what makes you different
2. **Technical approach** - stack, architecture, domain depth
3. **Feasibility** - risks, challenges, how you actually execute
4. **Impact** - scale, sustainability, where it goes after SIH

Inside that, the narrative spine is always:

**Problem → Solution → Architecture → Implementation → Impact.**

---

## Slide rules

- Start with the **problem**. Make it clear before any technology is mentioned.
- **Clarity over quantity.** No long paragraphs.
- Diagrams, workflows, key points. Not prose.
- Show the **complete workflow** - input to output - in one clean picture.
- **Justify every tech choice.** Because you need it, not because it sounds impressive.
- Show **what you actually built**. Prototype screenshots or a demo video. Proof beats promises.
- **Who benefits, and how much?** Answer both.
- Keep it consistent and professional. Clutter kills.

---

## Diagrams

- **Do not use AI-generated diagrams.** Judges can tell, and a wrong arrow is worse than no
  diagram. Use AI for ideas, then draw it yourself so it reflects what you actually built.
- [napkin.ai](https://www.napkin.ai/) is good for architecture and flow visuals - it produces
  real selectable objects, not flat images, so you can fix a label.
- In this repo the architecture diagram is drawn by hand in
  [`scripts/ppt_diagrams.html`](../scripts/ppt_diagrams.html) and rendered with
  `cd web && node render-diagrams.mjs`, for exactly this reason: every label in it is a fact and
  a model cannot be trusted to spell `incois_argo_10d_VAM`.

---

## Humanise anything AI helped write

AI is fine for brainstorming and tightening. **Do not paste what it gives you.** The deck should
sound like your team. The tells: uniform sentence length, "leveraging", "cutting-edge",
"seamless", "revolutionise", three-item lists everywhere, and every section opening the same way.

---

## Add proof links

Put these on the deck where a judge can reach them:

- GitHub repository
- The deployed prototype
- A video walking through it

They give an evaluator direct access to evidence instead of asking them to take your word.

---

## Prototype and deck must be one story

The demo mirrors the slides. Same order, same claims, same language. A judge should see **one
product narrative**, not a deck and then a separate unrelated tour of an app.

Practically: whatever number is on the impact slide should appear on screen during the demo.

---

## Applying this to our project

What we have that most teams do not, and should lead with:

- **A number on our own error**, printed separately for assimilated and unassimilated
  instruments - this is the differentiator and it should be on the first slide, not the fifth
- A **live deployed link** and a **public defect list**
- Every figure on the deck **generated from the build** ([`FACTS.md`](FACTS.md)), so nothing on
  screen can go stale
- A **requirements page** that answers each PS clause and links to the control that does it

What we have to actively resist:

- We have 15 variables and 15 probes and 379 tests. **That is feature-dump ammunition.** Mention
  them as evidence of rigour, once, and move on.
- The rendering is impressive and it is the *least* important thing about the project. If the
  demo becomes a graphics showcase, the argument is lost.

---

## Sources

Community posts from SIH judges and multi-time SIH winners, collected September 2026. The
consistent message across all of them: **presentation is as important as innovation, and most
teams lose here rather than in the code.**
