# Vimmy: Resume-Ready 2D Game Plan

## Goal

Turn this repo into a polished 2D web game where players learn Vim motions through a story-driven campaign and then compete in multiplayer rooms.

The concept:

- A hunter-themed training journey inspired by shonen progression.
- Players sign up, create a profile, and enter a world where each zone teaches a Vim skill.
- Single-player levels teach motions through combat, puzzles, movement, and timed challenges.
- Multiplayer rooms let players race or duel on Vim-based challenges.

For resume value, this project should show:

- real product thinking
- frontend game architecture
- backend API design
- auth and persistence
- real-time multiplayer
- clean deployment on Cloudflare

## Important Product Direction

Do not market it as a direct `Hunter x Hunter` game. Use a `hunter-inspired` original setting instead.

Reason:

- You avoid IP issues.
- The project still keeps the same energy: exams, guilds, progression, rivals, and high-skill challenges.

## What The Final Product Should Feel Like

The player journey should be:

1. Sign up and create a hunter profile.
2. Enter a hub area with NPCs, quests, and level gates.
3. Complete tutorial missions for `h`, `j`, `k`, `l`, `w`, `b`, `e`, `gg`, `G`, `dd`, `yy`, `p`, `ciw`, and search motions.
4. Unlock harder regions with faster enemies, trickier text patterns, and multi-step command puzzles.
5. Join live rooms to race other players in accuracy and speed.
6. Track rank, progress, streaks, and mastery.

## Recommended Stack

Use the current stack as the base instead of restarting.

### Keep

- `React 19` for UI
- `TypeScript` for full-stack type safety
- `Vite` for frontend build
- `Cloudflare Workers` for API
- `Hono` for routing on the backend
- `Drizzle ORM` for schema and queries
- `Zustand` for local game state
- `TanStack Query` for server state
- `Zod` for validation

### Add

- `Phaser 3` for the 2D game runtime
- `@tanstack/react-router` for app routing, since it is already installed
- `Cloudflare D1` for relational persistence
- `Cloudflare Durable Objects` for multiplayer rooms and real-time match state
- `WebSocket` support through Durable Objects
- `Cloudflare Turnstile` for bot-resistant auth flows
- `better-auth` or custom JWT session flow using `jose`
- `Vitest` for unit tests
- `Playwright` for end-to-end testing

### Optional Later

- `Howler.js` for audio
- `Motion` or CSS-only animation for menus
- `Sentry` or Cloudflare observability dashboards for error tracking

## High-Level Architecture

### 1. Frontend App Layer

This is the React shell around the game.

Responsibilities:

- auth screens
- onboarding
- profile screen
- world map / level select
- inventory / achievements / rank UI
- matchmaking UI
- post-match results
- tutorial overlays

Suggested React routes:

- `/`
- `/login`
- `/onboarding`
- `/hub`
- `/campaign/:chapterId`
- `/arena`
- `/room/:roomId`
- `/profile/:username`
- `/leaderboard`

### 2. Game Runtime Layer

This is the actual 2D game engine area, best handled by Phaser.

Responsibilities:

- scene management
- player movement
- enemy behavior
- collision
- pickups and rewards
- dialogue triggers
- motion-input challenges
- timing windows
- keyboard capture

Suggested Phaser scenes:

- `BootScene`
- `MenuScene`
- `HubScene`
- `TutorialScene`
- `MissionScene`
- `BossScene`
- `ArenaScene`
- `ResultsScene`

### 3. Vim Challenge Engine

This is the most important system in the project.

Responsibilities:

- define motions to teach
- generate exercises
- validate inputs
- score correctness, speed, combo, and recovery
- map motions into gameplay outcomes

Examples:

- `h/j/k/l` moves the player through a grid arena
- `w/b/e` lets the player dash word-to-word across text platforms
- `dd` defeats a target line enemy
- `yy` copies a rune
- `p` places the rune in a new slot
- `ciw` transforms a locked object by editing the target word
- `/pattern` highlights hidden enemies matching the search

This should be built as a reusable logic module, not mixed directly into rendering code.

### 4. Backend API Layer

Use Hono inside the Worker.

Responsibilities:

- auth
- user profile CRUD
- campaign progress persistence
- level metadata
- inventory / rewards
- leaderboard reads
- matchmaking requests
- match history

Suggested API groups:

