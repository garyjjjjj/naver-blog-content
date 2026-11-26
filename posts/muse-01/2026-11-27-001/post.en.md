---
post_id: "2026-11-27-001"
muse_account: "muse-01"
language: "en"
revision: 1
status: "ready"
title: "7 New Claude Features｜What Changed in Meetings, Sheets, and Data"
category: "AI 뉴스"
targets: ["wordpress-en", "blogger-en"]
tags: ["Claude", "Anthropic", "ClaudeFeatures", "ClaudeMeetings", "ClaudeSheets", "ClaudeData", "Fable52", "ClaudeWhiteboards", "AINews", "ClaudePricing"]
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

![저녁 회의실 대형 화면의 AI 인터페이스 앞에서 협업하는 사람들](images/01-hero-en.jpg)

Claude is pulling paid apps inside itself, one by one.
Meeting notes, whiteboards, spreadsheets, and data dashboards all arrived in the November update.
This post covers what each of the seven features does, whether your plan can use it, and where to turn it on.

```blog
type: text
runs:
  - text: "The heart of Claude's November update is simple: work that used to mean copying things out and pasting them back in can now finish inside Claude. Meetings, whiteboards, sheets, data, connected apps, themes, and a way to save on the priciest model all arrived at once, but only the connected-app view works on the Free plan. Check your plan first for the rest."
    style: {bold: true, color: "#007aa6"}
```

