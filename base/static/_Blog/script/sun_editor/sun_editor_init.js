post_editor = document.getElementById('post_editor');

// ex) A codehighlight plugin that appends the contents of the input element to the editor
var plugin_codehighlight = {
    // @Required @Unique
    // plugin name
    name: 'custom_plugin_codehighlight',

    // @Required
    // data display
    display: 'submenu',

    // @Options
    title: 'Code syntax highlight',
    buttonClass: '', 
    innerHTML: '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <title>language_json</title> <rect width="24" height="24" fill="none"></rect> <path d="M5,3H7V5H5v5a2,2,0,0,1-2,2,2,2,0,0,1,2,2v5H7v2H5c-1.07-.27-2-.9-2-2V15a2,2,0,0,0-2-2H0V11H1A2,2,0,0,0,3,9V5A2,2,0,0,1,5,3M19,3a2,2,0,0,1,2,2V9a2,2,0,0,0,2,2h1v2H23a2,2,0,0,0-2,2v4a2,2,0,0,1-2,2H17V19h2V14a2,2,0,0,1,2-2,2,2,0,0,1-2-2V5H17V3h2M12,15a1,1,0,1,1-1,1,1,1,0,0,1,1-1M8,15a1,1,0,1,1-1,1,1,1,0,0,1,1-1m8,0a1,1,0,1,1-1,1A1,1,0,0,1,16,15Z"></path> </g></svg>',

    // @Required
    // add function - It is called only once when the plugin is first run.
    // This function generates HTML to append and register the event.
    // arguments - (core : core object, targetElement : clicked button element)
    add: function (core, targetElement) {

        // @Required
        // Registering a namespace for caching as a plugin name in the context object
        const context = core.context;
        context.customSubmenu = {
            targetButton: targetElement,
            textElement: null,
            currentSpan: null
        };

        // Generate submenu HTML
        // Always bind "core" when calling a plugin function
        let listDiv = this.setSubmenu(core);

        // Input tag caching
        context.customSubmenu.textElement = listDiv.querySelector('input');

        // You must bind "core" object when registering an event.
        /** add event listeners */
        listDiv.querySelector('.se-btn-primary').addEventListener('click', this.onClick.bind(core));

        // @Required
        // You must add the "submenu" element using the "core.initMenuTarget" method.
        /** append target button menu */
        core.initMenuTarget(this.name, targetElement, listDiv);
    },

    setSubmenu: function (core) {
        const listDiv = core.util.createElement('DIV');
        // @Required
        // A "se-submenu" class is required for the top level element.
        listDiv.className = 'se-menu-container se-submenu se-list-layer';
        listDiv.innerHTML = '' +
            '<div class="se-list-inner">' +
                '<ul class="se-list-basic" style="width: 230px;">' +
                    '<li>' +
                        '<div class="se-form-group">' +
                            '<input class="se-input-form" type="text" placeholder="language python,java" style="border: 1px solid #CCC;" />' +
                            '<button type="button" class="se-btn-primary se-tooltip">' +
                                '<strong>Add</strong>' +
                                '<span class="se-tooltip-inner">' +
                                    '<span class="se-tooltip-text">Append code block</span>' +
                                '</span>' +
                            '</button>' +
                        '</div>' +
                    '</li>' +
                '</ul>' +
            '</div>';

        return listDiv;
    },

    // @Override core
    // Plugins with active methods load immediately when the editor loads.
    // Called each time the selection is moved.
    active: function (element) {
        // If no tag matches, the "element" argument is called with a null value.
        if (!element) {
            this.util.removeClass(this.context.customSubmenu.targetButton, 'active');
            this.context.customSubmenu.textElement.value = '';
            this.context.customSubmenu.currentSpan = null;
        } else if (this.util.hasClass(element, 'se-custom-tag')) {
            this.util.addClass(this.context.customSubmenu.targetButton, 'active');
            this.context.customSubmenu.textElement.value = element.textContent;
            this.context.customSubmenu.currentSpan = element;
            return true;
        }

        return false;
    },

    // @Override submenu
    // Called after the submenu has been rendered
    on: function () {
        this.context.customSubmenu.textElement.focus();
    },


    onClick: function () {
        const value = this.context.customSubmenu.textElement.value.trim();
        if (!value) return;

        const span = this.context.customSubmenu.currentSpan;
        if (span) {
            span.textContent = value;
            this.setRange(span, 1, span, 1);
        } else {
            this.functions.insertHTML('<pre><code class="language-'+value+'">' + 'Write your '+ value +' code' + '</code></pre>', true);
            this.context.customSubmenu.textElement.value = '';
        }
        this.submenuOff();
    }
};


