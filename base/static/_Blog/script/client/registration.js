
$(document).ready(function() {

    // Function to toggle password visibility
    function togglePasswordView() {
        var passwordInput = $('#password');
        var confirmPasswordInput = $('#confirm-password');
        
        if (passwordInput.attr('type') === 'password') {
            passwordInput.attr('type', 'text');
            confirmPasswordInput.attr('type', 'text');
        } else {
            passwordInput.attr('type', 'password');
            confirmPasswordInput.attr('type', 'password');
        }
    }

    // Toggle password view on button mousedown
    $('#password-view').on('mousedown', function() {
        togglePasswordView();
    });


    // Function to check if a password is valid and strong
    function is_valid_strong_password(password) {
        var passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{}\[\]:;"'<>,.?/\\|]).{8,}$/;
        return passwordPattern.test(password);
    }

    // Enable submit button if conditions are met
    function updateSubmitButtonState() {
        var username = $('#username').val();
        var password = $('#password').val();
        var confirmPassword = $('#confirm-password').val();
        var submitButton = $('#submit-form');

        if (username && password === confirmPassword && is_valid_strong_password(password)) {
            submitButton.prop('disabled', false);
        } else {
            submitButton.prop('disabled', true);
        }
    }

    // Call the function on input change
    $('#username, #password, #confirm-password').on('input', function() {
        updateSubmitButtonState();
    });
});