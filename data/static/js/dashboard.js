
document.addEventListener('DOMContentLoaded', () => {
    const currentDate = new Date();
    const currentDay = currentDate.getDate();
    const calenderDays = document.querySelectorAll('.calender-day');
    const taskList = document.getElementById('task-list');

    // Task data for different dates (for example purposes)
    const tasksData = {
        '1': [
            { task: 'Working on Asia Project', time: '08:00 - 10:00 AM' },
            { task: 'Team Meeting', time: '10:00 - 12:00 PM' }
        ],
        '2': [
            { task: 'Research Task', time: '09:00 - 11:00 AM' }
        ],
        // Add more dates and tasks here
        '30': [
            { task: 'Finalize Reports', time: '03:00 - 05:00 PM' }
        ]
    };

    // Function to update the task list based on the selected date
    function updateTaskList(date) {
        const tasks = tasksData[date] || [];
        taskList.innerHTML = tasks.map(task => `
            <li class="flex justify-between items-center">
                <span>${task.task}</span>
                <span class="text-gray-500">${task.time}</span>
            </li>
        `).join('');
    }

    // Set the current day as highlighted
    calenderDays.forEach(day => {
        if (parseInt(day.textContent) === currentDay) {
            day.classList.add('bg-purple-600', 'text-white');
            day.classList.remove('text-gray-700');
        }
    });

    // Add event listeners for each date
    calenderDays.forEach(day => {
        day.addEventListener('click', () => {
            // Remove highlight from previous selected day
            calenderDays.forEach(d => d.classList.remove('bg-purple-600', 'text-white'));
            day.classList.add('bg-purple-600', 'text-white');
            day.classList.remove('text-gray-700');

            // Update the tasks for the clicked date
            updateTaskList(day.textContent);
        });
    });

    // Set the default task list for the current date
    updateTaskList(currentDay);
});
