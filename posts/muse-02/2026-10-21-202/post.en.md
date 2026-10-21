---
post_id: "2026-10-21-202"
muse_account: "muse-02"
language: "en"
content_revision: 1
status: "ready"
title: "A robot dog that jumps on your palm — the wire-free, open-source Q8botOne"
blog_url: "https://blog.naver.com/3700708"
category: "새로 나온 테크"
platform_categories:
  wordpress-en: "Tech"
  blogger-en: "Tech"
tags: ["robot dog", "open source", "maker", "crowdfunding", "desk robot", "ESP32", "robotics", "gadgets"]
action: "publish"
visibility: "public"
scheduled_at: ""
timezone: "Asia/Seoul"
editing: "format_only"
cover_image: "images/01-hero.jpg"
result:
  url: ""
  completed_at: ""
  note: ""
---

<!-- 본문 시작 -->
A robot dog that jumps on your palm — the wire-free, open-source Q8botOne

When you hear "robot dog," you probably picture a knee-high machine. This one is only 12 cm long — small enough to walk between a coffee cup and a laptop on your desk. But small doesn't mean toy. This introduction is based on published materials.

![12 cm long, 250 g — four legs on a body the size of a smartphone (illustration)](images/01-hero.jpg)

## No wires. That's the point.

Q8botOne is a quadruped robot built by ZeroWire Robotics in the US. Building a robot usually means routing a messy bundle of wires to every motor, but here the circuit board (PCB) itself is the chassis. Eight motors and two batteries plug straight into the board, so there's no wire bundle inside. The "ZeroWire" in the name means exactly that.

> One line
>
> ### **The board is the body, with no wires — a robot built to be opened up and fixed.**

## Three fun things about it

First, it doesn't move like a tiny toy. According to the developer, it walks and jogs — and even jumps — and can carry up to twice its own 250 g body weight. The legs use a parallel-link structure, and you can experiment with different gait patterns in the firmware.

Second, the motors are smart. Each joint uses a DYNAMIXEL smart servo — eight in total — feeding back position and speed. Unlike cheap hobby servos, the robot knows where its legs are, so you can run gait-correction experiments.

Third, everything is open. The circuit design files, firmware, 3D models, and assembly instructions are all open source. The base model has no camera or sensors, but a Qwiic connector and a 5 V expansion port let you mount sensors, a camera — or even a small computer like a Raspberry Pi — on its back.

![Motors and batteries plug straight into the board — when something breaks, you check the board, not a wire bundle (illustration)](images/02-pcb.jpg)

## Key product facts

| Item | Detail |
| --- | --- |
| Product | Q8botOne |
| Maker | ZeroWire Robotics (US) |
| Size · weight | 120×70×70mm / 250g |
| Hardware | ESP32-C3, 8× DYNAMIXEL smart servos, central PCB chassis |
| Price | Kit $199 (actuators sold separately) / assembled $599 |
| Availability | Crowd Supply campaign (funding through ~Nov 19, 2026) |
| Shipping | From March 2027, listed with free worldwide shipping |

## The catch

The $199 kit looks cheap until you notice the eight actuators that drive the legs aren't included — you have to buy them separately, and they're the most expensive part. And you can't buy the assembled version right now either: it's a crowdfunding product, shipping in March 2027. Performance figures like jumping and load capacity are still manufacturer claims with no independent verification.

![The joy of changing gaits in code — the experiment itself is this robot's real body (illustration)](images/03-jump.jpg)

## Editor's take

This isn't a companion robot — it's closer to a teaching kit. No face, no cuteness. Instead, everything is visible and open, ready to be modified. It's for people who want to know how a robot's walk is made, or makers who want hands-on practice with ESP32 and servo control. If you want a finished toy, check the assembled version's price and shipping schedule once more before deciding.

Sources: Crowd Supply official campaign page, Hackster and Yanko Design coverage (October 2026). Prices and schedule verified October 21, 2026; this is a materials-based introduction, not a hands-on review.
Related posts:
https://blog.naver.com/3700708/224444408193
https://blog.naver.com/3700708/224447910718
<!-- 본문 끝 -->

## Working notes (excluded from upload)

- Sources: Crowd Supply official campaign (https://www.crowdsupply.com/zerowire-robotics/q8botone) / Hackster (2026-10-08) / Yanko Design (2026-10-10) / CNX Software / verified 2026-10-21
- 3 images (AI-generated illustrations, self-made, usage rights: own):
  - images/01-hero.jpg / 12 cm long, 250 g — four legs on a body the size of a smartphone (illustration)
  - images/02-pcb.jpg / Motors and batteries plug straight into the board (illustration)
  - images/03-jump.jpg / The joy of changing gaits in code (illustration)
- Fact check: performance figures (jump, 2× payload) are manufacturer claims, no independent verification. $199 kit excludes actuators. Shipping scheduled March 2027.
- Target: English WordPress/Blogger (multi-channel program). English edition content_revision: 1 — confirm against check_distribution before first submit.
- Additional requests: none
