# What actually gets a deck shortlisted

Collected from people who have judged SIH and from teams who won after being rejected. Simple
points, no theory. Read this before touching [`DECK.md`](DECK.md) or [`script.md`](script.md).

**This file holds decisions.** The raw material it was argued from is in
[`SUBMISSION-GUIDANCE.md`](SUBMISSION-GUIDANCE.md) - an owner-collected checklist plus an
evaluator rubric, **a suggestion rather than an instruction, and partly out of date**. Its
section 6 lists what this project deliberately did *not* take from it, so nobody re-applies it.

---

## Honesty is the proof, not the product

This is the failure this deck keeps drifting into, so it is written down.

Everything good about this project is true *and checkable*, and that is rare enough that it is
tempting to make checkability the pitch. It is not the pitch. **A judge is buying a capability
and accepting the proof; they are not buying the proof.** "Honest about gaps" sitting in one of
four innovation slots is a limitation occupying the place a reader looks for a reason to
shortlist you.

The shape that works, in every block:

> **capability first, in the reader's language - then one hard clause of proof.**

**And "the reader's language" means a recruiter, not an oceanographer.** The first screening is
done by someone who has never opened an ocean tool. A card they cannot parse in four seconds
scores nothing, however true it is. Test every line on slide 2 against that reader:

| Too clever | What they read |
| --- | --- |
| "It answers machines as well as people" | "Works with their tools" |
| "Zero network calls at demo time" | "It keeps running if the internet drops" |
| "OPeNDAP, CF-1.8 NetCDF and OGC WMS" | "the standard ocean formats" - the acronyms live on slide 3 |
| "matching INCOIS's published values in 97% of cells" | "matching INCOIS's own published values 97% of the time" |
| "a GPU ray-marched water column" | "a solid block of water you dive into and turn" |

**Acronyms are allowed on slide 3 and nowhere else.** A technical reader goes to the technical
slide looking for them; on slide 2 they are a wall.

| Drifted | Rewritten |
| --- | --- |
| "Checked against INCOIS's own" | "Cyclone fuel, mapped in 3D - matching INCOIS's own published values in **97% of cells**" |
| "Honest about gaps" | "It shows where nobody has measured - which is where the next float is worth deploying" |
| "The picture and the truth are kept apart" | "It answers machines as well as people: OPeNDAP, CF-1.8 and WMS out" |
| "It refuses to invent" | "Nothing on this screen is guessed" |

The limits are all still in the deck. Slide 4 is five risks and what was done about each, and
slide 5 says a tenth of this ocean has no measurement behind it. **They belong there** - on the
slides whose headings are feasibility and impact - and not in the innovation block.

**A competitor deck will out-promise this one, every time.** Theirs can list crowdsourcing, SOS
alerts and ML anomaly detection because none of it has to work yet. The answer is not to match
the promise count; it is to be the only deck in the pile whose live link opens. Put the link
where a judge sees it in the first ten seconds, and let the capabilities be concrete.

---

## The scoring, and what each fifth is actually asking

Five criteria, **20% each**. A deck that is excellent at three and absent at two scores worse
than one that is solid at all five, which is why the weakest slide is the one worth working on.

| Criterion | What a judge is looking for | Where this deck answers it |
| --- | --- | --- |
| **Problem-solution fit** | Every feature traced to a clause of the PS. Named beneficiaries. A measurable outcome, not an adjective. | Slide 2's five-gap table, and the "who it is for" line under it. |
| **Innovation and uniqueness** | A novel approach, and an honest comparison with what already exists. | Slide 2's four innovation points, and slide 6's related-work paragraph. |
| **Technical depth** | An architecture diagram. Data flow in, processing, out. Realistic choices, justified. | Slide 3, which is one diagram and a justified stack. |
| **Feasibility** | Buildable, resourced, scalable past a prototype, with risks named and mitigated. | Slide 4: three feasibility boxes, scale and demand, then five risks with what was done. |
| **Presentation quality** | Visuals over paragraphs. Plain language. No errors. Ideas that connect. | Every picture is the real software. No stock photography, no picture of text. |

