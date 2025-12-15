# Quick Start Guide - Team Hierarchy Feature

## What's New? 🎉

I've created an **advanced, modern Team Hierarchy view** for your HRMS tool that displays organizational structure in a beautiful, interactive interface.

## Files Created

1. **Template:** `employee/templates/employee/team_hierarchy.html`
2. **CSS:** `employee/static/employee/css/team_hierarchy.css`
3. **JavaScript:** `employee/static/employee/js/team_hierarchy.js`
4. **View Function:** Added `team_hierarchy_view()` to `employee/views.py`
5. **URL:** Added route in `employee/urls.py`
6. **Sidebar:** Updated `employee/sidebar.py` with new menu item

## How to Use

### Step 1: Start Your Server
```bash
python manage.py runserver
```

### Step 2: Access the Page
Navigate to: `http://localhost:8000/employee/team-hierarchy/`

Or click **"Team Hierarchy"** in the Employee sidebar menu.

### Step 3: View Your Team Structure

The page will show:

#### 📊 Reporting Manager (Top)
- Your direct manager's profile card
- Purple gradient border
- Contact information
- "View Profile" button

#### 👤 You (Center - Highlighted)
- Your profile prominently displayed
- Pink gradient border with larger shadow
- Pulsing online status indicator
- "Edit Profile" button for quick access

#### 👥 Team Peers (Side-by-side)
- Colleagues with the same role and manager
- Grid layout showing up to 10 peers
- Online/offline status indicators
- Quick "View" buttons

#### 🌳 Direct Reportees (Bottom)
- All employees reporting to you
- Grid layout, alphabetically sorted
- Full contact information
- Quick access to profiles

## Features Highlights

### 🎨 Modern Design
- **Gradient backgrounds** with purple and pink themes
- **Glassmorphism effects** for a premium look
- **Smooth animations** on scroll and hover
- **3D tilt effects** when hovering over cards
- **Ripple animations** on click

### 📱 Responsive
- Works perfectly on desktop, tablet, and mobile
- Adaptive grid layouts
- Touch-friendly on mobile devices

### ♿ Accessible
- Keyboard navigation support
- Screen reader friendly
- ARIA labels for all interactive elements
- Focus indicators

### ⚡ Performance
- Lazy loading for images
- Optimized animations
- Efficient database queries
- Limited peer count for speed

## Customization

### Change Colors
Edit `employee/static/employee/css/team_hierarchy.css`:

```css
:root {
    --primary-gradient: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
    --secondary-gradient: linear-gradient(135deg, #YOUR_COLOR_3, #YOUR_COLOR_4);
}
```

### Change Peer Limit
Edit `employee/views.py` in the `team_hierarchy_view` function:

```python
peers = Employee.objects.filter(...).exclude(id=employee.id)[:10]  # Change 10
```

### Modify Card Layout
Edit the grid columns in CSS:

```css
.peers-grid,
.reportees-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    /* Change 280px to adjust card width */
}
```

## What Each Section Shows

### Reporting Manager Card
- Profile image or placeholder icon
- Full name
- Job position
- Badge ID
- Email address
- Department
- "View Profile" button

### Your Card (Current Employee)
- All of the above, plus:
- Highlighted with special gradient
- Pulsing online indicator
- "Edit Profile" button instead

### Peer Cards
- Profile image
- Name and position
- Badge ID
- Email
- Online/offline status
- Compact "View" button

### Reportee Cards
- Same as peer cards
- Shows everyone reporting to you
- Sorted alphabetically

## Empty States

If you don't have:
- **No reporting manager:** Manager section won't show
- **No peers:** Peers section won't show
- **No reportees:** Reportees section won't show
- **No team at all:** Shows friendly empty state message

## Interactive Features

### Hover Effects
- Cards lift up with shadow
- 3D tilt effect follows mouse
- Smooth transitions

### Click Effects
- Ripple animation from click point
- Navigates to profile pages

### Scroll Animations
- Sections fade in as you scroll
- Staggered timing for visual appeal

### Keyboard Navigation
- Tab through cards
- Enter/Space to activate buttons
- Escape to blur focus

## Browser Support

✅ Chrome/Edge (latest)
✅ Firefox (latest)
✅ Safari (latest)
✅ Mobile browsers

## Troubleshooting

### Page Not Loading?
1. Check if server is running: `python manage.py runserver`
2. Verify URL: `http://localhost:8000/employee/team-hierarchy/`
3. Check browser console for errors

### No Team Members Showing?
1. Ensure employees have `reporting_manager_id` set in work info
2. Check if employees have `job_position_id` assigned
3. Verify employees are marked as `is_active=True`

### CSS Not Applied?
1. Run: `python manage.py collectstatic`
2. Clear browser cache (Ctrl+Shift+R)
3. Check static files configuration

### JavaScript Not Working?
1. Check browser console for errors
2. Ensure Ion Icons library is loaded
3. Verify JS file path in template

## Next Steps

1. ✅ Access the page and explore the interface
2. ✅ Test with different employee accounts
3. ✅ Customize colors to match your brand
4. ✅ Add more team members to see the full effect
5. ✅ Share feedback for improvements!

## Need Help?

Refer to the detailed documentation in `TEAM_HIERARCHY_README.md` for:
- Complete feature breakdown
- Technical details
- Advanced customization
- Future enhancement ideas

---

**Enjoy your new Team Hierarchy view! 🚀**
