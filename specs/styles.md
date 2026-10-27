# UI/UX & Styling Guidelines (The Living Design System)

> **Target Directory:** `specs/styles.md`  
> **Design Language:** Modern Minimalist / Dark High-Tech (shadcn/ui aesthetic)  
> **Status:** Canonical Standard (Updated & Locked)  

---

## 1. Aesthetic Vision & Atmosphere

The design system of **uTrack** draws inspiration from the refined, modern minimalism of **shadcn/ui**:
- **Palette Foundation:** Pure deep blacks (`#000000`, `#09090b`), subtle dark zinc/slate surfaces (`#18181b`, `#27272a`), and clean hairline border lines (`#27272a` / `#3f3f46`).
- **Monochromatic Accents:** Primarily near-colorless with stark white text (`#ffffff`, `#f4f4f5`) on dark backgrounds.
- **Controlled Semantic Accents:**
  - **Success / Activity:** Emerald green (`#10b981`, `bg-emerald-500/20 text-emerald-400 border-emerald-500/40`) representing completed habits, active progress, and heatmap high-intensity days.
  - **Danger / Errors:** Subdued crimson (`#ef4444`, `bg-red-950/40 border-red-800/60 text-red-300`).
  - **Muted Notes / Meta:** Zinc-400 / Zinc-500 for captions, timestamps, and subtitles.
- **Atmospheric Gradients & Texture Overlays:** Deep, dark, moody gradients (`from-zinc-900 via-zinc-950 to-black`) enhanced with subtle, low-contrast, monochrome background photography (`opacity-25`, `mix-blend-luminosity`) with deep edge vignetting.
- **Typography:** Ultra-clean sans-serif (Inter / Geist) with crisp weight distribution (bold tracking-tight headers, medium labels, regular body).
- **Surfaces & Borders:** 1px hairline borders (`border border-zinc-800`), gentle rounded corners (`rounded-lg` / `rounded-xl`), and dark backdrop blurs (`backdrop-blur-md`).

---

## 2. Branding & Header Proportions

- **Brand Mark:**
  - Standard container: `w-11 h-11 rounded-xl bg-zinc-950 border border-zinc-800/80 p-0.5 shadow-md`.
  - Icon: The Activity Heatmap Matrix (`logo.svg`), 7 calibrated tiles forming a 'u' with an active emerald pulse tile.
- **Title & Typography Hierarchy:**
  - App Name: `text-xl sm:text-2xl font-bold tracking-tight text-white leading-none`.
  - Subtitle: `text-[11px] text-zinc-500 font-medium tracking-wide` (*"Life & Media Chronicle"*).
- **Proportion Standard:** Sized deliberately to stand grounded and clearly visible without overpowering content panels.

---

## 3. Dynamic Interactivity & HTMX Feedback (Loaders & Toasts)

### 3.1 Buttons & Loading States (HTMX + Spinners)
Every interactive submit button or trigger must include an inline dynamic loading indicator to eliminate user friction and ambiguity:
- **Button Base:** `w-full py-2.5 px-4 bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-sm rounded-lg shadow-sm transition-all active:scale-[0.99] disabled:opacity-75 disabled:pointer-events-none relative flex items-center justify-center gap-2`.
- **Loading Spinner (htmx-indicator):** An SVG ring spinner hidden by default (`hidden` or `opacity-0`) that reveals automatically during in-flight network requests (`htmx-request:inline-block` or `htmx-request:opacity-100`).
- **Button Text Transition:** Swaps text or adds spinner seamlessly: *"Sign In"* $\rightarrow$ *"Signing in..."*.

### 3.2 Floating Dynamic Toasts (shadcn Sonner-style)
Flash notifications (messages) must not distort page layouts:
- **Placement:** Floating bottom-right (`fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 pointer-events-none`).
- **Container Card:** `pointer-events-auto flex items-start gap-3 p-3.5 rounded-xl bg-zinc-900/95 border border-zinc-800 text-zinc-100 shadow-2xl backdrop-blur-md text-sm max-w-sm w-full animate-in fade-in slide-in-from-bottom-3 duration-200`.
- **Dismissibility:** Dismiss button or auto-fade via minimal JavaScript/CSS.
- **Tone Indicators:** 
  - Success: emerald icon / badge.
  - Error: crimson icon / badge.
  - Info: zinc / white icon.

---

## 4. Authentication Screen Layout Standard

For all authentication screens (`sign-in`, `sign-up`, `forgot-password`, `reset-password`):
- **Desktop Layout:** 50/50 split grid (`grid grid-cols-1 lg:grid-cols-2 min-h-screen`).
  - **Left Column (Form Hub):**
    - Centered container (`max-w-sm w-full mx-auto my-auto`).
    - Prominent branded logo & title header.
    - Dark input fields (`bg-zinc-900/80 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 rounded-lg`).
    - Primary solid action button with HTMX loading spinner.
  - **Right Column (Visual & Reflective Experience):**
    - Hidden on mobile, flex on `lg:flex`.
    - Subtle monochrome textured backdrop (`auth-bg.jpg` at 25% opacity with luminosity blend) framed by dark radial vignettes.
    - Category pill (e.g. `Literature & Discovery`, `Retrospectives & Time`).
    - Curated, multi-sentence philosophical quotation rotated randomly from `accounts/quotes.py`.
    - Author attribution line with hairline accent separator.

---

## 5. Components & Forms Standard

### 5.1 Form Inputs & Dropdowns
```css
/* Input base */
w-full px-3.5 py-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800 text-zinc-100 placeholder:text-zinc-500 text-sm focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 transition-colors
```

### 5.2 Form Errors
- Red hairline border (`border-red-500/80`) on input.
- Error message immediately below input: `text-xs text-red-400 mt-1`.
- Non-field banner error: `p-3 text-xs rounded-lg border bg-red-950/40 border-red-800/60 text-red-300`.
