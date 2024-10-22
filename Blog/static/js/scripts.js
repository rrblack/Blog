window.addEventListener('DOMContentLoaded', () => {
    // Log to confirm the script is loading
    console.log("Script Loaded. Attaching event listeners...");

    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;

    window.addEventListener('scroll', function () {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if (currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove('is-visible');
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });

// Confirmation Dialog for Deleting a Post
    const deleteButtons = document.querySelectorAll('.btn-delete');

    // Check if delete buttons exist
    if (deleteButtons.length === 0) {
        console.warn("No delete buttons found.");
    }

    // Attach event listener to each delete button
    deleteButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            console.log("Delete button clicked.");

            // Stop Bootstrap link from following immediately
            event.preventDefault();

            // Confirmation dialog
            if (confirm('Are you sure you want to delete this post?')) {
                // If confirmed, proceed with navigation
                window.location.href = button.href;
                console.log("Post deletion confirmed.");
            } else {
                // Otherwise, prevent deletion
                console.log("Deletion canceled.");
            }
        });
    });
});