**The advantage this project has, and must not waste:** four of those five are usually promises.
Here they are demonstrable, because the thing exists and is on the internet. Put the link where a
judge sees it in the first ten seconds.

---

## Mechanical eliminations - checked before anybody reads a word

These are not judgements. They are filters, and every one of them is a rejection with no appeal.

- **Wrong file format.** Export to PDF.
- **More than six slides**, or the official template's structure modified. Six, in order.
- **A missing mandatory field on slide 1**: PS ID, exact PS title, theme, category, Team ID, team
  name, **college name and location**. The PS ID must match sih.gov.in character for character.
- **The team name containing the college name.** It may not.
- **Late.** The deadline is 30 September 2026.
- **More than two problem statements** applied to, or no SPOC approval.
- **A broken link.** Check the live URL and the video URL on a machine that is not yours.

---

## The content failures that get decks dropped

- **A generic solution.** "Another dashboard." The fix is the narrow, defensible claim, not the
  grand one - see slide 6's related-work paragraph.
- **Unrealistic scope.** Promising what cannot be built. The opposite risk here: this deck can
  *under*-claim, because everything on it is already running.
- **No evidence.** "Trust us." Every figure on this deck is on a public provenance page.
- **Buzzword overload.** No AI, no ML, no blockchain - and there is none in this project, which
  is a point worth making out loud rather than hiding.
- **Jargon with no explanation.** "Thermocline" gets three words of explanation the first time.
- **A picture of text.** Only screenshots go in as images. If it is words, type the words.

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

- **A number on our own error**, printed separately for floats (the analysis is built from them) and moored
  buoys - this is the differentiator and it should be on the first slide, not the fifth
- A **live deployed link** and a **public defect list**
- Every figure on the deck **generated from the build** ([`FACTS.md`](FACTS.md)), so nothing on
  screen can go stale
- A **requirements page** that answers each PS clause and links to the control that does it

What we have to actively resist:

- We have 19 variables and 16 probes and 495 tests. **That is feature-dump ammunition.** Mention
  them as evidence of rigour, once, and move on.
- The rendering is impressive and it is the *least* important thing about the project. If the
  demo becomes a graphics showcase, the argument is lost.

---

## Sources

Community posts from SIH judges and multi-time SIH winners, collected September 2026. The
consistent message across all of them: **presentation is as important as innovation, and most
teams lose here rather than in the code.**

---

# SIH 2026 Idea-Submission PPT Audit Rubric - for "OceanVerity" (PS SIH26067, INCOIS / Ministry of Earth Sciences)

## TL;DR
- The SIH idea PPT is judged by *reading*, not presenting: at the national screening stage nobody pitches and no demo is seen. Per SIH winner Zaid Sayyed, "Roughly five teams are shortlisted per problem statement nationally… On a popular statement that can mean 500 submissions competing for those five seats, decided entirely by your idea PPT with no jury to convince and no demo to save you." Clarity and PS-specificity beat cleverness.
- SIH mandates an exact 6-slide template (Title / Proposed Solution / Technical Approach / Feasibility & Viability / Impact & Benefits / Research & References), PDF-only, no format changes - but there is **no publicly published numeric scoring rubric**. The official evaluation *parameters* are documented verbatim in the SIH guidelines ("novelty of the idea, complexity, clarity and details in the prescribed format, feasibility, practicability, sustainability, scale of impact, user experience and potential for future work progression"), while every percentage weighting circulating online is a community reconstruction, not official.
- For an INCOIS/MoES problem, evaluators (a ministry officer + technical expert) reward operational deployability: differentiate against INCOIS's existing 2D/fragmented tools, cite real INCOIS data sources and open standards (OGC WMS/WCS, CF Conventions, OPeNDAP/NetCDF), keep the stack self-hostable on Indian government infrastructure, and tie impact to real INCOIS mandates (tsunami warning, Ocean State Forecast, fishery advisories, search-and-rescue).

