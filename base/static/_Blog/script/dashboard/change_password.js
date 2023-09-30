
$(document).ready(function() {

    // Function to toggle password visibility
    function togglePasswordView() {
        var old_passwordInput = $('#old-password');
        var passwordInput = $('#password');
        var confirmPasswordInput = $('#confirm-password');
        seenIcon = `<svg viewBox="0 0 24 24" class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <circle cx="12" cy="12" r="3.5" stroke="currentColor"></circle> <path d="M20.188 10.9343C20.5762 11.4056 20.7703 11.6412 20.7703 12C20.7703 12.3588 20.5762 12.5944 20.188 13.0657C18.7679 14.7899 15.6357 18 12 18C8.36427 18 5.23206 14.7899 3.81197 13.0657C3.42381 12.5944 3.22973 12.3588 3.22973 12C3.22973 11.6412 3.42381 11.4056 3.81197 10.9343C5.23206 9.21014 8.36427 6 12 6C15.6357 6 18.7679 9.21014 20.188 10.9343Z" stroke="currentColor"></path> </g></svg>`
        unseenIcon = `<svg viewBox="0 0 24 24" class="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M2.99902 3L20.999 21M9.8433 9.91364C9.32066 10.4536 8.99902 11.1892 8.99902 12C8.99902 13.6569 10.3422 15 11.999 15C12.8215 15 13.5667 14.669 14.1086 14.133M6.49902 6.64715C4.59972 7.90034 3.15305 9.78394 2.45703 12C3.73128 16.0571 7.52159 19 11.9992 19C13.9881 19 15.8414 18.4194 17.3988 17.4184M10.999 5.04939C11.328 5.01673 11.6617 5 11.9992 5C16.4769 5 20.2672 7.94291 21.5414 12C21.2607 12.894 20.8577 13.7338 20.3522 14.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>`
                
        if (passwordInput.attr('type') === 'password') {
            old_passwordInput.attr('type', 'text');
            passwordInput.attr('type', 'text');
            confirmPasswordInput.attr('type', 'text');
            $("#password-view").html(unseenIcon)
        } else {
            old_passwordInput.attr('type', 'password');
            passwordInput.attr('type', 'password');
            confirmPasswordInput.attr('type', 'password');
            $("#password-view").html(seenIcon)
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
        var old_pass = $('#old-password').val();
        var password = $('#password').val();
        var confirmPassword = $('#confirm-password').val();
        var submitButton = $('#submit-form');

        if (old_pass && password === confirmPassword && is_valid_strong_password(password)) {
            submitButton.prop('disabled', false);
        } else {
            submitButton.prop('disabled', true);
        }
    }

    // Call the function on input change
    $('#old-password, #password, #confirm-password').on('input', function() {
        updateSubmitButtonState();
    });

    //Check is the password is valid & matched or not
    // Get references to the password fields
    var passwordField = $('#password');
    var confirmPasswordField = $('#confirm-password');

    // Function to check password validity and match
    function checkPasswords() {
        var password = passwordField.val();
        var confirmPassword = confirmPasswordField.val();
        var regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{}\[\]:;"'<>,.?/\\|]).{8,}$/;

        // Reset Tailwind classes
        passwordField.removeClass('border-red-500');
        confirmPasswordField.removeClass('border-red-500');

        // Check if passwords match and meet regex after both fields have input
        if (password && confirmPassword) {
            if (password !== confirmPassword || !regex.test(password)) {
                if (password !== confirmPassword) {
                    confirmPasswordField.addClass('border-red-500');
                }
                if (!regex.test(password)) {
                    passwordField.addClass('border-red-500');
                }
            }
        }
    }

    // Attach event handlers to both password fields
    passwordField.on('input', checkPasswords);
    confirmPasswordField.on('input', checkPasswords);
});