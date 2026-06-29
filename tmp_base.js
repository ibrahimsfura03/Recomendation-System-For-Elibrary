
        let pendingAction = null;
        let selectedRating = 0;
        let pendingBookId = null;
        let pendingRejectionAction = null;

        function isBootstrapAvailable() {
            return typeof bootstrap !== 'undefined' && typeof bootstrap.Modal === 'function';
        }

        function sanitizeText(html) {
            const div = document.createElement('div');
            div.innerHTML = html;
            return div.textContent || div.innerText || '';
        }

        function showConfirmModal(message, action) {
            if (isBootstrapAvailable()) {
                document.getElementById('modalBody').innerHTML = message;
                pendingAction = action;
                new bootstrap.Modal(document.getElementById('confirmModal')).show();
            } else {
                const confirmed = window.confirm(sanitizeText(message));
                if (confirmed && typeof action === 'function') {
                    action();
                }
            }
        }

        function executeAction() {
            if (pendingAction) {
                pendingAction();
            }
        }

        function showSuccessModal(message) {
            if (isBootstrapAvailable()) {
                document.getElementById('successBody').innerHTML = message;
                new bootstrap.Modal(document.getElementById('successModal')).show();
            } else {
                window.alert(message);
            }
        }

        function showErrorModal(message) {
            if (isBootstrapAvailable()) {
                document.getElementById('errorBody').innerHTML = message;
                new bootstrap.Modal(document.getElementById('errorModal')).show();
            } else {
                window.alert('Error: ' + message);
            }
        }

        function showRejectionModal(action) {
            pendingRejectionAction = action;
            if (isBootstrapAvailable()) {
                document.getElementById('rejectionReason').value = '';
                new bootstrap.Modal(document.getElementById('rejectionModal')).show();
            } else {
                const reason = window.prompt('Reason for rejection:');
                if (reason !== null && reason.trim() !== '') {
                    action(reason.trim());
                } else if (reason !== null) {
                    showErrorModal('Please provide a reason for rejection');
                }
            }
        }

        function submitRejection() {
            const reason = document.getElementById('rejectionReason').value.trim();
            if (!reason) {
                showErrorModal('Please provide a reason for rejection');
                return;
            }
            if (isBootstrapAvailable()) {
                bootstrap.Modal.getInstance(document.getElementById('rejectionModal')).hide();
            }
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
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
                    body: JSON.stringify({rating: selectedRating})
                })
                .then(r => r.json())
                .then(d => {
                    if (d.success) {
                        if (isBootstrapAvailable()) {
                            bootstrap.Modal.getInstance(document.getElementById('ratingModal')).hide();
                        }
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
            if (isBootstrapAvailable()) {
                new bootstrap.Modal(document.getElementById('ratingModal')).show();
            } else {
                const rating = window.prompt('Enter rating between 1 and 5:');
                const value = parseInt(rating, 10);
                if (!Number.isNaN(value) && value >= 1 && value <= 5) {
                    setRating(value);
                    submitRating();
                } else if (rating !== null) {
                    showErrorModal('Invalid rating. Please enter a number between 1 and 5.');
                }
            }
        }

        function saveBook(bookId) {
            showConfirmModal(
                '<i class="fas fa-bookmark"></i> <strong>Save Book?</strong><br><small>This book will be added to your saved collection.</small>',
                function() {
                    fetch('/api/save-book/' + bookId, {method: 'POST', credentials: 'same-origin'})
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
                    fetch('/api/unsave-book/' + bookId, {method: 'POST', credentials: 'same-origin'})
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
    