if (post_editor){
    var editor = SUNEDITOR.create('post_editor', {
        plugins: [plugin_codehighlight],
        display: 'block',
        width: '100%',
        height: '400px',
        popupDisplay: 'full',
        charCounter: true,
        charCounterLabel: 'Characters :',
        imageUploadHeader: {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
            // Add any other custom headers if needed
        },
        imageUploadUrl: '/dashboard/upload-image',
        imageGalleryUrl: '/dashboard/suneditor_gallery',
        buttonList: [
            // default
            ['undo', 'redo'],
            ['font', 'fontSize', 'formatBlock'],
            ['custom_plugin_codehighlight'],
            ['paragraphStyle', 'blockquote'],
            ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
            ['fontColor', 'hiliteColor', 'textStyle'],
            ['removeFormat'],
            ['outdent', 'indent'],
            ['align', 'horizontalRule', 'list', 'lineHeight'],
            ['table', 'link', 'image', 'video', 'audio', 'math'],
            ['imageGallery'],
            ['fullScreen', 'showBlocks', 'codeView'],
            ['preview', 'print'],
            ['save', 'template'],
            // (min-width: 1546)
            ['%1546', [
                ['undo', 'redo'],
                ['font', 'fontSize', 'formatBlock'],
                ['custom_plugin_codehighlight'],
                ['paragraphStyle', 'blockquote'],
                ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                ['fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                ['table', 'link', 'image', 'video', 'audio', 'math'],
                ['imageGallery'],
                ['fullScreen', 'showBlocks', 'codeView'],
                ['-right', ':i-More Misc-default.more_vertical', 'preview', 'print', 'save', 'template']
            ]],
            // (min-width: 1455)
            ['%1455', [
                ['undo', 'redo'],
                ['font', 'fontSize', 'formatBlock'],
                ['custom_plugin_codehighlight'],
                ['paragraphStyle', 'blockquote'],
                ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                ['fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                ['table', 'link', 'image', 'video', 'audio', 'math'],
                ['imageGallery'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
            ]],
            // (min-width: 1326)
            ['%1326', [
                ['undo', 'redo'],
                ['font', 'fontSize', 'formatBlock'],
                ['custom_plugin_codehighlight'],
                ['paragraphStyle', 'blockquote'],
                ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                ['fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template'],
                ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery']
            ]],
            // (min-width: 1123)
            ['%1123', [
                ['undo', 'redo'],
                [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock','custom_plugin_codehighlight', 'paragraphStyle', 'blockquote'],
                ['bold', 'underline', 'italic', 'strike', 'subscript', 'superscript'],
                ['fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template'],
                ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery']
            ]],
            // (min-width: 817)
            ['%817', [
                ['undo', 'redo'],
                [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock', 'custom_plugin_codehighlight','paragraphStyle', 'blockquote'],
                ['bold', 'underline', 'italic', 'strike'],
                [':t-More Text-default.more_text', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template'],
                ['-right', ':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery']
            ]],
            // (min-width: 673)
            ['%673', [
                ['undo', 'redo'],
                [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock','custom_plugin_codehighlight', 'paragraphStyle', 'blockquote'],
                [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                ['align', 'horizontalRule', 'list', 'lineHeight'],
                [':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
            ]],
            // (min-width: 525)
            ['%525', [
                ['undo', 'redo'],
                [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock','custom_plugin_codehighlight', 'paragraphStyle', 'blockquote'],
                [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle'],
                ['removeFormat'],
                ['outdent', 'indent'],
                [':e-More Line-default.more_horizontal', 'align', 'horizontalRule', 'list', 'lineHeight'],
                [':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
            ]],
            // (min-width: 420)
            ['%420', [
                ['undo', 'redo'],
                [':p-More Paragraph-default.more_paragraph', 'font', 'fontSize', 'formatBlock','custom_plugin_codehighlight', 'paragraphStyle', 'blockquote'],
                [':t-More Text-default.more_text', 'bold', 'underline', 'italic', 'strike', 'subscript', 'superscript', 'fontColor', 'hiliteColor', 'textStyle', 'removeFormat'],
                [':e-More Line-default.more_horizontal', 'outdent', 'indent', 'align', 'horizontalRule', 'list', 'lineHeight'],
                [':r-More Rich-default.more_plus', 'table', 'link', 'image', 'video', 'audio', 'math', 'imageGallery'],
                ['-right', ':i-More Misc-default.more_vertical', 'fullScreen', 'showBlocks', 'codeView', 'preview', 'print', 'save', 'template']
            ]]
        ],
        placeholder: 'Start typing your content...',
        templates: [
            {
                name: 'Template-1',
                html: '<p>HTML source1</p>'
            },
            {
                name: 'Template-2',
                html: '<p>HTML source2</p>'
            }
        ],
        codeMirror: CodeMirror,
        katex: katex
    });

    //After initializing suneditor load saved content if found
    const url = window.location.href; // Get the current URL
    const savedValue = localStorage.getItem(url);
    if (savedValue !== null) {
        editor.setContents(savedValue)
    }
}
else{
    console.log('Post editor may not required.')
}

editor.save = () => { //Save editor content on local storage
    const url = window.location.href; // Get the current URL
    const editor_value = editor.getContents()
    localStorage.setItem(url, editor_value);
    console.log('Saved to local storage')
}
  