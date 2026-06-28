# Vimmy: Repo-Specific Implementation Roadmap

## Purpose

This file turns [PLAN.md](/home/sohail/Github/vimmy/PLAN.md) into an execution checklist for the current repository.

Current repo reality:

- frontend is a minimal Vite React app
- backend Worker is a placeholder
- Drizzle is configured but schema is effectively empty
- multiplayer does not exist yet

So the correct approach is not `refactor`; it is `build the real app structure in controlled phases`.

## Current Files To Replace or Expand

Existing files that should be treated as temporary scaffolding:

- [src/App.tsx](/home/sohail/Github/vimmy/src/App.tsx)
- [src/main.tsx](/home/sohail/Github/vimmy/src/main.tsx)
- [src/App.css](/home/sohail/Github/vimmy/src/App.css)
- [src/index.css](/home/sohail/Github/vimmy/src/index.css)
- [worker/index.ts](/home/sohail/Github/vimmy/worker/index.ts)
- [drizzle/schema/schema.ts](/home/sohail/Github/vimmy/drizzle/schema/schema.ts)
- [wrangler.jsonc](/home/sohail/Github/vimmy/wrangler.jsonc)

## Build Order

Follow this order:

1. fix platform and config
2. create backend foundation
3. create frontend foundation
4. build auth and profile
5. build single-player game MVP
6. persist progress and mastery
7. build multiplayer rooms
8. polish, testing, deployment

## Phase 1: Platform and Config Foundation

### Objective

Make the project structurally correct before gameplay work begins.

### Files To Edit

- [package.json](/home/sohail/Github/vimmy/package.json)
- [wrangler.jsonc](/home/sohail/Github/vimmy/wrangler.jsonc)
- [drizzle.config.ts](/home/sohail/Github/vimmy/drizzle.config.ts)
- [README.md](/home/sohail/Github/vimmy/README.md)

### Files To Add

- `.env.example`
- `vitest.config.ts`
- `playwright.config.ts`
- `docs/architecture.md`

### Work Items

- Clean `wrangler.jsonc` because it currently has duplicated `assets` configuration.
- Add D1 binding configuration.
- Add Durable Object binding configuration.
- Add environment variable documentation.
- Add scripts for database migration, local dev, tests, and type checks.
- Add test runners and basic CI-ready commands.

### Recommended `package.json` Additions

Add dependencies:

- `phaser`
- `hono`
- `@hono/zod-validator`

Add dev dependencies:

- `drizzle-kit`
- `vitest`
- `playwright`
- `@playwright/test`

Add scripts like:

- `typecheck`
- `test`
- `test:e2e`
- `db:generate`
- `db:migrate`
- `cf:dev`

### Definition of Done

- local app runs
- worker runs
- D1 binding is declared
- Durable Object binding is declared
- scripts are usable by another developer without guessing

## Phase 2: Backend Foundation

### Objective

Turn the Worker into a real API service with Hono and typed modules.

### Replace

- [worker/index.ts](/home/sohail/Github/vimmy/worker/index.ts)

### Add

- `worker/app.ts`
- `worker/lib/env.ts`
- `worker/lib/db.ts`
- `worker/lib/http.ts`
- `worker/middleware/auth.ts`
- `worker/middleware/error.ts`
- `worker/routes/health.ts`
- `worker/routes/auth.ts`
- `worker/routes/profile.ts`
- `worker/routes/campaign.ts`
- `worker/routes/leaderboard.ts`
- `worker/routes/rooms.ts`
- `worker/types.ts`

### Structure

Suggested backend composition:

```text
worker/
  app.ts
  index.ts
  lib/
    db.ts
    env.ts
    http.ts
  middleware/
    auth.ts
    error.ts
  routes/
    auth.ts
    campaign.ts
    health.ts
    leaderboard.ts
    profile.ts
    rooms.ts
  realtime/
    MatchRoom.ts
  types.ts
```

### API To Implement First

