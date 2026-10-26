---
post_id: "2026-10-27-001"
muse_account: "muse-01"
language: "en"
revision: 1
status: "ready"
title: "Vibe Coding Fails Without Principles｜What a 90-Minute Masterclass Really Teaches"
category: "AI 뉴스"
platform_categories:
  wordpress-en: "AI News"
  blogger-en: "AI News"
targets: ["wordpress-en", "blogger-en"]
tags: ["VibeCoding", "AICoding", "CodingBasics", "ArtificialIntelligence", "AINews", "ClaudeCode", "Cursor", "SpecDrivenDevelopment", "AIProductivity", "AITools"]
action: "publish"
visibility: "public"
timezone: "Asia/Seoul"
editing: "format_only"
cover_image: "images/01-hero-en.jpg"
result:
  url: ""
  completed_at: ""
  note: ""
---

<!-- 본문 시작 -->

![Vibe coding fails without principles](images/01-hero-en.jpg)

Just tell the AI and an app appears?
At first, it really does.
But add a few features and it stalls fast.
Vibe coding does not stall because of the tool. It stalls because you don't know the principles.
The 90-minute masterclass boils down to one line.
Before you pick a tool, learn how software actually works.

> **Key takeaway: Vibe coding means describing a goal in plain language, letting AI write the code, and judging only by running it. Andrej Karpathy named the concept in February 2025: the developer shifts from writing code to requesting and reviewing it. The catch is that without review criteria, bugs, structural collapse, and security holes all pass through. So the right order is principles, then tools, then verification.**

## What exactly is different about vibe coding?

![See, say, run](images/02-img1-en.jpg)

Vibe coding is not just asking AI to write code.

In traditional development, people write the code and AI assists on the side.
Vibe coding reverses the order.
People state a goal in plain language, AI writes the code, and people skip reading it closely, judging only by running it and giving the next instruction.
Karpathy's flow is three verbs: see stuff, say stuff, run stuff.

The boundary matters.
If a person understands and reviews AI-written code, that is closer to typing assistance than vibe coding.
Real vibe coding includes the tendency to skip review in its definition.
That is why it is fast.
And that is why it is risky.

Its strong areas are clear.
Personal automation tools, internal operations helpers, one-off data cleanup scripts, clickable prototypes, demo screens.
Results where "roughly right" is good enough.
Short loops of instruct, run, and feedback are the core.

## Why learn principles first?

![No map, no fix](images/03-img2-en.jpg)

Vibe coding stalls in familiar ways.

The screen AI made looks fine, but pressing a button throws an error from somewhere unexpected.
Adding one feature breaks a feature that worked.
Not knowing where to fix it, you repeat "just fix it" until the app is no longer what you intended.
That is not an AI performance problem. It is sailing without a map.

At minimum, you need this map.
How the screen (frontend), server (backend), and data store (database) split apart and talk through APIs, which are agreed promises between parts.
Where a request goes when a user presses a button, and where it gets saved.
Why sensitive features like login and payments cannot just be "attached," and why authentication and authorization are separate things.

Principles let you judge AI answers.
You gain a standard to ask "why is this code written this way" and to stop AI when it heads the wrong way.
Without principles, you have no choice but to trust a plausible-looking answer.
Most vibe coding failures start here.

## How do you pick tools and verification?

![Verification before tools](images/04-img3-en.jpg)

Pick tools to match your level.

If you don't know code at all, start with web tools that build an app from a description alone.
Lovable and Google AI Studio fit here.
If you are comfortable with code, agent-style tools like Cursor and Claude Code edit many files at once and run commands for you.
A tool above your level eats your time just reading its manual.

But verification matters more than tools.
Build in small steps, run and check at each step, and attach automated checks called tests to important features.
Spec-driven development follows the same logic.
Writing "what to build" as a spec first keeps direction steady even as the conversation grows long.
The spec stops vibe coding from drifting like an endless chat thread.

There is also a number to respect.
In a 2025 METR study, experienced developers working on a familiar codebase took 19% longer with AI tools allowed, because review and fixes took time.
"Always faster" is a false premise.
High-security systems like finance and healthcare, and large codebases shared by many people, should not take raw vibe coding.
Speed and verification both have to be chosen.

---

| Item | Vibe coding | Spec-driven development |
|---|---|---|
| Starting point | Vague prompt | Clear spec |
| Developer role | Instructor | Designer and reviewer |
| Speed | Very fast prototypes | Slower start, steadier direction |
| Risk | Hidden bugs and tech debt pile up | Cost of writing the spec |
| Fits | Personal tools, demos, one-off scripts | Products to maintain, shared code |

---

What struck me while organizing this material is that "fast" is only half the story.
Building the first version is definitely fast.
But once fixing and maintaining are added, the story changes.
So before handing work to AI, I plan to first ask where a feature is stored and who can see it.
Tools will change again next month.
What remains is the eye that reads the flow.

## Frequently asked questions

**Q. Can I build an app with vibe coding without knowing code at all?**

A. Prototypes and personal tools, yes. But putting a public service out requires principles like authentication, security, and maintenance, and review becomes essential at that stage.

**Q. Which tool should I start with?**

A. With no code experience, start with web tools that build from a description. With code experience, start with agent-style IDEs or terminal tools. A tool matched to your level matters.

**Q. Does vibe coding always raise productivity?**

A. No. A 2025 METR study reported cases where experienced developers took longer. It is strong for fast exploration, but review and fix costs must be counted too.

## Further reading

[How to Hand Work to AI Without Knowing How to Code｜GPT Codex and Aside Setup Guide — from one terminal line to a browser that works for you](https://aitechnotesen.blogspot.com/2026/10/how-to-hand-work-to-ai-without-knowing.html)
[Open Weights Reach the Frontier's Doorstep｜Kimi K3.1 Pro and the November 4 Test — intelligence index 55, ranked 4th overall, and the fine print before weights drop](https://aitechnotesen.blogspot.com/2026/10/open-weights-reach-frontiers.html)
[AI Video You Download and Run Yourself｜Why LTX-2.5 Changes the Game — the fork between renting a model and owning one](https://aitechnotesen.blogspot.com/2026/10/ai-video-you-download-and-run.html)

<!-- 본문 끝 -->

## 작업용 출처·이미지 정보 (업로드 제외)

- 자료 출처: honjobs '바이브코딩 원리는 알고 하세요' (2026-10-26) / Karpathy 2025-02 concept, METR 2025 study, spec-driven development references via web research
- 이미지: images/01-hero-en.jpg ~ 04-img3-en.jpg / 직접 제작 (AI 생성 + 영어 오버레이) / 사용권: 자작
- 참고: 자막 원문 확인 작업 진행 중, 자막 도착 시 원고와 대조해 정정 여부 판단