You can check what each plan includes in [Claude Pricing Compared｜Free, Pro, Max, and Ultra Prices and Limits](https://aitechnotesen.wordpress.com/2026/11/26/claude-pricing-compared%ef%bd%9cfree-pro-max-and-ultra-prices-and-limits/). Knowing which tier unlocks each feature makes the seven below much faster to sort through.

```blog
type: heading
level: 2
runs:
  - text: "Can meetings and brainstorming end inside Claude?"
    style: {bold: true, color: "#007aa6"}
```

![First is Claude Meetings.](images/02-img1-en.jpg)

First is Claude Meetings.
Claude joins a video call as a visible participant, takes notes, and answers questions.
It does not listen in secret. Everyone in the meeting can see it there.

It arrived in beta on November 12, 2026, and for now only Team and Enterprise plans can use it.
If you are on Pro alone, you cannot use it yet.
Only Google Meet works for now, and other meeting apps are coming later.

Turning it on is simple.
Open Meetings in the left menu and connect Google Calendar once.
On a company account, an admin has to allow the Google Calendar connection first.
Then pick a meeting, press Add Claude, and Claude joins when the meeting starts.

During the meeting, you can call Claude by name or type a question in the Meet chat, and it answers in writing.
Ask it to summarize what has been decided so far at the end of a client meeting, and it works from what was said up to that point.
It can also pull in material from other connected apps, but only within the permissions each person has.
While the meeting runs, you can build a document or a whiteboard together and edit it live.

When the meeting ends, each meeting gets its own page.
The summary, action items, transcript, and everything made during the meeting sit in one place, so there is nothing left to copy over afterward.
One thing to know: voice recordings are not kept. Only the written record remains.
Claude can stay in a single meeting for up to 8 hours.

```blog
type: text
runs:
  - text: "Claude Meetings is a participant, not a recorder."
    style: {bold: true, background: "#FFF3CD"}
  - text: " It takes notes and answers where everyone can see it, which is what sets it apart from ordinary meeting summary tools. But it is limited to Team and Enterprise plans, so personal plan users cannot turn it on yet."
```

Second is Claude Whiteboards.
The online whiteboard where you stuck Post-its and drew arrows now lives inside Claude.
It follows documents, slides, and design, which arrived in September, as one more thing you can make directly inside a conversation.

It arrived in beta with the November 10 announcement, and paid plans from Pro up can use it.
The Free plan cannot use it yet.
Until now, brainstorming with Claude produced long stretches of text. On a whiteboard, what you say, write, or roughly sketch gets organized into boxes and arrows.
There are two ways to start one.
Ask in chat to start a whiteboard, or pick Whiteboards in the Artifacts menu.
Pour out a plan for three videos next month in any order and ask Claude to organize it, and it spreads into a schedule with who does what and when.
If a board gets complicated, you can drag one part into a box, select it, and group or fix just that part.
Teammates can edit the same board at the same time, and photos and video can go on the board too.
A finished board can be turned into a document or a presentation on request.

There are limits, since it is still in beta.
Saving to a file produces a PNG image only, and boards cannot be imported from other files.
Sending a board to a whiteboard app like Lucid or Miro does work.

```blog
type: heading
level: 2
runs:
  - text: "Does Claude make tables and numbers itself now?"
    style: {bold: true, color: "#007aa6"}
```

![Third is Claude Sheets.](images/03-img2-en.jpg)

Third is Claude Sheets.
Claude makes tables like Excel or Google Sheets directly.
It arrived in beta with the November 10 announcement, and Pro plans and above can use it.

Ask in chat to make a table, or pick Sheets in Artifacts.
Ask for a target tab and an actual sales tab for this month, plus how much of the target was reached, and it builds both tabs with formulas linking them.
The point is that real formulas stay in the cells, not just numbers.
Click a number and you can see right away how the value was calculated.
More than 250 functions are available, and conditional coloring and charts work too.
When teammates edit the same table, the cells Claude changed get a border, so you can see what changed at a glance.

It helps to know the limits too.
Up to 500,000 populated cells fit in.
There are no dropdown lists or PDF export yet.
And Sheets cannot pull live numbers from a connected app.
For live numbers, the next feature is the right one.

Fourth is Claude Data.
The dashboards that arrived in beta in October changed their name to Data and launched properly with the November 10 announcement.
Pro plans and above can use it, and you first have to connect a place that holds numbers.
You can connect a data warehouse where company numbers sit together, such as BigQuery or Snowflake.

After connecting, pick Data in Artifacts and say what you want to know.
What changed this time is that the same numbers can come back in four shapes.
First is the familiar dashboard.
Second is a data story you read by scrolling down, good for explaining why this month's sales rose.
Third is a short video that walks through the numbers one by one.
Fourth is a written analysis report.
Say which shape you want in chat, and you can review it yourself before sending it to anyone.

Numbers refresh when someone opens the dashboard and it is time for a fresh pull.
They do not update on a fixed schedule by themselves, but you can set how often each dashboard refreshes.
Team plans get two more features.
One is real-time sharing, which lets colleagues see your numbers as they are without connecting separately.
The other lets you set a company formula, like a sales calculation, and attach a verified badge to charts made from it.
If you work alone, you do not need to know these two yet.

```blog
type: text
runs:
  - text: "Term: artifact "
    style: {bold: true, color: "#ff008c"}
  - text: "Something Claude builds beside the chat that you can open and edit separately. Documents, presentations, tables, and dashboards all count. Whiteboards, Sheets, and Data in this update all open inside Artifacts."
```

Fifth is a feature that opens an app you already use, whole, beside the chat.
Connecting apps like Notion, Canva, and HubSpot to Claude already worked.
Now the app's full screen opens beside the chat or in full screen.
You are already signed in, so you can edit directly inside it or ask Claude to edit it for you.
Everything Claude touches needs your approval one by one, and it cannot go beyond the permissions each person has.

Adobe, Atlassian, and Box company apps are opening first.
This works on every plan including Free, rolling out on web and desktop first.
Mobile is not supported yet.
To see whether an app you use works, check Settings, Connectors, and look for the Interactive label.

```blog
type: text
runs:
  - text: "The difference between Sheets and Data is make versus fetch."
    style: {bold: true, background: "#FFF3CD"}
  - text: " Sheets builds a new table inside Claude, while Data connects numbers that already exist and shows them as a dashboard. Check live numbers in Data, not Sheets."
```

```blog
type: heading
level: 2
runs:
  - text: "How do you save on the most expensive model?"
    style: {bold: true, color: "#007aa6"}
```

![Sixth is themes.](images/04-img3-en.jpg)

Sixth is themes.
It changes how the Code tab in the Claude desktop app looks, the way you want it.
Colors, light and dark screens, moving backgrounds, chat bubbles, fonts, and even sounds can change.
It runs on top of Modes, a feature that arrived in October.

To make one, describe the look you want in words in the Code tab and Claude builds it.
If building one yourself feels hard, Anthropic offers example packs.
There are 38 moving backgrounds now, including an ocean seen from above, cherry blossoms at night, a koi pond, and an airport departure board.
18 of them react to the mouse, and some, like the koi pond, make sounds too.
Type the custom theme command and a preview card appears, and you can set a different background per project.

What overseas users made is the fun part.
In one theme, the longer the conversation gets, the more snow falls, showing how much of what Claude can remember at once is filled.
It is not an official feature, but it shows what themes can do.
Themes are also modes, so they run with your computer's permissions.
It is safer to install only ones from sources you trust.
And backgrounds show only in the desktop app, not in Claude Code in the terminal.

The seventh and last is how to save on the most expensive model.
Fable 5.2, released on November 9, is the smartest model in Claude right now, but using the same amount costs twice as much as Opus 5.5.
Anthropic's official API pricing confirms it: Fable 5.2 costs $8 per million input tokens and $40 per million output tokens, while Opus 5.5 costs $4 and $20.
Anthropic itself advises starting everyday coding and work with Opus 5.5 and saving Fable for the hardest, biggest jobs.

That is where the advisor feature in Claude Code comes in.
The command is /advisor.
Sonnet or Opus normally does the work, and only before deciding a direction, when the same error keeps blocking progress, or right before saying the work is done, does it ask the smarter model.
The advisor reads the whole conversation so far and gives advice, and Claude decides when to ask.
Think of it like a company where staff do the daily work and only call an expensive consultant for important decisions.

Pick Fable once in the advisor and the setting is saved, so it carries over to the next task.
According to the official explanation, it is usually cheaper than using the expensive model from start to finish.
It fits long, multi-step work well, and for short tasks simply switching models is better.
It is still experimental.
Check your plan carefully.
Max and Ultra include Fable in usage, but Pro pays separately for how much Fable it uses.
The same applies when Fable is called only as an advisor.

| Feature | Release and status | Plans that can use it | What to know |
| --- | --- | --- | --- |
| Claude Meetings | Beta, November 12 | Team and Enterprise | Google Meet only, up to 8 hours, no voice files kept |
| Claude Whiteboards | Beta, November 10 | Pro and above | PNG export only, no import from other files |
| Claude Sheets | Beta, November 10 | Pro and above | 250+ functions, 500,000 cells, no PDF export |
| Claude Data | Launched November 10 | Pro and above | Live numbers in Data; Team-only sharing and verified badge |
| Open apps beside chat | Rolling out November 10 | All plans including Free | Web and desktop first, mobile not supported |
| Themes | Built on Modes from October | Desktop app | 38 backgrounds, desktop only |
| Fable 5.2 and advisor | Launched November 9, experimental | Included in Max and Ultra, Pro pays separately | Twice the API price of Opus 5.5 |

```blog
type: text
runs:
  - text: "Confirmed facts versus claims "
    style: {bold: true, color: "#ff008c"}
  - text: "Confirmed: the Anthropic release notes dates (Meetings beta November 12; monthly recap out of beta, install artifacts as apps, and send files to connected apps on November 24), the official API prices (Fable 5.2 at $8 input and $40 output, Opus 5.5 at $4 and $20), and the Fable 5.2 launch date of November 9. The video presenter's walkthrough (how the advisor works, 38 themes, 250+ Sheet functions) is summarized from the video, and some dates differ from the official record by a day."
```

The November 24 release notes also carry news beyond the seven.
The monthly recap left beta and is now available on Free, Pro, Max, and Ultra.
It can draw on Claude Code sessions and Cowork tasks, and stored recaps can be deleted.
Installing an artifact Claude makes as an app on Mac or Windows arrived in beta too.
Sending files to a connected app, or saving a file an app offers, also opened in beta.

## Closing thoughts

You do not need to learn all seven at once.
On Free, start by opening an app beside the chat. On Pro or above, try the whiteboard and Sheets first.
If you use the Code tab, try themes and the advisor, and on a company plan, turn on meetings.
Claude is pulling apps inside faster and faster, so the question now is which app comes in next.

## Frequently asked questions

**What new features can Free plan users use?**

Opening a connected app whole beside the chat. It works on every plan including Free, rolling out on web and desktop first. Whiteboards, Sheets, and Data need Pro or above, and Meetings is limited to Team and Enterprise.

**Can Pro users not use Fable 5.2?**

They can, but it is not included in usage and is billed separately for how much is used. Max and Ultra include Fable in usage. The same rule applies when Fable is called only as an advisor.

**Do Claude Meetings keep voice recordings?**

No. Voice recording files are not kept. Only the written record remains. Each meeting gets a page holding the summary, action items, transcript, and everything made during the meeting.

## Good reads

[Claude Pricing Compared｜Free, Pro, Max, and Ultra Prices and Limits](https://aitechnotesen.wordpress.com/2026/11/26/claude-pricing-compared%ef%bd%9cfree-pro-max-and-ultra-prices-and-limits/)

[District 9｜When Humans Caged Aliens, the Tech Picked a Side](https://aitechnotesen.wordpress.com/2026/11/25/district-9%ef%bd%9cwhen-humans-caged-aliens-the-tech-picked-a-side/)

<!-- 본문 끝 -->

## 작업용 출처·이미지 정보 (업로드 제외)

**출처**
- Ai-Con Lab, "꼭 알아야할 클로드 새 기능 7가지!!!", 2026-11-26 (자막 원문, 2026-11-27 06:02 브라우저 스크립트 패널 확보, 0:02~9:29 전문)
- Anthropic 공식 출시 노트 https://support.claude.com/en/articles/12138966-release-notes (2026-11-26 직접 확인)
- Anthropic 공식 API 가격 https://platform.claude.com/docs/en/about-claude/pricing (2026-11-27 검색 확인): Fable 5.2 $8/$40, Opus 5.5 $4/$20 (100만 토큰당)
- Fable 5.2 출시 2026-11-09: dev.to 정리, Geeky Gadgets 2026-11-26 기사 대조
- 수치 확인 기준: 2026년 11월 27일

**원고 노트**
- 영문 URL 주의: District 9 영문 URL은 wordpress-en 2026-11-25 명세 기록 주소 사용(추측 URL 금지 — 2026-11-25 명세에서 확인).
- 추천 링크: 클로드 요금제 비교(wordpress-en, 2026-11-26 명세 기록 URL) + 디스트릭트 9(blogger-en)