## Key Findings

**1. The official template is fixed and minimal.** The SIH idea-submission template mandates a maximum of six slides *including the title slide*, with these headings: Title Page; Proposed Solution (Idea Title); Technical Approach; Feasibility and Viability; Impact and Benefits; Research and References. The official "Important Instructions" slide states verbatim: keep slides to a maximum of six (including title); avoid paragraphs, use points/diagrams/infographics/pictures; keep explanation precise; the idea should be unique and novel; use only the provided template without changing the idea-detail pointers; and save/upload as PDF only - "No PPT, Word Doc or any other format will be supported."

**2. Screening is a reading exercise with brutal odds.** Community sources (Reskilll) describe evaluators spending only 2–3 minutes per submission across tens of thousands of decks. Roughly 4–5 teams per problem statement are shortlisted nationally, and the problem-statement-issuing organisation makes the final call and is not obligated to select any winner if submissions don't meet expectations.

**3. Two distinct evaluation stages with different judges.** (a) The **internal college hackathon** is judged by faculty (sometimes with invited external judges) who decide nominations; per the SIH 2025 SPOC guidelines, "A max of 50 teams (45 Shortlisted + 05 Waitlisted) per college can be nominated (including Problem statement based/Student innovation category)." (b) The **national screening** is done by experts including ministry/PS-organisation representatives, reading the PPT (and, where required, a demo video). (c) The **grand finale** is a 36-hour offline build at a nodal centre where evaluators visit each table 3–4 times.

**4. Official evaluation parameters are published; weights are not.** Verbatim from the SIH 2025 Guidelines: "Evaluation criteria will include novelty of the idea, complexity, clarity and details in the prescribed format, feasibility, practicability, sustainability, scale of impact, user experience and potential for future work progression." No official percentage breakdown exists publicly. Blogs publish differing numeric rubrics - one (Anish Prashun, 2022 winner) gives Innovation/Novelty 20% / Technology 15% / MVP-Prototype 15% / Criticality-Impact 25% / Commercial viability & cost-effectiveness 25%; another (Reskilll) gives Problem understanding 20% / Innovation 25% / Feasibility 20% / Impact 20% / Presentation 15%. These are anecdotal reconstructions and disagree with each other, so treat any single weighting as unofficial.

**5. INCOIS/MoES problems reward operational realism.** The problem statement (SIH26067) explicitly states the gap: "no integrated, web-based 3D visualization platform currently exists that can simultaneously render model fields and in-situ instrument observations… Existing tools are either desktop-bound, support only 2D plan views, or lack the ability to co-visualize model outputs alongside instrument profiles." It mandates open standards (OGC WMS/WCS, CF Conventions for NetCDF) and browser-native deployability "on INCOIS infrastructure without any client-side dependencies." INCOIS's existing public tools are all 2D or fragmented, giving a clear differentiation story (see Details E).

## Details

### A. Hard rules that risk disqualification or automatic mark loss
Official (from template/guidelines) unless flagged as community advice.

