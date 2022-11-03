document.addEventListener('DOMContentLoaded', function() {

    // Add event listener to all edit links for switching between edit forms and the post itself
    document.querySelectorAll('.edit').forEach(editLink => {
        editLink.addEventListener('click', function() {
            switchView(true, this.dataset.id);
        });
    });

    // Hide all edit forms and add event listener to all edit forms
    document.querySelectorAll('.edit-form').forEach(form => {
        // Hide form
        switchView(false, form.dataset.id);
        form.addEventListener('submit', function() {
            // Call editPost with the post ID and textarea content
            editPost(form.dataset.id, form.querySelector("textarea").value);
        });
    });

    // Add event listener to all like/unlike links
    document.querySelectorAll('.fa').forEach(likeLink => {
        likeLink.addEventListener('click', function() {
            // Call likePost with the post ID
            likePost(likeLink.dataset.id);
        });
    });
});

function editPost(postID, newContent) {
    /**
     * Edits the contents of a post
     */

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch(`/editpost/${postID}`, {
        method: 'PUT',
        headers: {"X-CSRFToken": token},
        body: JSON.stringify({
            content: newContent
        })
    })
        .then(response => response.json())
        .then(result => {
            // Update the post
            document.querySelector(`.post-content[data-id="${postID}"]`).innerHTML = result.content;
            // Hide the edit post form and show the post itself
            switchView(false, postID);
        })
        .catch(error => {
            console.log(error);
        });

    // Prevent the form from submitting
    return false;
}

function likePost(id) {
    /**
     * Switches the like/unlike state of a post for the current user.
     */

    // Get the CSRF token
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch(`/switchlike/${id}`, {
        method: 'PUT',
        headers: {"X-CSRFToken": token}
    })
        .then(response => response.json())
        .then(likes => {
            // Update the number of likes value in HTML
            document.querySelector(`.post-num-of-likes[data-id="${id}"]`).innerHTML = likes.num_of_likes;

            if (likes.flag) {
                // Switch the icon to liked
                document.querySelector(`.fa[data-id="${id}"]`).classList.remove('fa-thumbs-o-up');
                document.querySelector(`.fa[data-id="${id}"]`).classList.add('fa-thumbs-up');

            } else {
                // Switch the icon to not liked
                document.querySelector(`.fa[data-id="${id}"]`).classList.remove('fa-thumbs-up');
                document.querySelector(`.fa[data-id="${id}"]`).classList.add('fa-thumbs-o-up');
            }
        });

    return false;
}

function switchView(showEditBox, postID) {
    /**
     * Switches between the edit post form and the post itself.
     */

    if (showEditBox) {
        // Show the edit post form and hide the post itself
        document.querySelector(`.post-content[data-id="${postID}"]`).style.display = 'none';
        document.querySelector(`.edit-post[data-id="${postID}"]`).style.display = 'block';
        // Try to hide the edit link, ignore if it does not exist
        try {
            document.querySelector(`.edit[data-id="${postID}"]`).style.display = 'none';
        } catch(error) {
            // ignore if there is no edit button
        }
    } else {
        // Show the post itself and hide the edit post form
        document.querySelector(`.post-content[data-id="${postID}"]`).style.display = 'block';
        document.querySelector(`.edit-post[data-id="${postID}"]`).style.display = 'none';
        // Try to show the edit link, ignore if it does not exist
        try {
            document.querySelector(`.edit[data-id="${postID}"]`).style.display = 'block';
        } catch(error) {
            // ignore if there is no edit button
        }
    }
}


