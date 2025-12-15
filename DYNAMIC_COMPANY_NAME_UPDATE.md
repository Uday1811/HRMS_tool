# Dynamic Company Name Display - Update

## What Changed

The company name in both the **sidebar** and **navbar** now **dynamically changes** based on the logged-in user's company!

### Before
- Sidebar always showed "Petabytz" (hardcoded)
- Navbar didn't show company name

### After
- **Sidebar**: Shows company name dynamically
- **Navbar**: Shows company name next to menu icon
- **Petabytz users** see "Petabytz"
- **Bluebix users** see "Bluebix"  
- **Softstandard users** see "Softstandard"

---

## How It Works

### 1. Multi-Tenant Middleware
When a user logs in, the `MultiTenantMiddleware` attaches the company to the request:
```python
request.company = Company object (Petabytz/Bluebix/Softstandard)
```

### 2. Context Processor
The `company_context` processor makes company information available in all templates:
```python
# Available in all templates
{{ request.company.company }}  # Company name
{{ request.company.timezone }}  # Company timezone
{{ request.company.email_domain }}  # Company domain
```

### 3. Sidebar Template
The sidebar template now uses `request.company` to display the correct company:
```html
{% if request.company %}
  <span>{{ request.company.company }}</span>
{% endif %}
```

### 4. Navbar Template (index.html)
The navbar now shows the company name next to the menu icon:
```html
{% if request.company %}
  <span class="oh-navbar__page-title">
    {{ request.company.company }}
  </span>
{% endif %}
```

---

## Files Modified

1. **templates/sidebar.html**
   - Updated company display logic
   - Now checks `request.company` first
   - Falls back to session or employee company

2. **templates/index.html**
   - Added company name display in navbar
   - Shows company name next to menu icon
   - Uses `request.company` for dynamic display

3. **base/context_processors.py**
   - Added `company_context()` function
   - Makes company available in all templates

4. **horilla/settings.py**
   - Added `base.context_processors.company_context` to context processors

---

## Testing

### Test the Dynamic Company Name

1. **Login as Petabytz user**
   ```
   Email: test.petabytz@petabytz.com
   Password: password123
   ```
   ✅ Sidebar should show "Petabytz"

2. **Logout and login as Bluebix user**
   ```
   Email: test.bluebix@bluebix.com
   Password: password123
   ```
   ✅ Sidebar should show "Bluebix"

3. **Logout and login as Softstandard user**
   ```
   Email: test.india@softstandard.com
   Password: password123
   ```
   ✅ Sidebar should show "Softstandard"

---

## Benefits

✅ **Automatic** - No manual configuration needed  
✅ **Secure** - Company is validated by middleware  
✅ **Consistent** - Same company shown everywhere  
✅ **Multi-tenant** - Each company sees their own name  

---

## Additional Template Variables

You can now use these in any template:

```django
{{ request.company }}  {# Company object #}
{{ request.company.company }}  {# Company name #}
{{ request.company.timezone }}  {# Company timezone #}
{{ request.company.email_domain }}  {# Company domain #}
{{ request.company.country_code }}  {# Country code #}
{{ request.company.is_multi_location }}  {# Multi-location flag #}

{# Or use context processor variables #}
{{ current_company }}  {# Same as request.company #}
{{ current_company_name }}  {# Company name #}
{{ current_company_timezone }}  {# Company timezone #}
```

---

## Example Usage

### Display Company Name in Header
```html
<h1>Welcome to {{ request.company.company }}</h1>
```

### Show Company-Specific Message
```html
{% if request.company.company == "Petabytz" %}
  <p>Welcome to Petabytz India!</p>
{% elif request.company.company == "Bluebix" %}
  <p>Welcome to Bluebix USA!</p>
{% elif request.company.company == "Softstandard" %}
  <p>Welcome to Softstandard!</p>
{% endif %}
```

### Display Timezone
```html
<p>Your timezone: {{ request.company.timezone }}</p>
```

---

## 🎉 Complete!

The company name now dynamically changes based on the logged-in user's company. This is part of the multi-tenant HRMS system with strict company-based isolation.

**Test it now by logging in with different company users!**