- `/api/auth/*`
- `/api/profile/*`
- `/api/campaign/*`
- `/api/levels/*`
- `/api/rooms/*`
- `/api/leaderboard/*`
- `/api/admin/*`

### 5. Persistence Layer

Use D1 with Drizzle for durable data.

Core tables:

- `users`
- `sessions`
- `profiles`
- `levels`
- `chapters`
- `player_progress`
- `motion_mastery`
- `match_results`
- `room_history`
- `achievements`
- `inventory_items`

### 6. Real-Time Multiplayer Layer

Use Durable Objects for authoritative room state.

Responsibilities:

- room lifecycle
- player join/leave
- ready state
- match countdown
- authoritative scoring
- anti-cheat validation
- real-time event broadcast

Room modes:

- `race`: first to clear a challenge set
- `survival`: last player standing
- `duel`: head-to-head command combat
- `daily challenge`: all players compete on the same generated seed

## Core Game Systems

### Story System

Build an original hunter world with:

- a guild exam
- mentors
- rival players
- ranked regions
- special artifacts linked to Vim mastery

Suggested story arc:

1. `Entrance Exam`
2. `Forest of Motions`
3. `Archive Ruins`
4. `Command Tower`
5. `Arena Trials`
6. `Master Hunt`

Each arc introduces a Vim concept and one new game mechanic.

### Learning System

Each lesson should teach:

- what the motion does
- when to use it
- how fast the player can perform it
- where it fails
- how it combines with other motions

Track per-motion metrics:

- attempts
- success rate
- average input speed
- error type
- mastery level

### Combat and Puzzle System

Do not make this a generic platformer. Make the game mechanics visibly tied to Vim.

Examples:

- enemies are arranged as tokens, words, or lines
- commands trigger attacks
- movement is constrained through text-based terrain
- bosses require command chains
- some rooms are puzzle-based editing tasks

### Progression System

Reward:

- badges
- titles
- new zones
- cosmetics
- ranks
- story unlocks

Avoid pay-to-win systems. This should feel skill-based.

## Component Breakdown

## Frontend Components

### App Shell

- router setup
- query client
- auth provider
- global layout
- settings and keybinding support

### Auth Components

- login form
- signup form
- guest mode gate
- session restore

### Profile Components

- player card
- level progress summary
- motion mastery chart
- match history list
- achievements panel

### Hub Components

- world map
- NPC dialogue boxes
- quest tracker
- chapter gates
- inventory panel

### Matchmaking Components

- room browser
- create room form
- join by code
- ready-state panel
- live scoreboard

### Game UI Components

- health / stamina / combo HUD
- current objective panel
- command input display
- error feedback panel
- timer
- mini leaderboard

## Game Engine Components

### Input System

- keyboard capture
- command buffering
- combo timing
- invalid input handling

### Player Controller

- movement rules
- motion-triggered abilities
- state machine

### Enemy System

- basic enemy AI
- boss patterns
- text-tagged weak points

### Level System

- tilemap loading
- object triggers
- checkpoints
- scripted events

### Challenge Generator

- lesson templates
- random seeds
- dynamic difficulty scaling

### Scoring System

- accuracy
- speed
- combo streak
- damage avoided

## Backend Components

### Auth Module

- account creation
- session issuance
- logout
- protected route middleware

### User Module

- profile fetch/update
- username uniqueness
- avatar and cosmetic metadata

### Campaign Module

- chapter definitions
- level unlock logic
- save checkpoints
- mastery updates

### Match Module

- room creation
- join/leave
- matchmaking
- result persistence

### Leaderboard Module

- global ranking
- friends ranking later
- daily challenge ranking

## Data Model Breakdown

Minimum schema plan:

- `users(id, email, created_at)`
- `sessions(id, user_id, expires_at)`
- `profiles(id, user_id, username, title, rank, avatar_seed)`
- `chapters(id, slug, title, order_index)`
- `levels(id, chapter_id, slug, motion_focus, difficulty, config_json)`
- `player_progress(id, user_id, level_id, completed, stars, best_score, best_time_ms)`
- `motion_mastery(id, user_id, motion_key, accuracy, avg_time_ms, mastery_tier)`
- `rooms(id, room_code, mode, status, created_by, created_at)`
- `match_results(id, room_id, user_id, score, placement, payload_json)`
- `achievements(id, key, name, description)`
- `player_achievements(id, user_id, achievement_id, unlocked_at)`

