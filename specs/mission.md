# Project Mission & Philosophy

> **Target Directory:** `specs/mission.md`  
> **Audience:** Development Agent & Engineering Team  
> **Status:** Foundational / Inviolable  

---

## 1. Executive Summary & Purpose

Modern digital consumers engage in an immense volume of enriching media and activities every day: watching movies, binging series, reading books, tracking comics/manga/anime, listening to audiobooks, and maintaining workout regimens. 

Yet, due to fragmented platforms and cognitive overload, the user reaches the end of the day, month, or year feeling an acute sense of emptiness—feeling as though time slipped away without tangible progress or meaningful consumption.

**Our Core Tenet:**  
> **"Help the user remember what they did, understand how they spend their life, and reclaim a sense of personal accomplishment."**

This constitution governs the design, engineering priorities, user experience, and architecture of **uTrack**. Every feature must serve the goal of turning ephemeral consumption into a coherent, self-reflective personal chronicle.

---

## 2. The Persona & Problem Space

### 2.1 The Target User
- **The Modern Omnivore:** Consumes diverse media across fractured channels (Netflix, Goodreads, Kindle, Spotify, Crunchyroll, local gyms, paperbacks).
- **The Pain Point:** High engagement, zero retention. At the end of the month, the question arises: *"Where did my time go? What did I actually accomplish?"*
- **The Emotional Toll:** Amnesia of personal milestones, leading to feelings of unproductivity, guilt, and disorganization.

### 2.2 The Solution Commitment
1. **Low Friction Logging:** Tracking must not feel like homework.
2. **Comprehensive Scope:** Unify movies, series, books, audiobooks, comics, anime, physical habits, and activities in one consolidated dashboard.
3. **Automated Enrichment via Open APIs:** Leverage public metadata catalogs (e.g., Open Library, TMDB, AniList, etc.) so users never have to type mundane metadata (posters, synopsis, release dates, authors, directors) manually.
4. **Insightful Retrospectives & Visual Proof of Life:** Provide intuitive monthly/weekly summaries, timeline logs, and a GitHub-style daily activity heatmap that visually validates their consistency and engagement with clarity and pride.

---

## 3. Constitutional Directives for the Agent

When designing or implementing any subsystem in uTrack, the agent must uphold the following non-negotiable standards:

### Directive I: Zero-Friction Input & Open Metadata Integration
- Users should search or pick an item and immediately track it.
- Prioritize integrations with open, standard databases and APIs.
- The system must enrich entries behind the scenes without demanding manual data entry for standard attributes.

### Directive II: Meaningful Temporal Views & Visual Activity Graphs
- Temporal grouping is a first-class citizen.
- Every entry must easily tie into timelines, calendars, retrospective summaries, and a daily activity heatmap (GitHub-style calendar grid) so users can at any glance see: *"This is what I did in October; here are all the days I showed up."*

### Directive III: Universal Activity Extensibility
- Media is the foundation, but the system must accommodate holistic life activities (e.g., fitness, hobbies, personal projects).
- Data schemas must remain flexible enough to handle varied consumption models (read chapters/pages, watch episodes/runtime, workout sessions).

### Directive IV: Respect for User Ownership & Privacy
- This tracker is a deeply personal reflective space.
- Data structures and exports must be transparent, user-owned, and reliable.

---

## 4. Operational Checklist for Future Features

Before building or accepting any feature or PR, evaluate it against these questions:
- [ ] Does this make logging faster and less tedious for the user?
- [ ] Does it automatically populate rich metadata via external databases/APIs?
- [ ] Does this contribute directly to the user's retrospective clarity (monthly/yearly summaries)?
- [ ] Does the UI communicate reassurance and accomplishment rather than stress and checklist fatigue?

---
*Signed and enforced by the autonomous development agent as the guiding benchmark for all decisions.*
