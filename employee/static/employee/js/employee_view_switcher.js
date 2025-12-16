// Employee View Switcher
function switchEmployeeView(viewType) {
    const listView = document.getElementById('view-container');
    const hierarchyView = document.getElementById('hierarchy-view');
    const tabs = document.querySelectorAll('.view-tab-btn');

    // Update tab active states
    tabs.forEach(tab => {
        if (tab.getAttribute('data-view') === viewType) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    // Switch views
    if (viewType === 'hierarchy') {
        listView.style.display = 'none';
        hierarchyView.style.display = 'block';

        // Store preference
        localStorage.setItem('employeeViewPreference', 'hierarchy');
    } else {
        listView.style.display = 'block';
        hierarchyView.style.display = 'none';

        // Store preference
        localStorage.setItem('employeeViewPreference', 'list');
    }
}

// Restore view preference on page load
document.addEventListener('DOMContentLoaded', function () {
    const savedView = localStorage.getItem('employeeViewPreference');
    if (savedView) {
        switchEmployeeView(savedView);
    }
});