- **Six slides maximum, including the title slide.** (Official.) A duplicated or extra slide making it seven pages is a common real-world error.
- **PDF only.** PPT/PPTX/DOC will not be accepted by the portal. (Official.)
- **Use the provided template; do not alter the mandated section pointers.** (Official.) Keep the five content headings intact.
- **Team composition:** per SIH 2026 rules, "Every team must have exactly six student members, including the team leader. At least one female student member is mandatory in every team." All six from the same college. (Official.) A missing female member is cited as a disqualifier.
- **Team name must be unique and must not contain the college/institute name in any form.** (Official.)
- **Deadline is hard.** For SIH 2025/2026 the portal nomination + idea-submission deadline was 30 September (Zaid Sayyed: "30 September 2026 for the portal submission"). Each PS freezes at 500 submitted ideas - SIH 2025 guidelines: "Idea submission counter will start from August 2025 and only 500 ideas will be submitted for a particular PS." The SIH26067 row on sih.gov.in/sih2026PS reads **30 September 2026** (checked 2026-09-14; the portal says the deadline was extended, and community mirrors still show 20 September). A team may submit against a maximum of 2 problem statements. Only teams cleared through the internal hackathon can be nominated by the SPOC.
- **Delete the "Important Instructions/Pointers" slide** before uploading (the template explicitly permits deletion). Leaving template placeholder text ("IDEA TITLE", "YOUR TEAM NAME", "TO BE UPDATED") on slides is a frequently cited red flag. (Community.)
- **Theme/PS metadata must match the portal exactly.** A wrong theme on the title slide is "the cheapest mark you will ever lose" per Zaid Sayyed. (Community.)

**Note on the "10-slide" confusion:** Some blogs (e.g., Reskilll) present a 10-slide structure. This is **not** the official idea-submission format - the official portal template is **six** slides. For the national idea submission, follow six.

### B. Evaluation criteria - what "good" looks like
Mapped to the official parameters. "Good" descriptions blend official language with winner/mentor advice (flagged).

- **Novelty / uniqueness:** Not "a platform combining AI and data." Name the specific gap only you close. For SIH26067: browser-native 3D volumetric co-visualization of model fields *and* in-situ Argo/Glider profiles in one interactive scene - which no current INCOIS tool does.
- **Complexity / technical depth:** Name concrete technologies, not categories. "WebGL/Three.js or Cesium.js for volumetric rendering; xarray/PyNIO NetCDF parsing; REST/OPeNDAP backend" beats "HTML, CSS, JS + AI/ML layer." Evaluators check that named tech is real and defensible. (Community consensus + PS text.)
- **Clarity & completeness in prescribed format:** One key message per slide; bullets/diagrams over paragraphs. (Official.)
- **Feasibility & practicability:** The single most-differentiating slide per winners. Show you know where your idea is weak - list 3 real risks with mitigations (data access, accuracy/performance at scale, adoption). A slide with only reasons it will work reads as naïve. (Community - strong consensus.)
- **Sustainability / future scope:** Who maintains it after graduation; extensibility (the PS asks for plugin-style addition of new sensors/variables). Show a phased pilot → scale → integrate roadmap.
- **Scale of impact:** Quantify. One number with visible working (beneficiaries, forecaster time saved) beats adjectives like "better/faster." (Community.)
- **User experience:** Show it's usable by the actual operator (INCOIS forecaster) and, per the PS, usable for public outreach/education.

### C. Common reasons for rejection (community/anecdotal unless noted)
- Solving a generic/adjacent problem instead of the exact PS. Anish Prashun (2022 winner), verbatim: "Carefully study and address every word in the official problem statement. If you drift away from this, even a great solution won't get selected. This is non-negotiable." Not addressing the PS's own listed gaps is a top failure mode.
- Buzzword tech with no integration story; "we'll use AI" without how.
- Text-heavy slides, no numbers, vague promises.
- No prototype evidence - no screenshot, no video, no demo link. (Especially damaging given you already have a deployed prototype - not showing it wastes your biggest edge.)
- Recycled/obviously AI-generated generic content; copying a past SIH solution.
- References that name nothing ("government datasets," "research literature") or framework docs passed off as research.
- Formatting traps: placeholder text left in; wrong theme; duplicated slide (7 pages); title text running off the slide; a free-host demo link that sleeps and shows a blank page to the evaluator.
- Missing female member; late submission; wrong track/category.

### D. Slide-by-slide checklist for the 6 mandated slides (tailored to OceanVerity / SIH26067)

**Slide 1 - Title Page.** PS ID (SIH26067), exact PS title, Theme, PS Category (Software), Team ID, Team Name (as registered) - copied character-for-character from the portal. No placeholder text. Optional: one-line tagline ("OceanVerity - browser-native 3D ocean visualization for INCOIS forecasters").