- `GET /api/health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/profile/me`
- `POST /api/profile/create`
- `GET /api/campaign/chapters`
- `GET /api/campaign/progress`

### Notes

- Keep auth/session logic isolated from route handlers.
- Return typed JSON consistently.
- Use `zod` on every input boundary.

### Definition of Done

- Worker serves structured API routes
- errors are normalized
- auth middleware exists
- D1 access is abstracted in one place

## Phase 3: Database Schema and Persistence

### Objective

Create the actual relational model for users, progress, and match history.

### Replace

- [drizzle/schema/schema.ts](/home/sohail/Github/vimmy/drizzle/schema/schema.ts)

### Add

- `drizzle/schema/users.ts`
- `drizzle/schema/auth.ts`
- `drizzle/schema/campaign.ts`
- `drizzle/schema/multiplayer.ts`
- `drizzle/schema/achievements.ts`
- `drizzle/migrations/*`

### Recommended Split

Instead of one giant schema file, split by domain:

- `users.ts`
- `auth.ts`
- `campaign.ts`
- `multiplayer.ts`
- `achievements.ts`

Then re-export from `schema.ts`.

### Tables To Implement First

- `users`
- `sessions`
- `profiles`
- `chapters`
- `levels`
- `player_progress`
- `motion_mastery`
- `rooms`
- `match_results`

### Immediate Schema Priorities

Add enough data to support:

- sign up
- login session
- profile creation
- chapter list
- tutorial level save state
- multiplayer result storage

### Definition of Done

- schema compiles
- migrations generate cleanly
- app can create/fetch users and progress

## Phase 4: Frontend App Shell

### Objective

Replace the single component app with a route-based product shell.

### Replace

- [src/main.tsx](/home/sohail/Github/vimmy/src/main.tsx)
- [src/App.tsx](/home/sohail/Github/vimmy/src/App.tsx)
- [src/index.css](/home/sohail/Github/vimmy/src/index.css)
- [src/App.css](/home/sohail/Github/vimmy/src/App.css)

### Add

- `src/app/router.tsx`
- `src/app/providers.tsx`
- `src/app/query-client.ts`
- `src/app/store.ts`
- `src/routes/__root.tsx`
- `src/routes/index.tsx`
- `src/routes/login.tsx`
- `src/routes/onboarding.tsx`
- `src/routes/hub.tsx`
- `src/routes/campaign.$chapterId.tsx`
- `src/routes/arena.tsx`
- `src/routes/room.$roomId.tsx`
- `src/routes/profile.$username.tsx`
- `src/routes/leaderboard.tsx`

### Add Shared UI

- `src/components/ui/Button.tsx`
- `src/components/ui/Card.tsx`
- `src/components/ui/Input.tsx`
- `src/components/ui/Screen.tsx`
- `src/components/ui/Badge.tsx`

### Add Feature UI

- `src/components/auth/LoginForm.tsx`
- `src/components/auth/SignupForm.tsx`
- `src/components/profile/ProfileSummary.tsx`
- `src/components/hub/WorldMap.tsx`
- `src/components/hub/QuestPanel.tsx`
- `src/components/multiplayer/RoomBrowser.tsx`
- `src/components/multiplayer/LiveScoreboard.tsx`

### Styling Direction

The current CSS reads like a starter template. Replace it with a defined visual system.

Use:

- parchment / guild / archive tones
- strong display typography
- custom CSS variables
- layout tokens
- motion accents that fit the hunter theme

Avoid:

- generic white page with centered text
- default system fonts
- purple-heavy starter palette

### Definition of Done

- route-based app exists
- login, onboarding, hub, and campaign pages render
- app looks intentional, not template-generated

## Phase 5: Auth and Session Flow

### Objective

Make users able to sign in, persist sessions, and create profiles.

### Backend Files

- `worker/routes/auth.ts`
- `worker/middleware/auth.ts`
- `worker/lib/auth.ts`

### Frontend Files

