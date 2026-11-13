---
name: Verdant Precision
colors:
  surface: '#f0fcf6'
  surface-dim: '#d0ddd7'
  surface-bright: '#f0fcf6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eaf7f0'
  surface-container: '#e4f1ea'
  surface-container-high: '#dfebe5'
  surface-container-highest: '#d9e5df'
  on-surface: '#131e1a'
  on-surface-variant: '#3f4944'
  inverse-surface: '#28332f'
  inverse-on-surface: '#e7f4ed'
  outline: '#6f7974'
  outline-variant: '#bec9c3'
  surface-tint: '#166b55'
  primary: '#00513f'
  on-primary: '#ffffff'
  primary-container: '#176b55'
  on-primary-container: '#9be9cd'
  inverse-primary: '#89d5ba'
  secondary: '#3d6753'
  on-secondary: '#ffffff'
  secondary-container: '#bfedd4'
  on-secondary-container: '#436d59'
  tertiary: '#3e4945'
  on-tertiary: '#ffffff'
  tertiary-container: '#56615d'
  on-tertiary-container: '#d0dcd6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a4f2d6'
  primary-fixed-dim: '#89d5ba'
  on-primary-fixed: '#002117'
  on-primary-fixed-variant: '#00513f'
  secondary-fixed: '#bfedd4'
  secondary-fixed-dim: '#a4d0b9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#254e3c'
  tertiary-fixed: '#d9e5df'
  tertiary-fixed-dim: '#bdc9c4'
  on-tertiary-fixed: '#131e1a'
  on-tertiary-fixed-variant: '#3e4945'
  background: '#f0fcf6'
  on-background: '#131e1a'
  surface-variant: '#d9e5df'
typography:
  display-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Manrope
    fontSize: 15px
    fontWeight: '500'
    lineHeight: 22px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  data-mono:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style
The design system establishes a disciplined, trustworthy, and luminous aesthetic tailored for intelligent financial statement analysis. Stripping away decorative tech-debt—such as neon accents, heavy dark schemes, glassy blurs, and chromatic gradients—this design system embraces a pristine, solid-color architectural minimalism.

The visual language communicates institutional precision, total clarity, and calm efficiency. Interactions feel tactile, balanced, and instantly legible, evoking confidence for auditors, finance operators, and wealth managers parsing dense monetary data under tight operational deadlines.

## Colors
The palette is built strictly around solid, opaque swatches with zero gradients. Contrast and status mapping are prioritized to maintain pristine data hierarchy across complex transaction reports and ledger sheets.

### Core Canvas & Structure
- **Primary Canvas (`#F8FAF9`)**: A soft, non-clinical tinted white that provides comfortable prolonged viewing without eye fatigue.
- **Card Surface (`#FFFFFF`)**: Pure solid white used for active panels, data grids, and modals, floating with crisp delineation over the canvas.
- **Subtle Surface / Neutral Tint (`#F1F4F2`)**: Applied to table header strips, disabled controls, search bars, and summary metric pods.
- **Structural Border (`#E7ECE9`)**: An exact, hairline boundary tone used to define table rows, cell separators, and card perimeters.

### Brand & Interactive Tones
- **Primary Brand (`#176B55`)**: A deep, authoritative evergreen representing solvency, stability, and decisive primary actions.
- **Primary Hover (`#125642`)**: High-contrast interaction state for primary focus and depressed trigger states.
- **Soft Mint Accent (`#E8F4EE`)**: High-legibility background fill for tags, active tab selections, filters, and row highlights.
- **Secondary Sage (`#A8D5BD`)**: Subtle boundary accents, balance indicator bars, and active indicator pips.

### Content & Semantics
- **Main Text (`#202B27`)**: Deep forest charcoal providing maximum alphanumeric contrast without the harshness of pure `#000000`.
- **Secondary Text (`#77847E`)**: Muted neutral for table sub-headers, transaction timestamps, metadata, and helper text.
- **Success (`#23865A`)**: Solid credit, positive delta, and verified statement status.
- **Warning (`#D99A35`)**: Solid ledger mismatch, duplicate flags, and manual verification needed.
- **Danger (`#D95C5C`)**: Solid overdraft alerts, debit flags, failed reconciliations, and critical system errors.

## Typography
The system couples Manrope’s geometric warmth for structural headings with Inter’s objective legibility for dense tabular and transactional interfaces. Headings deliberately avoid heavy, aggressive weights, relying on Medium (500) and Semi-Bold (600) to balance authority with Scandinavian restraint.

### Financial Numbers & Monospacing
- Numeric amounts, account references, and financial metrics utilize standard Inter with tabular figure open-type features (`tnum`, `cv05`) enabled, ensuring perfect vertical decimal alignment across ledger columns.
- Currency markers remain one size smaller or set at secondary tone `#77847E` to highlight pure value changes over symbolic glyphs.

## Layout & Spacing
The layout adheres to an operational grid built to display maximum analytical intelligence without crowding. It employs a responsive 12-column layout on desktop, condensing to 8 columns on tablet and 4 columns on mobile.