**Slide 2 - Proposed Solution / Idea Title.** Name the specific INCOIS pain in the PS's own words: forecasters must "switch between multiple tools, slowing operational analysis," and cannot co-visualize model fields with instrument profiles. State your solution: browser-native interactive 3D ocean visualization integrating numerical model outputs (temperature, salinity, currents, chlorophyll) with Argo/Glider in-situ profiles across the full water column. State the differentiator and that a **working deployed prototype exists.** Test: if you could swap "ocean" for another domain and the slide still reads fine, it's too generic.

**Slide 3 - Technical Approach.** Architecture diagram (input NetCDF/ASCII → parser via xarray/PyNIO → REST/OPeNDAP backend → WebGL/Three.js or Cesium.js 3D frontend). Name the real stack you deployed. Show depth-slice / isosurface / time-animation / customizable-colorbar controls. **Include a prototype screenshot here** - you have one deployed; use it. Cite the open standards the PS demands: OGC WMS/WCS, CF Conventions for NetCDF, OPeNDAP.

**Slide 4 - Feasibility & Viability.** Prove buildability (prototype already live). List 3 real risks + mitigations: (i) ingesting large NetCDF volumes / performance across the full water column → tiling, downsampling, server-side subsetting; (ii) live INCOIS data access needing clearance → generate a realistic dataset modelled on the official NetCDF/CF schema meanwhile, and show the schema; (iii) deployability on INCOIS infra → self-hostable open-source stack, no client-side dependencies, no commercial-API lock-in (mirrors how INCOIS already self-hosts ODIS on MySQL/MapServer/OpenLayers and runs its own ERDDAP/LAS). Name which existing INCOIS systems it would talk to.

**Slide 5 - Impact & Benefits.** Tie to real INCOIS operational mandates named in the PS: hazard/tsunami assessment (Indian Tsunami Early Warning Centre, an IOC-UNESCO Regional Tsunami Service Provider), search-and-rescue support, fishery advisories (Potential Fishing Zone advisories reach 100,000+ fisherfolk), Ocean State Forecast, climate monitoring - plus public outreach/education (the PS explicitly values this). You may cite scale context from the PS: India's EEZ spans ~2.37 million km². Quantify where honest. Name the day-one owner/user (INCOIS forecaster).

**Slide 6 - Research & References.** Named, linked sources only. Use real INCOIS sources: INCOIS portal (incois.gov.in), INCOIS Live Access Server (las.incois.gov.in), INCOIS ERDDAP (erddap.incois.gov.in), ODIS (odis.incois.gov.in), the Indian Argo Project (incois.gov.in/argo), the INCOIS-GODAS model (GFDL MOM4.0-based), and the standards (OGC WMS/WCS, CF Conventions - cfconventions.org, OPeNDAP - opendap.org, NetCDF). State existing tools studied and exactly how you differ. Add one line of team roles if space. Never write "government datasets."

### E. INCOIS-specific differentiation intelligence (use to make slides concrete)
INCOIS's three existing public tools split the problem the PS wants unified:
- **INCOIS Live Access Server (I-LAS)** - serves gridded satellite/model data (SST, chlorophyll, winds, GODAS-MOM); produces **2D static plots/maps, time-series, Hovmöller** - no interactive 3D volumetric rendering.
- **INCOIS ERDDAP** - data-access/download server with WMS 1.3.0 and basic 2D "Make A Graph"; **not a 3D environment.**
- **Ocean Data and Information System (ODIS)** - 2D Web-GIS (OpenLayers/MapServer) for **in-situ** data, handled on a *separate* pipeline from gridded model data.

The differentiation line for Slide 2/4: none of INCOIS's tools offers browser-native interactive 3D volumetric co-visualization of model fields *and* in-situ profiles together - this tri-partite fragmentation is the justification for OceanVerity. On deployability, note government data-residency expectations (NDSAP 2012 governs MoES/INCOIS data release; MeitY MeghRaj/GI-Cloud implies in-India data centres), reinforcing a self-hostable, no-foreign-SaaS design.

