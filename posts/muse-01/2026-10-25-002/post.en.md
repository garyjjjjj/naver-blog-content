---
post_id: "2026-10-25-002"
muse_account: "muse-01"
language: "en"
revision: 1
status: "ready"
title: "How to Hand Work to AI Without Knowing How to Code｜GPT Codex and Aside Setup Guide"
category: "AI 뉴스"
platform_categories:
  wordpress-en: "AI News"
  blogger-en: "AI News"
targets: ["wordpress-en", "blogger-en"]
tags: ["GPTCodex", "Aside", "CodingAgent", "AIBrowser", "ArtificialIntelligence", "AINews", "Automation", "AIProductivity", "GenerativeAI", "AITools"]
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

![Hand work to AI without coding](images/01-hero-en.jpg)

You do not need to know how to code to hand work to AI.
There is GPT Codex, which writes code for you, and Aside, a browser that does web work itself.
Use them together and "write this code" becomes "finish this job for me."
Here is the beginner's path, from install to first task, in order.

> **Key takeaways**
>
> **GPT Codex** is OpenAI's coding agent. Type `codex` in a terminal and talk to it — it writes, fixes, and tests code for you. It is included in every ChatGPT plan.
> **Aside** is an AI-native browser built by a Korean team. It keeps your logged-in browser session and lets AI look at screens and click like a person, handling crawling, booking, and shopping tasks. It currently runs on macOS only.
> Split the work: Codex takes the code, Aside takes the web clicks. That division is how beginners taste automation.

---

## GPT Codex — how do you install it?

![One line in the terminal](images/02-img1-en.jpg)

One line in the terminal, `codex`, starts the coding agent.

Codex comes in three forms.
A web version inside chat, a desktop app, and a CLI for the terminal.
For beginners who want to feel automation, the CLI is the best start. It installs with a single command.

On Mac and Linux, type this in the terminal:

`curl -fsSL https://chatgpt.com/codex/install.sh | sh`

On Windows, run the install script in PowerShell.
Or install with npm: `npm install -g @openai/codex`.
Once installed, open a project folder, type `codex`, and sign in with your ChatGPT account.

Check your plan first.
Codex itself is included in every ChatGPT plan, including Free and Go.
But Codex Cloud — long-running jobs in the cloud — is only for Plus and higher (Pro, Business, Enterprise, and similar). Free and Go do not include it.
Start with the local CLI, and add the cloud later only if you need it.

Keep the first task small.
Try a safe request like "organize the file list in this folder."
Build the habit of reviewing what Codex wants to change and approving only what you checked.

---

## Aside — a browser that does the work itself

![A browser that works itself](images/03-img2-en.jpg)

Hand your logged-in browser to AI and web tasks run on their own.

Aside is not a browser extension — it is the browser itself.
It is a Chromium-based local AI browser built by a Korean team backed by Y Combinator.
Download it from aside.com; it currently runs on macOS only.

The key idea is that it keeps your login session as-is.
AI opens your already-logged-in YouTube Studio or Instagram dashboard just as you left it.
Connect a model like Claude or Codex from the terminal, and the AI reads the tab's screen, scrolls, and clicks.
It clears barriers like CAPTCHAs the way a person would, and saves results as Markdown or JSON in your folder.

For beginners, the uses are easy to picture.
Gathering rival channels' latest view counts every morning, checking shopping-mall prices regularly, or handling repetitive input on an admin page.
Even where there is no API or where login blocks access, it imitates "a person looking and clicking" to get the job done.
You can connect several models, including Claude, Codex, DeepSeek, and Kimi.

The cautions are just as clear.
Your login information lives in that browser, so set the scope of what you hand over.
Start with Read-only or Guard mode, which stops the AI from paying or deleting on its own.
Using a separate testing profile, so real service data stays untouched, is another good habit.

---

## What changes when you use both together?

![Turn the guard on first](images/04-img3-en.jpg)

Code to Codex, web clicks to Aside — a clean division of labor.

Either one alone is only half the job.
Codex writes code well but cannot wander through your logged-in websites.
Aside navigates the web well but does not design complex code work.
So divide the labor.

Here is one example flow.
Aside gathers rival channels' view counts and comments; Codex turns that data into a report script.
Or Codex builds an automation script, and Aside runs it on the real site to verify the result.
One becomes the eyes (the web), the other the hands (the code).

The starting order looks like this.
1. Install the Codex CLI with your ChatGPT account and try a small task first.
2. On macOS, install Aside and open a logged-in page with a testing profile.
3. In Read-only mode, start with a safe job like "collect only the prices from this page."
4. Check the results yourself, then widen the scope little by little.

---

Honestly, at first I wondered, "Can I even use this?"
The word "terminal" alone was intimidating.
But one line — `codex` — and one sentence — "collect this for me" — and the first automation runs sooner than you expect.
The point is not perfect automation. It is starting small and checking the results yourself.
Learning how to hand work to AI is the beginner's first step.

## Frequently asked questions

**Q. Can I use Codex if I cannot code at all?**

A. Yes — you ask in words. But do not trust the result blindly. Check what it wants to change and approve it. Start with small tasks.

**Q. Does Aside work on Windows?**

A. It is currently macOS-only. Windows users should start with the Codex CLI and add Aside later if a Mac is available.

**Q. Is it safe to hand my login information to AI?**

A. Convenience comes with risk. Start with Read-only and Guard modes and a separate testing profile. Hand over payment or deletion tasks only after you have checked them yourself.

## Further reading

[The AI Assistant That Moves Before You Ask｜Claude Duet and This Week's AI News — from morning briefings to payroll prep, connected to 6,000+ apps](https://aitechnotesen.blogspot.com/2026/10/the-ai-assistant-that-moves-before-you.html)
[AI Video You Download and Run Yourself｜Why LTX-2.5 Changes the Game — rented models versus owned models](https://aitechnotesen.blogspot.com/2026/10/ai-video-you-download-and-run.html)
[AI That Films in 30-Second Takes｜Kling 4.0 Official Launch — the monster model with 30-second long takes and 15 references, now on real film sets](https://aitechnotesen.blogspot.com/2026/10/ai-that-films-in-30-second-takeskling.html)

<!-- 본문 끝 -->

## 작업용 출처·이미지 정보 (업로드 제외)

- 자료 출처: Shin Yeongseon AI guide 'GPT Codex & Aside install and use' (2026-10-24) / OpenAI help docs (Codex in ChatGPT plans, CLI install) / Aside product info (aside.com, Korean team, YC-backed, macOS only)
- 이미지: images/01-hero-en.jpg ~ 04-img3-en.jpg / 직접 제작 (AI 생성 + 영어 오버레이) / 사용권: 자작
