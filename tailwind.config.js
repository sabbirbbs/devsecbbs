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
const options = {
  defaultTabId: 'settings',
  activeClasses: 'dark:bg-gray-600 bg-gray-100 dark:text-white text-gray-900',
  inactiveClasses: 'text-gray-500 hover:text-gray-600 dark:text-gray-400 border-gray-100 hover:border-gray-300 dark:border-gray-700 dark:hover:text-gray-300',
  onShow: () => {
      console.log('tab is shown');
  }
};