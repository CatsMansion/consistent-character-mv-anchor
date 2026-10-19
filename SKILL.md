---
name: consistent-character-mv-anchor
displayName: "Consistent Character MV Anchor (角色MV锚点一致性)"
slug: consistent-character-mv-anchor
category: image-processing
description: "Produce consistent character anchors and animation/MV assets for a fixed original character: keep identity stable across poses/expressions/frames using image-to-image with a locked anchor reference, green-screen keying, programmatic feature locking, and frame-consistency locking. Use when: 'consistent character across frames', 'keep identity in AI image generation', 'MV character asset', '角色一致性', 'MV 锚点', '帧间一致', '绿幕键控', '特征锁定', 'sprite baseline alignment'. Covers: i2i+anchor identity lock (don't trust text prompts for fine features), dual-criteria chroma key (connected-component + color distance) that also strips baked-in generator watermarks, programmatic feature transplant for small local features the model drifts on, and the only reliable way to get frame-to-frame absolute pixel consistency (lock the static region back to the base frame, animate only the intended region). Includes a composition-baseline measurement method so assets don't jump in a sprite pack, an ethics note (use your own characters; never publish client/third-party assets), and a 'tested backfires' list."
agent_created: true
description_zh: "为固定原创角色生产一致的 MV/动画角色锚点与素材：用图生图+锁定的锚图参考保持跨姿态/表情/帧的身份一致，绿幕键控，程序化特征锁定，帧间一致性锁定。触发：跨帧角色一致、AI 出图保身份、MV 角色素材、角色一致性、MV 锚点、帧间一致、绿幕键控、特征锁定、精灵基线对齐。含：i2i+锚图身份锁（细特征别信文字 prompt）、双判据绿幕（连通域+颜色距离，顺带去掉生成器水印）、小特征的程序化移植、以及帧间绝对像素一致的唯一可靠路径（静态区锁回底板、只动目标区）。含构图基线测量法（防进 pack 跳变）、伦理说明（用你自己的角色，勿发客户/第三方资产）、实测反效果清单。"
---

# Consistent Character MV Anchor

## Problem
Generating many assets (poses, expressions, frames) of ONE character for an MV /
animation: identity drifts between outputs, backgrounds must become transparent,
small signature features (a hair streak, an earring) won't stay put, and frames
jitter against each other.

## Core principles
1. **Lock identity with an anchor, not with words.** Always image-to-image from
   a fixed anchor image of the character. Text prompts cannot reliably hold fine
   identity features (streak placement, earring side, exact palette). The anchor
   is the source of truth; prompts only describe the *change* (pose/expression).
2. **Generate on a solid key color, then key it out.** Render on a known
   background (e.g. pure green) so you can chroma-key to transparent
   deterministically.
3. **Lock small features programmatically, don't re-roll.** For a tiny localized
   feature the model keeps drifting on, do a color-domain remap / transplant from
   the anchor at fixed coordinates. Zero extra generations, deterministic.
4. **Frame consistency is a programmatic job, not a generation job.** Independent
   i2i samples never align pixel-to-pixel. Take the approved base frame, lock the
   non-moving region back to it, and let only the intended region animate.
5. **Align every asset to one composition baseline** so they don't jump when
   packed into a sprite sheet.

## Workflow
### 1) Build the anchor
Pick one clean, on-model full-body (or bust) image as THE identity anchor.
Record its composition baseline (step 5). All future assets i2i from this anchor.

### 2) Generate with key color + i2i
- Set canvas/background to a solid key color.
- i2i from the anchor; prompt only the delta (pose/expression/action).
- Output carries the key-color background + possibly a generator watermark.

### 3) Key out + strip watermark
- Chroma-key with **dual criteria**: (a) color distance to the key color below
  threshold, AND (b) connectivity to the frame border (the background is one
  connected region). After keying, only the **largest connected foreground
  component** is kept, so small disconnected specks and a watermark sitting on the
  background (a different color than the key) are dropped too.
- See `scripts/key_green.py`.

### 4) Lock drifted features
- If a small feature drifted (wrong side / wrong shape), remap its color region
  or transplant the correct pixels from the anchor at the same coordinates.
  Deterministic; costs no generations.
- Generalize: any feature smaller than ~a few dozen px that the model won't hold
  → lock it, don't re-roll.

### 5) Composition baseline (measure once, enforce always)
Measure the anchor's bounding box and margins; require every new asset to match:
- left/right/top/bottom margin (px), occupancy % (character area / canvas),
  bottom padding.
- If a new asset deviates beyond tolerance, nudge/regenerate before packing.
- See `scripts/measure_bbox.py`.

### 6) Frame consistency
For animation frames: from the approved base frame, programmatically copy the
static region from the base into each frame, animate only the moving part. This
is the only way to hit "absolute pixel consistency" across frames.

## Scripts
- `scripts/measure_bbox.py input.png` → prints L/R/T/B margins, occupancy %,
  bottom padding, center. Use to set and check the baseline.
- `scripts/key_green.py in.png out.png --key #06EB0D --dist 60` → chroma-keys the
  key color to transparent with dual criteria; light background watermarks are
  dropped with the border region.

## Ethics & scope
- Use **your own** original characters. Do **not** publish or process client /
  third-party assets through a shared or public pipeline.
- Generator watermarks: strip only the in-file stamp from images **you**
  generated; keep separate AI-use disclosure per platform rules.
- This is a methodology, not a model. Swap in whatever i2i / keying tools you have.

## Tested backfires (don't retry blindly)
- **Localized features drift under i2i** (hair streak flips side, earring
  vanishes, streak becomes a horizontal band). Re-rolling rarely fixes it and
  burns generations. Lock programmatically instead.
- **i2i overrides a written aspect ratio.** If the anchor is a different body
  ratio than the target, the model pulls the result back toward the anchor's
  ratio. Pick an anchor at the target ratio, or redraw after.
- **Frames never align by generation alone.** Independent sampling ⇒ jitter.
  Lock the static region.
- **Don't trust "no silver / single side" negative prompts** to hold a fine
  feature — models treat localized color as highlight / band. Describe via anchor
  + programmatic lock.
