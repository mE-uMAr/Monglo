# Monglo Admin - Custom Branding Guide

The Monglo Admin panel supports full customization of branding.

## Quick Start

```python
from monglo.ui_helpers.fastapi import setup_ui

setup_ui(
    app,
    engine=engine,
    title="My App Admin",           # Custom title in sidebar
    logo="/static/my-logo.png",     # URL to logo image
    brand_color="#FF5722",          # Primary color (buttons, links)
    prefix="/admin"                 # URL prefix (default: /admin)
)
```

## Parameters

### `title` (str)
- **Default**: `"Monglo Admin"`
- Displayed in the sidebar header
- Shows in browser tab titles

### `logo` (str | None)
- **Default**: `None` (shows database icon)
- URL to your logo image
- Can be absolute URL or relative path
- Recommended size: 24px height, any width
- Example: `"/static/logo.png"` or `"https://example.com/logo.svg"`

### `brand_color` (str)
- **Default**: `"#10b981"` (green)
- CSS color value for primary brand color
- Affects buttons, links, highlights
- Accepts: hex (`#FF5722`), rgb (`rgb(255, 87, 34)`), named colors (`red`)

### `prefix` (str)
- **Default**: `"/admin"`
- URL prefix for admin panel
- Example: `"/dashboard"` → access at `http://localhost:8000/dashboard`

## Examples

### Minimal Setup
```python
setup_ui(app, engine=engine)
# Uses all defaults
```

### Custom Title Only
```python
setup_ui(app, engine=engine, title="Blog Admin")
```

### Full Branding
```python
setup_ui(
    app,
    engine=engine,
    title="E-Commerce Dashboard",
    logo="https://cdn.example.com/logo.svg",
    brand_color="#E91E63",
    prefix="/dashboard"
)
```

### Using Local Static Files
```python
from fastapi.staticfiles import StaticFiles

# Mount your static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Use logo from static files
setup_ui(
    app,
    engine=engine,
    logo="/static/images/logo.png"
)
```

## Logo Specifications

**Recommended:**
- Format: PNG or SVG
- Height: 24-32px
- Background: Transparent
- Style: Simple, recognizable icon or wordmark

**File placement:**
1. Create a `static` folder in your project
2. Add your logo: `static/logo.png`
3. Mount static files in FastAPI (see example above)
4. Reference in setup: `logo="/static/logo.png"`

## Tips

- **High contrast**: Ensure logo is visible on sidebar background
- **Responsive**: SVG logos scale better than PNG
- **Testing**: Restart server after changing logo files
- **Browser cache**: Hard refresh (Ctrl+Shift+R) to see logo changes