### Spatial Rhythms
- **Data Densities**: Financial statements require tight, consistent scanning lines. Table row heights are standard 40px (compact) or 48px (standard), using `space-md` for internal horizontal cell padding.
- **Section Hierarchy**: Outer canvas padding preserves breathing room (`margin-desktop: 2rem`), while nested components and cards nest tightly with consistent `space-lg` and `space-xl` gaps to keep relationships immediate and clear.
- **Adaptation Rules**: Multi-column account reconciliations collapse horizontally into stacked expandable cards under 768px viewports. Numeric columns anchor right; text identifiers anchor left.

## Elevation & Depth
Depth is strictly structured through tonal surface stacking and subtle ambient shadows. Translucent glass effects, blur-filters, and saturated drop shadows are explicitly forbidden.

### Depth Hierarchy
1. **Canvas Layer (`#F8FAF9`)**: Base system backdrop.
2. **Surface Layer (`#FFFFFF`)**: Cards, panels, side rails, and data grids sit atop the base with a hairline `1px solid #E7ECE9` border and a delicate, diffused ambient shadow: `box-shadow: 0 1px 3px rgba(32, 43, 39, 0.04), 0 1px 2px rgba(32, 43, 39, 0.02)`.
3. **Elevated Layer (Popovers, Filter Menus, Flyouts)**: Retains `#FFFFFF` fill with `1px solid #E7ECE9` and an expanded subtle boundary: `box-shadow: 0 4px 12px rgba(32, 43, 39, 0.06), 0 1px 3px rgba(32, 43, 39, 0.04)`.
4. **Modal Layer (Transaction Detail / File Ingestion Overlays)**: Sits over an opaque canvas overlay (`rgba(32, 43, 39, 0.40)`) with `box-shadow: 0 8px 24px rgba(32, 43, 39, 0.08)`.

## Shapes
Component geometry utilizes an architectural 10px–14px radius curve range, creating a polished, modern, yet strictly institutional appearance.

### Geometric Scale
- **Small Elements (10px / `0.625rem`)**: Tags, status badges, utility buttons, inline code blocks, and check controls.
- **Standard Controls (12px / `0.75rem`)**: Primary buttons, input fields, date pickers, table header pills, and dropdown selectors.
- **Containers & Surfaces (14px / `0.875rem`)**: Data tables, financial statement previewers, reconciliation panels, and KPI cards.
- **Pill Radius (Full / `9999px`)**: Exclusively reserved for quantitative badges (e.g., matching confidence scores, delta percentages).

## Components

### Buttons
- **Primary**: Solid `#176B55` background, `#FFFFFF` text, 12px border radius. Hover: `#125642`. Active: `#0E4333`. Never use gradients or heavy glow.
- **Secondary**: Solid `#FFFFFF` background, `1px solid #E7ECE9` border, `#202B27` text. Hover: `#F1F4F2` background, `#176B55` border.
- **Tertiary / Ghost**: Transparent background, `#176B55` text. Hover: `#E8F4EE` solid background.
- **Destructive**: Solid `#D95C5C` background, `#FFFFFF` text. Hover: `#C34949`.

### Chips & Badges
- **Status Tags**: Solid background `#E8F4EE`, text `#176B55`, 10px radius, 0.25rem 0.5rem padding.
- **Categorization Pills**: `#F1F4F2` solid background, `#77847E` text.
- **Alert Flags (Credit/Debit/Pending)**:
  - Credit: Background `#E8F4EE`, text `#23865A`.
  - Debit: Background `#FDF2F2`, text `#D95C5C`.
  - Review Needed: Background `#FDF8EE`, text `#D99A35`.

### Input Fields & Controls
- **Inputs & Selects**: Height 40px, solid `#FFFFFF` background, `1px solid #E7ECE9` border, 12px radius, text `#202B27`. Placeholder: `#77847E`.
- **Focus State**: `1px solid #176B55` border with a crisp `0 0 0 3px #E8F4EE` ring outline.
- **Checkboxes & Radios**: 18px size, 4px radius for checkbox, fully rounded for radio. Unselected: `1px solid #E7ECE9`, `#FFFFFF` fill. Selected: Solid `#176B55` fill with pure `#FFFFFF` icon mark.

### Financial Tables & Data Grids
- **Header**: `#F1F4F2` solid background, text `#77847E`, 11px uppercase label font, 36px row height, bottom border `1px solid #E7ECE9`.
- **Row**: `#FFFFFF` background, 44px height, `1px solid #E7ECE9` row divider. Row hover: `#F8FAF9`.
- **Numeric Alignment**: All monetary balances, amounts, and dates are right-aligned using tabular figures (`data-mono`).

### Cards & Analytical Widgets
- **Card**: Pure `#FFFFFF` background, `1px solid #E7ECE9` border, 14px radius, padded with `1.25rem`.
- **KPI Summary Tile**: Displays top metric label in `#77847E` (`label-sm`), main value in `#202B27` (`headline-lg`), and secondary status indicator pill aligned to top right.