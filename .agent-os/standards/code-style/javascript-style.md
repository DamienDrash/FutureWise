# JavaScript / TypeScript Style Guide

## General Principles
- **TypeScript first**: All new JavaScript code must be written in TypeScript (`.ts` or `.svelte` with `<script lang="ts">`).
- Code must be **clean, readable, and self-documenting**.
- All code, comments, and documentation must be written in **English**.
- Follow **NumPy-style docstring principles** for JSDoc where applicable.

---

## Syntax & Formatting
- Use **ESNext syntax** (e.g., `let` / `const`, arrow functions, template literals).
- Always prefer `const` over `let` unless reassignment is required.
- Never use `var`.
- Strings:
  - Prefer single quotes `'...'`
  - Use backticks `` `...` `` for template literals or multi-line strings
- End statements with semicolons.

---

## Naming Conventions
- **Variables & functions:** `camelCase` (e.g., `fetchUserData`)
- **Classes & components:** `PascalCase` (e.g., `UserProfile`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **Private members:** Prefix with `_` (e.g., `_internalCache`)
- File names:
  - Components: `PascalCase.svelte`
  - Utility modules: `kebab-case.ts`

---

## Imports & Exports
- Group imports:
  1. Built-in modules
  2. External packages
  3. Internal modules
- Use **named exports** by default.
- Use **default exports** only for a single main component per file.

---

## Functions
- Keep functions small (≤ 30 lines).
- Each function should have a single responsibility.
- Use async/await for asynchronous code; avoid `.then()` chaining.
- Type all parameters and return values in TypeScript.

---

## Comments & Documentation
- Use JSDoc for public functions, classes, and modules:
```ts
/**
 * Fetch user data from API.
 *
 * @param {number} id - User ID to fetch.
 * @returns {Promise<User>} Promise resolving to user object.
 * @throws {Error} If request fails.
 */
async function fetchUser(id: number): Promise<User> {
  // ...
}

	•	Tags for in-code tracking:
	•	// TODO(YYYY-MM-DD, initials): Description
	•	// FIXME(YYYY-MM-DD, initials): Description
	•	// BUG(YYYY-MM-DD, initials): Description
	•	// NOTE: for important clarifications

---

Error Handling
	•	Always handle errors in async functions with try/catch.
	•	Throw meaningful error messages.
	•	Avoid silent failures.

---

Svelte-Specific Rules
	•	<script> block comes before <style> and markup.
	•	Keep reactive statements ($:) minimal and relevant.
	•	Import order in Svelte:
	1.	External dependencies
	2.	Stores
	3.	Components
	4.	Utilities
	•	Pass only required props to components.

---

TailwindCSS in JS/Svelte
	•	Apply classes directly in markup whenever possible.
	•	For complex class logic, compute class strings in the <script> block using arrays or template literals.
	•	Follow multi-line Tailwind formatting from html-style.md.

---

Testing
	•	Use vitest for unit tests and playwright for e2e tests.
	•	Test file naming: *.test.ts
	•	Arrange-Act-Assert structure in tests.
	•	Keep test data in fixtures.

---

Performance & Best Practices
	•	Avoid unnecessary DOM manipulation; use Svelte reactivity.
	•	Debounce or throttle expensive operations.
	•	Lazy-load components and modules where applicable.
	•	Remove unused imports and variables.