- `src/features/auth/api.ts`
- `src/features/auth/store.ts`
- `src/features/auth/hooks.ts`
- `src/components/auth/LoginForm.tsx`
- `src/components/auth/SignupForm.tsx`
- `src/routes/login.tsx`
- `src/routes/onboarding.tsx`

### Flow

1. user signs up or logs in
2. session token is issued
3. frontend restores session
4. first-time user is sent to onboarding
5. onboarding creates hunter profile
6. profile unlocks hub access

### Definition of Done

- auth works end-to-end
- session restore works on refresh
- first-time flow is distinct from returning-user flow

## Phase 6: Campaign Data and Level Definitions

### Objective

Create the content format that powers single-player learning levels.

### Add

- `src/game/levels/types.ts`
- `src/game/levels/chapters.ts`
- `src/game/levels/tutorial-levels.ts`
- `src/game/levels/missions/intro-grid.ts`
- `src/game/levels/missions/word-dash.ts`
- `src/game/levels/missions/delete-strike.ts`
- `worker/services/levels.ts`

### Level Metadata Should Include

- level id
- chapter id
- motion focus
- tilemap or arena config
- enemy layout
- dialogue intro
- completion rules
- scoring rules
- reward rules

### First 3 Levels

- `intro-grid`: teach `h`, `j`, `k`, `l`
- `word-dash`: teach `w`, `b`, `e`
- `delete-strike`: teach `dd`

### Definition of Done

- level definitions are data-driven
- frontend can request or load campaign content cleanly

## Phase 7: Phaser Integration and Single-Player Game MVP

### Objective

Build the first actual playable game loop.

### Add

- `src/game/engine/createGame.ts`
- `src/game/engine/config.ts`
- `src/game/scenes/BootScene.ts`
- `src/game/scenes/HubScene.ts`
- `src/game/scenes/TutorialScene.ts`
- `src/game/scenes/ResultsScene.ts`
- `src/game/entities/Player.ts`
- `src/game/entities/Enemy.ts`
- `src/game/systems/InputBuffer.ts`
- `src/game/systems/MotionSystem.ts`
- `src/game/systems/ScoreSystem.ts`
- `src/game/systems/DialogueSystem.ts`
- `src/game/vim/parser.ts`
- `src/game/vim/validator.ts`
- `src/game/vim/motions.ts`
- `src/components/game/GameCanvas.tsx`

### Core MVP Loop

1. player enters a tutorial mission
2. the scene explains one Vim motion
3. the player performs the motion to move or attack
4. score is calculated
5. result is saved
6. next mission unlocks

### Critical Rule

Keep Vim input logic separate from Phaser scenes.

This separation should look like:

- scene handles rendering and events
- motion system handles keyboard command meaning
- score system handles result math

### Definition of Done

- at least one mission is fully playable
- player input changes in-game state
- level results appear after completion

## Phase 8: Progress, Mastery, and Results

### Objective

Turn the game from a toy into a learning product.

### Add

- `src/features/mastery/types.ts`
- `src/features/mastery/api.ts`
- `src/components/profile/MasteryPanel.tsx`
- `src/components/profile/ProgressChart.tsx`
- `worker/services/progress.ts`
- `worker/services/mastery.ts`

### Track Per Motion

- attempts
- success count
- accuracy percentage
- average input speed
- best streak
- mastery tier

### UI Screens To Improve

- hub overview
- profile page
- post-level results
- chapter completion summary

### Definition of Done

- player sees measurable skill progression
- backend persists mastery stats

## Phase 9: Multiplayer Rooms with Durable Objects

### Objective

Build one real-time competitive mode that is resume-worthy.

### Add

- `worker/realtime/MatchRoom.ts`
- `worker/realtime/protocol.ts`
- `worker/services/matchmaking.ts`
- `worker/routes/rooms.ts`
- `src/features/multiplayer/socket.ts`
- `src/features/multiplayer/api.ts`
- `src/features/multiplayer/store.ts`
- `src/components/multiplayer/RoomLobby.tsx`
- `src/components/multiplayer/ReadyPanel.tsx`
- `src/components/multiplayer/LiveScoreboard.tsx`
- `src/routes/arena.tsx`
- `src/routes/room.$roomId.tsx`

