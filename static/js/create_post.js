var quill;

// https://stackoverflow.com/questions/29008914/how-to-add-image-in-quill-js
var toolbarOptions = [
  ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
  ['blockquote'],

  [{ 'header': [2, 3, 4, false] }],                 // custom button values
  [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
  [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
  [{ 'direction': 'rtl' }],                         // text direction

  [ 'link', 'image'],                               // add's image support
  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  [{ 'font': [] }],
  [{ 'align': [] }],

  ['clean']                                         // remove formatting button
];

var bindings = {
  tab: {
    key: 9,
    handler: function() {
      this.quill.format('indent', '+1');
    }
  }
};

window.addEventListener('load', function () { 

  quill = new Quill('#editor', {
    theme: 'snow',
    placeholder: 'Compose an epic...',
    modules: {
      toolbar: toolbarOptions,
      keyboard: {
        bindings: bindings
      }
    }
  });

  const post_form = document.getElementById('postForm');
  post_form.onsubmit = submit_entry;
});

function submit_entry() {
  const hidden_input = document.getElementById('postData');
  hidden_input.value = quill.root.innerHTML;
}

function redirectHome() {
  location.href = window.location.origin;
}

// inspired by https://stackoverflow.com/questions/12368910/html-display-image-after-selecting-filename
// requires HTML5 capable browser for FileReader capabilities
function acceptThumbnail(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      document.getElementById('thumbnail-preview').src = e.target.result;
    };

    reader.readAsDataURL(input.files[0]);
  }
} 
