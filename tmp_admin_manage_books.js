
function approveBook(bookId) {
    showConfirmModal(
        '<i class="fas fa-check-circle"></i> <strong>Approve Book?</strong><br><small>It will be published and visible to users.</small>',
        function() {
            fetch('/api/admin/approve-book/' + bookId, {method: 'POST', credentials: 'same-origin'})
                .then(r => {
                    if (!r.ok) throw new Error('Server error: ' + r.status);
                    return r.json();
                })
                .then(d => {
                    if (d.success) {
                        showSuccessModal('Book approved successfully');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showErrorModal(d.error || 'Error approving book');
                    }
                })
                .catch(e => showErrorModal('Network error: ' + e.message));
        }
    );
}

function rejectBook(bookId) {
    showRejectionModal(function(reason) {
        fetch('/api/admin/reject-book/' + bookId, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({reason: reason})
        })
        .then(r => {
            if (!r.ok) throw new Error('Server error: ' + r.status);
            return r.json();
        })
        .then(d => {
            if (d.success) {
                showSuccessModal('Book rejected successfully');
                setTimeout(() => location.reload(), 1500);
            } else {
                showErrorModal(d.error || 'Error rejecting book');
            }
        })
        .catch(e => showErrorModal('Network error: ' + e.message));
    });
}

function deleteBook(bookId) {
    showConfirmModal(
        '<i class="fas fa-trash"></i> <strong>Delete Book?</strong><br><small class="text-danger">This action cannot be undone.</small>',
        function() {
            fetch('/api/admin/delete-book/' + bookId, {method: 'POST', credentials: 'same-origin'})
                .then(r => {
                    if (!r.ok) throw new Error('Server error: ' + r.status);
                    return r.json();
                })
                .then(d => {
                    if (d.success) {
                        showSuccessModal('Book deleted successfully');
                        setTimeout(() => location.reload(), 1500);
                    } else {
                        showErrorModal(d.error || 'Error deleting book');
                    }
                })
                .catch(e => showErrorModal('Network error: ' + e.message));
        }
    );
}


        let pendingAction = null;
        let selectedRating = 0;
        let pendingBookId = null;
        let pendingRejectionAction = null;

        function showConfirmModal(message, action) {
            document.getElementById('modalBody').innerHTML = message;
            pendingAction = action;
            new bootstrap.Modal(document.getElementById('confirmModal')).show();
        }

        function executeAction() {
            if (pendingAction) {
                pendingAction();
            }
        }

        function showSuccessModal(message) {
            document.getElementById('successBody').innerHTML = message;
            new bootstrap.Modal(document.getElementById('successModal')).show();
        }

        function showErrorModal(message) {
            document.getElementById('errorBody').innerHTML = message;
            new bootstrap.Modal(document.getElementById('errorModal')).show();
        }

        function showRejectionModal(action) {
            document.getElementById('rejectionReason').value = '';
            pendingRejectionAction = action;
            new bootstrap.Modal(document.getElementById('rejectionModal')).show();
        }

        function submitRejection() {
            const reason = document.getElementById('rejectionReason').value.trim();
            if (!reason) {
                showErrorModal('Please provide a reason for rejection');
                return;
            }
            bootstrap.Modal.getInstance(document.getElementById('rejectionModal')).hide();
            if (pendingRejectionAction) {
                pendingRejectionAction(reason);
            }
        }

        function setRating(rating) {
            selectedRating = rating;
            document.getElementById('ratingText').innerHTML = `<strong>${rating} out of 5 stars</strong>`;
            
            const stars = document.querySelectorAll('#ratingStars i');
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.style.color = '#ffc107';
                } else {
                    star.style.color = '#ccc';
                }
            });
        }

        function submitRating() {
            if (selectedRating === 0) {
                showErrorModal('Please select a rating');
                return;
            }
            
            if (pendingBookId) {
                fetch('/api/rate-book/' + pendingBookId, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({rating: selectedRating})
                })
                .then(r => r.json())
                .then(d => {
                    if (d.success) {
                        bootstrap.Modal.getInstance(document.getElementById('ratingModal')).hide();
                        showSuccessModal('Thank you for rating!');
                        setTimeout(() => location.reload(), 1500);
                    }
                });
            }
        }

        function showRatingModal(bookId) {
            pendingBookId = bookId;
            selectedRating = 0;
            document.getElementById('ratingText').innerHTML = 'Click to select rating';
            const stars = document.querySelectorAll('#ratingStars i');
            stars.forEach(star => star.style.color = '#ccc');
            new bootstrap.Modal(document.getElementById('ratingModal')).show();
        }

        function saveBook(bookId) {
            showConfirmModal(
                '<i class="fas fa-bookmark"></i> <strong>Save Book?</strong><br><small>This book will be added to your saved collection.</small>',
                function() {
                    fetch('/api/save-book/' + bookId, {method: 'POST'})
                        .then(r => r.json())
                        .then(d => {
                            if (d.success) {
                                showSuccessModal('Book saved successfully');
                                setTimeout(() => location.reload(), 1500);
                            }
                        });
                }
            );
        }

        function toggleSave(bookId) {
            saveBook(bookId);
        }

        function unsaveBook(bookId) {
            showConfirmModal(
                '<i class="fas fa-trash"></i> <strong>Remove from saved?</strong><br><small>This book will be removed from your saved collection.</small>',
                function() {
                    fetch('/api/unsave-book/' + bookId, {method: 'POST'})
                        .then(r => r.json())
                        .then(d => {
                            if (d.success) {
                                showSuccessModal('Book removed from saved');
                                setTimeout(() => location.reload(), 1500);
                            }
                        });
                }
            );
        }
    