### First Multiplayer Mode

Build only one mode first:

- `race mode`

Flow:

1. user creates or joins room
2. room waits for players
3. Durable Object tracks readiness
4. match starts on synchronized countdown
5. all players get same challenge seed
6. DO validates results and broadcasts standings

### Anti-Cheat Principle

Do not trust client-side score submissions blindly.

At minimum:

- validate event order
- validate motion completion against seed
- validate timing boundaries

### Definition of Done

- two players can join a room
- countdown sync works
- standings update live
- result persists at match end

## Phase 10: Visual Polish and Content Expansion

### Objective

Make it feel portfolio-grade instead of prototype-grade.

### Add

- `src/game/assets/*`
- `src/components/hub/NpcDialogue.tsx`
- `src/components/ui/Toast.tsx`
- `src/components/ui/Modal.tsx`
- `src/features/audio/*`

### Polish Checklist

- better title screen
- dialogue transitions
- sound effects
- improved HUD
- boss intro moments
- achievement popups
- empty-state design
- loading states

### Content Expansion After MVP

- add `ciw`, `yy`, `p`, `gg`, `G`
- add boss command chains
- add daily challenge mode
- add leaderboard seasons

## Testing Plan

### Unit Tests

Add tests for:

- Vim motion parser
- motion validator
- score calculation
- profile creation validation
- unlock logic

Suggested files:

- `src/game/vim/parser.test.ts`
- `src/game/vim/validator.test.ts`
- `src/game/systems/ScoreSystem.test.ts`
- `worker/services/progress.test.ts`

### Integration Tests

Add tests for:

- signup flow
- login flow
- progress save endpoint
- room creation endpoint

### End-to-End Tests

Use Playwright for:

- sign up and create profile
- launch first mission
- complete tutorial motion level
- join room flow

## Suggested Milestones

### Milestone 1

`App shell + auth + profile`

Expected output:

- users can sign up
- users can log in
- users can create profiles
- hub page exists

### Milestone 2

`Single-player playable demo`

Expected output:

- 3 tutorial levels
- score and mastery tracking
- campaign progress save

### Milestone 3

`Multiplayer playable demo`

Expected output:

- room creation
- room join
- countdown
- race mode scoring

### Milestone 4

`Resume and portfolio release`

Expected output:

- polished landing page
- working deployed app
- screenshots and gameplay gif
- architecture docs

## Practical Next Commits

If you want to build this without thrashing, the first commits should be:

1. `chore: clean wrangler config and add project scripts`
2. `feat: add hono worker app skeleton`
3. `feat: add drizzle schema for auth and progress`
4. `feat: add app router and frontend shell`
5. `feat: implement auth and onboarding flow`
6. `feat: integrate phaser tutorial mission`
7. `feat: persist level progress and mastery`
8. `feat: add durable-object multiplayer race rooms`

## Highest-Risk Areas

These are the parts most likely to slow you down:

- trying to build too many Vim commands too early
- mixing game logic directly into React components
- mixing Vim parsing directly into Phaser scene code
- making multiplayer before single-player feels good
- designing too much story before the gameplay loop works

## Strict Scope Guardrails

To keep this project shippable:

- ship one good hub, not a huge world
- ship three strong tutorial levels before expanding content
- ship one multiplayer race mode before duels or ranked ladders
- ship text-safe, original lore instead of direct anime references

## Recommended Immediate Next Step

The best next implementation step in this repo is:

1. clean [wrangler.jsonc](/home/sohail/Github/vimmy/wrangler.jsonc)
2. scaffold the Hono Worker structure
3. replace the placeholder React app with a routed app shell

That gives the repo a serious foundation quickly and makes every later gameplay feature easier to add.
