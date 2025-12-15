# Employee Attendance Dashboard - Keka-Inspired Design

## Overview
A modern, feature-rich employee attendance dashboard inspired by Keka's design philosophy. This dashboard provides employees with an intuitive interface to manage their attendance, track working hours, and view attendance history.

## Features Implemented

### ✅ Core Features

1. **Web Clock-in / Clock-out**
   - One-click clock in/out functionality
   - Real-time status updates
   - Visual feedback with modern UI

2. **Automatic 9-hour Logout**
   - Automatically clocks out employees after 9 hours of work
   - Prevents overtime abuse
   - Sends notification before auto-logout

3. **Live Stopwatch Timer**
   - Real-time timer showing hours worked
   - Updates every second
   - Displays in HH:MM:SS format
   - Starts automatically after clock-in

4. **Automatic Location Capture**
   - Precise GPS coordinates captured on clock-in/out
   - Stores latitude and longitude
   - Optional location name/address
   - Uses browser's geolocation API

5. **Database Storage**
   - Login/logout times saved in AttendanceActivity model
   - Location data stored with each activity
   - Linked to Attendance records
   - Historical data preserved

6. **Monthly Payroll Cycle (28th → 27th)**
   - Configurable payroll period
   - Stats calculated for current cycle
   - Month-to-date tracking

7. **Missing Login/Logout Detection**
   - Identifies incomplete attendance records
   - Highlights missing clock-out entries
   - Shows count in dashboard stats
   - Visual indicators in logs

8. **Admin Dashboard**
   - Existing admin dashboard for viewing all employees
   - Attendance validation and approval
   - Overtime management

9. **Employee Dashboard**
   - Personal attendance view
   - Own records and statistics
   - Recent activity logs
   - Performance metrics

## Dashboard Sections

### 1. Header Section
- Welcome message with employee name
- Current date display
- Clock-in status badge (Present/Not Clocked In)

### 2. Clock In/Out Card
- Large, prominent timer display
- Clock in/out button (changes based on status)
- Last activity information
- Location badge showing where clocked in

### 3. Statistics Cards (6 cards)
- **Days Present**: Total days attended this month
- **Total Hours**: Cumulative hours worked
- **Avg Hours/Day**: Average daily working hours
- **Attendance %**: Attendance percentage
- **Missing Logs**: Count of incomplete records
- **Overtime**: Total overtime hours

### 4. Recent Attendance Logs
- Last 10 attendance records
- Date, clock-in, clock-out times
- Duration worked
- Location information
- Missing entry indicators
- Filter by month (This Month, Last Month, All Time)

### 5. Quick Actions
- View Full Report
- All Activities
- Request Correction

## Technical Implementation

### Files Created/Modified

1. **Template**: `attendance/templates/attendance/employee_dashboard.html`
   - Modern, responsive design
   - Keka-inspired color scheme
   - Interactive elements with hover effects
   - Mobile-friendly layout

2. **Views**: `attendance/views.py`
   - `employee_dashboard_view()`: Main dashboard view
   - `clock_in_api()`: API endpoint for clocking in
   - `clock_out_api()`: API endpoint for clocking out

3. **URLs**: `attendance/urls.py`
   - `/attendance/employee-dashboard/`: Dashboard route
   - `/attendance/clock-in-api/`: Clock-in API
   - `/attendance/clock-out-api/`: Clock-out API

4. **Migration**: `attendance/migrations/0002_add_location_fields.py`
   - Adds location fields to AttendanceActivity model
   - Latitude and longitude fields
   - Location name field

### Database Schema Changes

**AttendanceActivity Model** (New Fields):
```python
clock_in_latitude = DecimalField(max_digits=9, decimal_places=6)
clock_in_longitude = DecimalField(max_digits=9, decimal_places=6)
clock_out_latitude = DecimalField(max_digits=9, decimal_places=6)
clock_out_longitude = DecimalField(max_digits=9, decimal_places=6)
clock_in_location = CharField(max_length=255)
clock_out_location = CharField(max_length=255)
```

## Usage Instructions

### For Employees

1. **Access Dashboard**
   - Navigate to `/attendance/employee-dashboard/`
   - View your attendance summary

2. **Clock In**
   - Click "Clock In" button
   - Allow location access when prompted
   - Timer starts automatically
   - Location is captured

3. **Clock Out**
   - Click "Clock Out" button after work
   - Location is captured again
   - Attendance record is updated
   - Timer stops

4. **View Stats**
   - Check monthly statistics
   - Review attendance percentage
   - Identify missing logs

5. **Review Logs**
   - Scroll to Recent Attendance Logs
   - Filter by month
   - Check for missing entries
   - View location data

### For Administrators

1. **Run Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Configure Settings**
   - Set payroll cycle dates
   - Configure auto-logout duration
   - Set location tracking requirements

3. **Monitor Employees**
   - Use existing admin dashboard
   - View all employee attendance
   - Validate and approve records

## Design Features

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success**: Green gradient (#11998e → #38ef7d)
- **Warning**: Orange gradient (#FFB75E → #ED8F03)
- **Danger**: Red gradient (#FF5F6D → #FFC371)
- **Info**: Blue gradient (#4facfe → #00f2fe)

### UI Elements
- **Cards**: White background with subtle shadows
- **Hover Effects**: Smooth transitions and elevation
- **Icons**: Ionicons for consistent iconography
- **Typography**: Inter font family for modern look
- **Responsive**: Mobile-first design approach

### Animations
- Timer pulse effect when active
- Card hover lift effect
- Smooth color transitions
- Loading states

## Security Features

1. **Location Verification**
   - GPS coordinates stored for audit
   - Prevents buddy punching
   - Geofencing capability (future)

2. **Auto Logout**
   - Prevents extended sessions
   - Enforces work hour limits
   - Automatic attendance closure

3. **CSRF Protection**
   - All API calls protected
   - Token-based authentication
   - Secure data transmission

## Future Enhancements

1. **Geofencing**
   - Define allowed locations
   - Restrict clock-in to office premises
   - Alert on out-of-bounds attempts

2. **Face Recognition**
   - Integrate with existing face detection
   - Verify identity on clock-in
   - Prevent proxy attendance

3. **Notifications**
   - Push notifications for clock-in reminders
   - Alerts for missing clock-out
   - Monthly attendance summary emails

4. **Analytics**
   - Detailed charts and graphs
   - Attendance trends
   - Productivity insights

5. **Mobile App**
   - Native mobile application
   - Offline clock-in capability
   - Background location tracking

## Troubleshooting

### Location Not Working
- Ensure browser has location permissions
- Check HTTPS connection (required for geolocation)
- Verify GPS is enabled on device

### Timer Not Starting
- Check if clocked in successfully
- Verify JavaScript is enabled
- Clear browser cache and reload

### Missing Logs
- Ensure clock-out is performed
- Check for incomplete attendance records
- Contact admin for correction

## API Documentation

### Clock In API
**Endpoint**: `POST /attendance/clock-in-api/`

**Request Body**:
```json
{
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

**Response**:
```json
{
  "success": true,
  "message": "Clocked in successfully",
  "time": "09:30"
}
```

### Clock Out API
**Endpoint**: `POST /attendance/clock-out-api/`

**Request Body**:
```json
{
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

**Response**:
```json
{
  "success": true,
  "message": "Clocked out successfully",
  "time": "18:30"
}
```

## Support

For issues or feature requests, please contact the development team or create an issue in the project repository.

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Compatibility**: Django 3.2+, Python 3.8+