## Cloudflare-Specific Build Plan

This repo is already positioned well for Cloudflare. Use that.

### Worker

Use the Worker for:

- REST APIs with Hono
- auth/session verification
- content delivery for level metadata
- leaderboard endpoints

### Durable Objects

Use Durable Objects for:

- multiplayer room state
- synchronized countdowns
- player presence
- live scoring

### D1

Use D1 for:

- users
- progress
- story state
- achievements
- match history

### R2 Optional

Use R2 later if you want:

- custom avatars
- audio assets
- downloadable content packs

## Suggested Repo Structure

```text
src/
  app/
    router/
    providers/
    layouts/
  components/
    auth/
    profile/
    hub/
    matchmaking/
    ui/
  features/
    campaign/
    multiplayer/
    mastery/
  game/
    engine/
    scenes/
    entities/
    systems/
    levels/
    assets/
    vim/
  lib/
    api/
    auth/
    utils/
worker/
  api/
  auth/
  services/
  realtime/
  db/
drizzle/
  schema/
  migrations/
docs/
  game-design/
  api/
  architecture/
```

## Delivery Phases

### Phase 1: Foundation

Goal: make the repo look like a serious product quickly.

Tasks:

- set up app routing
- create layout and visual direction
- replace placeholder homepage
- set up Hono API structure
- configure D1 and Drizzle schema
- add auth flow
- add profile creation

Resume value unlocked:

- full-stack app structure
- production deployment base

### Phase 2: Single-Player MVP

Goal: prove the core idea works.

Tasks:

- integrate Phaser
- build hub scene
- build 3 tutorial levels
- implement motion validator for basic movement
- save progress to D1
- show post-level results

MVP motion set:

- `h`
- `j`
- `k`
- `l`
- `w`
- `b`
- `e`
- `dd`

Resume value unlocked:

- custom educational game logic
- game engine integration in a web app

### Phase 3: Story and Progression

Goal: make it memorable, not just functional.

Tasks:

- add dialogues and mentors
- add chapter unlocks
- add mastery progression
- add achievements
- add boss level with command chains

Resume value unlocked:

- product design depth
- retention mechanics

### Phase 4: Multiplayer

Goal: add the standout feature.

Tasks:

- Durable Object room service
- WebSocket join flow
- race mode
- live score sync
- anti-cheat validation
- result persistence

Resume value unlocked:

- real-time multiplayer architecture
- authoritative backend design

### Phase 5: Polish

Goal: make it portfolio-grade.

Tasks:

- sound design
- better art and animations
- leaderboard UI
- daily challenges
- onboarding improvements
- analytics and error tracking
- test coverage

## MVP Scope Recommendation

If you want this to ship instead of staying a concept, keep the first playable milestone very small.

Build this first:

- login
- profile
- one hub screen
- three single-player tutorial levels
- one scoring model
- progress saving
- one multiplayer race room

Do not build first:

- large open world
- many story arcs
- cosmetics marketplace
- complex inventory economy
- too many commands at once

## Suggested Visual Direction

Aim for:

- retro-modern pixel art or crisp low-poly 2D illustration
- parchment, guild, map, and archive aesthetics
- motion commands shown as magical glyphs or technique sigils

This makes the game distinct from generic coding-game dashboards.

## What To Build First In This Repo

Given the current repo state, the practical order is:

1. Fix and clean `wrangler.jsonc`.
2. Convert the Worker to a real Hono app.
3. Add D1 binding and Drizzle schema.
4. Add routing and app shell in React.
5. Build login and profile screens.
6. Integrate Phaser into a campaign route.
7. Build one real tutorial level around movement motions.
8. Save progress and show mastery metrics.
9. Add one Durable Object room for multiplayer races.

## Resume Framing

If executed well, this becomes a strong portfolio line:

`Built Vimmy, a full-stack 2D educational multiplayer game that teaches Vim motions through story-driven levels and real-time competitive rooms, using React, Phaser, Cloudflare Workers, Durable Objects, D1, and TypeScript.`

## Final Recommendation

Treat this as a product, not just a toy game.

The winning combination is:

- original hunter-themed world
- strong Vim learning loop
- clean single-player progression
- one solid real-time multiplayer mode
- production-ready Cloudflare deployment

If you want, the next step should be turning this plan into an implementation roadmap with exact file-by-file tasks for this repo.
