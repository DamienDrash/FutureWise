# HTML Style Guide

## General Principles
- All markup must be **semantic HTML** and accessible.
- Follow **mobile-first** principles in structure and classes.
- Keep HTML **clean, minimal, and readable** – avoid unnecessary wrappers.
- Always use **English** for content, IDs, classes, and attributes.

---

## Indentation & Structure
- Use **2 spaces** for indentation (never tabs).
- Each nested element should be on a new line with proper indentation.
- For multi-line elements, put the **content between tags on its own line**.
- Close tags at the same indentation level as their opening tag.

---

## Attribute Formatting
- Place multiple HTML attributes **each on their own line** for long elements.
- Align attributes vertically for readability.
- Keep the closing `>` of the opening tag on the **same line** as the last attribute.
- Attribute order:
  1. `id`
  2. `class`
  3. `data-*`
  4. `src` / `href` / `action`
  5. `alt` / `title`
  6. ARIA attributes
  7. Boolean attributes (e.g., `disabled`, `checked`)

---

## Class Formatting (Tailwind v4)
- Use **multi-line Tailwind class formatting** for complex elements:
  - First line: base (mobile) classes
  - Following lines: breakpoint classes (`xs`, `sm`, `md`, `lg`, `xl`, `2xl`)
  - Group classes logically: Layout → Spacing → Typography → Colors → States
  - Pseudo-classes (`hover:`, `focus:`, `active:`) grouped together
- Example:
```html
<button class="bg-primary text-primary-foreground font-semibold px-4 py-2 rounded-md shadow
               hover:bg-primary/90
               xs:px-6 xs:py-3
               sm:px-8 sm:text-lg
               lg:px-10 lg:text-xl">
  Submit
</button>


---

Accessibility (a11y)
	•	Every img must have a meaningful alt attribute.
	•	Use proper heading hierarchy (h1 → h2 → h3).
	•	Use aria-* attributes for interactive elements when needed.
	•	All interactive elements must be reachable via keyboard navigation.
	•	Use role attributes where appropriate (e.g., role="navigation").

---

Semantic & SEO Best Practices
	•	Use semantic elements (<header>, <main>, <footer>, <section>, <article>, <nav>, <aside>).
	•	Avoid using <div> when a semantic element fits.
	•	Use <button> for actions, <a> for navigation.
	•	Always set lang="en" on the <html> tag.

---

Example HTML Structure

<div class="container mx-auto p-4">
  <header class="flex flex-col space-y-2
                 md:flex-row md:space-y-0 md:space-x-4">
    <h1 class="text-primary font-bold">
      Page Title
    </h1>
    <nav class="flex flex-col space-y-2
                md:flex-row md:space-y-0 md:space-x-4"
         role="navigation"
         aria-label="Main navigation">
      <a href="/"
         class="btn-ghost">
        Home
      </a>
      <a href="/about"
         class="btn-ghost">
        About
      </a>
    </nav>
  </header>
</div>


---

Comments
	•	Use <!-- --> for HTML comments.
	•	For todos, bugs, or notes in HTML:

<!-- TODO(2025-08-02, DF): Replace placeholder image with final asset -->


---

Performance Guidelines
	•	Minimize DOM nesting.
	•	Avoid inline styles; use Tailwind classes or reusable components.
	•	Only load necessary scripts/styles for the current page.


