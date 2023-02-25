//Sun_editor theme change
function sun_theme(mode) {
    if ($("#suneditor_post_editor").length) {
        if (mode === "dark"){
            $("#suneditor_post_editor").css({
                "background-color": "#374151",
                "color": "white"
              });
        }else{
            $("#suneditor_post_editor").css({
                "background-color": "white",
                "color": "black"
              });
        }
    }
}
// It's best to inline this in `head` to avoid FOUC (flash of unstyled content) when changing pages or themes
if (
    localStorage.getItem('color-theme') === 'dark' ||
    (!('color-theme' in localStorage) &&
        window.matchMedia('(prefers-color-scheme: dark)').matches) //Find the OS theme & change it as system if manually not set yet
    ) {
    document.documentElement.classList.add('dark'); 
    sun_theme("dark") //Chaning mode of sun_editor
    } 
    else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches){
        document.documentElement.classList.add('dark')
        sun_theme("dark") //Chaning mode of sun_editor
    }
    else {
    document.documentElement.classList.remove('dark');
    sun_theme("light") //Chaning mode of sun_editor
    }
    
    var themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    var themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

    // Change the icons inside the button based on previous settings
    if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        themeToggleLightIcon.classList.remove('hidden');
    } else {
        themeToggleDarkIcon.classList.remove('hidden');
    }

    var themeToggleBtn = document.getElementById('theme-toggle');

    themeToggleBtn.addEventListener('click', function() {

        // toggle icons inside button
        themeToggleDarkIcon.classList.toggle('hidden');
        themeToggleLightIcon.classList.toggle('hidden');

        // if set via local storage previously
        if (localStorage.getItem('color-theme')) {
            if (localStorage.getItem('color-theme') === 'light') {
                document.documentElement.classList.add('dark');
                sun_theme("dark") //Chaning mode of sun_editor
                localStorage.setItem('color-theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                sun_theme("light") //Chaning mode of sun_editor
                localStorage.setItem('color-theme', 'light');
            }

        // if NOT set via local storage previously
        } else {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                sun_theme("light") //Chaning mode of sun_editor
                localStorage.setItem('color-theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                sun_theme("dark") //Chaning mode of sun_editor
                localStorage.setItem('color-theme', 'dark');
            }
        }
   }
);