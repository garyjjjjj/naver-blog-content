---
post_id: "2026-10-21-202"
muse_account: "muse-02"
language: "en"
content_revision: 2
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

Mention a robot dog and most people imagine something bulky, about as tall as your knee. Q8botOne measures just 12 cm from nose to tail — it could trot across the gap between your mug and your laptop. Don't let the size fool you into calling it a toy, though. What follows is a roundup drawn from published sources.

![Only 12 cm long and 250 g — four legs attached to a body roughly the size of a smartphone (illustration)](images/01-hero.jpg)

## The whole idea: no wires at all

Q8botOne is a four-legged robot from the American company ZeroWire Robotics. Anyone who has built a robot knows the usual headache: running a separate cable to every motor leaves the inside a tangled mess. This design sidesteps that entirely by making the printed circuit board (PCB) double as the frame. Its eight motors and two batteries connect directly to the board, so there is no bundle of wiring tucked inside — which is precisely what the "ZeroWire" name is getting at.

> The short version
>
> ### **The circuit board is the skeleton, and the wires are gone — a robot designed from the start to be taken apart and repaired.**

## Three things that make it interesting

To begin with, it moves far beyond its size. The developer says the robot can walk, break into a jog, and even leap, all while hauling a load of up to twice its own 250 g weight. Its legs are built around a parallel linkage, and the walking pattern itself lives in the firmware, ready for you to tweak and test.

Next, the motors are anything but dumb. Every joint carries a DYNAMIXEL smart servo — eight across the whole robot — and each one reports its position and speed back to the controller. Cheap hobby servos can't do that, so unlike them, this robot always knows where its legs are, opening the door to experiments like correcting its own stride.

And finally, nothing about it is locked away. The schematics, the firmware, the 3D model files, and the build guide have all been released as open source. The standard version ships without a camera or sensors, yet a Qwiic connector and an expansion port supplying 5 V power mean you can add sensors or a camera later — or perch a tiny computer such as a Raspberry Pi on its back.

![The motors and batteries mount straight onto the board — so when something fails, the board is the first place you look, not a nest of cables (illustration)](images/02-pcb.jpg)

## The essentials at a glance

| Item | Detail |
| --- | --- |
| Product | Q8botOne |
| Maker | ZeroWire Robotics (US) |
| Dimensions · weight | 120×70×70mm / 250g |
| Hardware | ESP32-C3, 8× DYNAMIXEL smart servos, central PCB body |
| Price | Kit $199 (actuators not included) / fully assembled $599 |
| Status | Crowdfunding on Crowd Supply (running until around November 19, 2026) |
| Shipping | Planned for March 2027, listed as free worldwide delivery |
| Buying from Korea | Direct import (Korean-language support not confirmed) |

## Where it falls short

That $199 kit price comes with a catch. The eight actuators that actually move the legs are sold separately, and in the end they account for most of what you will spend. The ready-built version isn't something you can order and receive right away, either — it is a crowdfunding reward, with delivery not expected until March 2027. As for headline abilities like the jumping and the payload figures, those remain the developer's own claims at this stage; nobody independent has verified them yet.

![Rewriting the gait in code is half the fun — the real product here is the experimenting itself (illustration)](images/03-jump.jpg)

## Our verdict

Think of Q8botOne less as a robot pet and more as a hands-on learning platform. There is no face and no attempt at being cute. What you get instead is a machine whose insides are fully visible and open to modification. It suits anyone curious about how a walking robot's gait comes together, and makers who want practical experience with ESP32 boards and servo control. If what you are after is a finished toy, take another careful look at the assembled model's price tag and its March 2027 shipping date before committing.

Sources: the official Crowd Supply campaign page, plus coverage by Hackster and Yanko Design (October 2026). Pricing and dates checked on October 21, 2026. This is an introduction based on published materials, not a hands-on review.
Related posts:
https://blog.naver.com/3700708/224444408193
https://blog.naver.com/3700708/224447910718
<!-- 본문 끝 -->

## Working notes (excluded from upload)

- Sources: Crowd Supply official campaign (https://www.crowdsupply.com/zerowire-robotics/q8botone) / Hackster (2026-10-08) / Yanko Design (2026-10-10) / CNX Software / verified 2026-10-21
- 3 images (AI-generated illustrations, self-made, usage rights: own):
  - images/01-hero.jpg / Only 12 cm long and 250 g — four legs attached to a body roughly the size of a smartphone (illustration)
  - images/02-pcb.jpg / The motors and batteries mount straight onto the board (illustration)
  - images/03-jump.jpg / Rewriting the gait in code is half the fun (illustration)
- Fact check: performance figures (jumping, carrying 2× its weight) are developer claims with no independent verification. The $199 kit excludes the actuators. Shipping is scheduled for March 2027.
- Target: English WordPress/Blogger (multi-channel program). English edition content_revision: 2 — rewritten for the 2026-10-21 Naver refresh batch with new wording; confirm against check_distribution before submitting.
- Additional requests: none
