# CSS Style Guide

## General Principles
- All styling is implemented using **TailwindCSS v4** in **utility‑first** style.
- **Design tokens** (colors, fonts, radii, shadows, spacing) are defined as **CSS custom properties** in `:root` and `.dark` selectors.
- The Tailwind theme configuration (`@theme inline`) must map directly to these variables.
- Maintain a **single source of truth** for colors, spacing, typography, shadows, and radii in `index.css`.

---

## Color & Design Tokens

### Definition
- Light mode tokens are defined under `:root`.
- Dark mode tokens are defined under `.dark`.
- Token names follow the format `--<element>` (e.g., `--primary`, `--border`).

### Usage
- Always use `var(--token-name)` inside `@theme inline` mapping to Tailwind theme colors.
- Never hardcode OKLCH or HEX values directly in markup – use the mapped Tailwind classes.

---

## Multi-line TailwindCSS Classes in Markup

We use a **multi-line formatting style** for Tailwind classes in HTML/Svelte markup:

1. **Smallest size** (no prefix) on the top line.
2. Each following line represents the next responsive size up (`xs`, `sm`, `md`, `lg`, `xl`, `2xl`).
3. Align all class names vertically for readability.
4. Group pseudo-classes (`hover:`, `focus:`, `active:`) on their own lines.
5. Custom CSS classes (if any) appear first on the top line.
6. Follow class grouping order: **Layout → Spacing → Typography → Colors → States**.

**Example:**
```html
<div class="custom-cta bg-background text-foreground p-4 rounded-md shadow
            hover:bg-muted hover:text-muted-foreground
            xs:p-6
            sm:p-8 sm:text-lg
            md:p-10 md:text-xl
            lg:p-12 lg:font-semibold
            xl:p-14 xl:text-2xl
            2xl:p-16 2xl:text-3xl">
  I'm a call-to-action!
</div>


---

Responsive Breakpoints
	•	Standard Tailwind breakpoints apply, plus one custom breakpoint:
	•	xs = 400px (must be added in tailwind.config.js).
	•	Always design mobile-first; add responsive classes progressively.

---

Shadows & Radius
	•	Use shadow tokens (shadow, shadow-md, etc.) mapped from index.css variables.
	•	Use radius tokens (radius-sm, radius-md, etc.) for consistent rounding.

---

Typography
	•	Fonts are mapped to tokens:
	•	font-sans → --font-sans
	•	font-serif → --font-serif
	•	font-mono → --font-mono
	•	Letter spacing is controlled via tracking tokens (tracking-tight, tracking-wide, etc.).

---

Dark Mode
	•	Implemented via the .dark class on the <html> or <body> tag.
	•	Dark mode tokens override light mode in index.css.
	•	Tailwind classes reference the same token names, ensuring color parity between modes.

---

Best Practices
	•	Do not mix arbitrary values (e.g., bg-[#123456]) in production code; map them to tokens instead.
	•	Keep custom CSS minimal; prefer Tailwind utilities for all layout, spacing, and typography.
	•	When custom CSS is necessary, define it in the appropriate *.css file and reference via a class name.

