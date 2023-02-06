/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
        "./base/templates/_Blog/**/*.html",
        "./base/templates/_Blog/*.html",            
        // Templates within theme app (e.g. base.html)
        './base/templates/_Blog/*.html',
        // Templates in other apps
        //'../../templates/**/*.html',
        // Ignore files in node_modules
        '!node_modules',
        // Include JavaScript files that might contain Tailwind CSS classes
        //'./base/static/Blog/script/*.js',
        //'./base/static/Blog/**/*.js',
        // Include Python files that might contain Tailwind CSS classes
        '../../**/*.py',
        "./node_modules/flowbite/**/*.js"
],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
}