### F. Timeline / logistics facts (flag edition)
- **Editions:** SIH 2026 is the software/hardware national competition run by the Ministry of Education's Innovation Cell (MIC) with AICTE. Problem statements went live around late August 2026; grand finale expected December 2026 (nodal centres). (2026, but confirm exact dates on sih.gov.in.)
- **Quota:** 50 teams max per college (45 shortlisted + 5 waitlisted). (SIH 2025 guidelines; carried into 2026 community guides.)
- **Per-team PS limit:** a team may submit against a maximum of 2 problem statements. (SIH 2024/2025/2026 college docs.)
- **PS cap:** each PS freezes at 500 submitted ideas. (SIH 2025.)
- **Internal hackathon is mandatory** before nomination; SPOC uploads the deck (and, where required, a demo video) for national screening.
- **Prize:** ₹1,00,000 per problem statement at national level (some editions/categories cited at ₹1,50,000). (Community; confirm.)

## Recommendations
1. **Immediately fix any hard-rule violations** in your current 6-slide deck: confirm exactly 6 slides, PDF export, exact PS metadata on the title slide (ID SIH26067, correct theme), no placeholder text, no leftover instructions slide, unique team name, female member present. These are the cheapest possible marks.
2. **Convert your deployed prototype into your single biggest advantage.** Put a real screenshot on the Technical Approach slide and ensure any live link is on always-on hosting, not a free tier that sleeps. Most competing decks describe an idea that doesn't exist; yours exists - make that undeniable in the first 30 seconds of reading.
3. **Rewrite the Feasibility slide to lead with 3 risks + mitigations** and name INCOIS systems and the mandated open standards. This is the slide winners repeatedly say separates otherwise-equal decks.
4. **Make every slide pass the "swap test"** - if a sentence would be equally true for a different ministry/domain, replace it with an INCOIS-specific fact (a named tool it beats, a named data source, a named operational mandate).
5. **Populate the References slide with named INCOIS sources and open standards** (Details D6/E). Explicitly state how you differ from I-LAS, ERDDAP and ODIS.
6. **Benchmarks that change the plan:** If SIH26067's counter is nearing 500, submit immediately (freeze risk) - and the portal shows 30 September 2026 for SIH26067 (checked 2026-09-14). If your internal hackathon date is imminent, the internal deck may carry more prototype detail and Q&A backup; the national PDF must stay at six slides.

## Caveats
- **No official numeric scoring rubric is published.** Every percentage-weighted rubric online is a community reconstruction, and they contradict each other. Only the qualitative parameter list (quoted above) is official.
- **Much practical advice here is anecdotal**, drawn from past winners/mentors (Zaid Sayyed, Anish Prashun), college guidance PDFs and coaching blogs (Reskilll, Apnijanta). It is credible and internally consistent but is not official SIH rule text.
- **Some facts are from earlier editions (SIH 2023/2024/2025)** and may change for 2026 - notably exact dates, the 50-team/45+5 quota, the 500-ideas-per-PS cap, and the 2-PS-per-team limit. Verify current values on sih.gov.in.
- **The SIH26067 problem-statement text was read from community mirrors** of the official portal (wording is consistent across mirrors); confirm exact wording, deadline and dataset links on sih.gov.in/sih2026PS before finalising slides.
- **A demo video may be required at national submission** in addition to the PPT; some 2026 college portals state the demonstration video and its narration must not be AI-generated and must be delivered by team members. Verify your college/portal's specific requirement.
- INCOIS operational figures (e.g., "100,000+ fisherfolk," RTSP designation, EEZ ~2.37 million km²) come from INCOIS pages, peer-reviewed reports and the PS text; treat exact counts as as-of-report-date and cite the primary INCOIS/PS source on slides, not aggregators.
