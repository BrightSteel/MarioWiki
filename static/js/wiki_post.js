var editQuill;

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

window.addEventListener("DOMContentLoaded", function() {
  
  let postContainer = document.getElementById("main-wiki");
  let id = postContainer.getAttribute("data-id");
  let formId = "form" + id;
  console.log("this is id: "+ id)
    
  function cancelForm() {
    let form = document.getElementById(formId);
    let toolBar = document.getElementsByClassName('ql-toolbar', 'ql-snow');
    toolBar[0].parentNode.removeChild(toolBar[0]);
    form.style.display = "none";
    let editBtn = document.getElementById("edit-btn");
    editBtn.disabled = false;
  }
  
  async function deleteDiscussion() {
    try{
      result = await fetch('/post/isLoggedInAuthor/'+id);
      console.log(result)
      if(!result.ok) throw new Error("not ok");
      try{
        if (confirm('Are you sure you want to delete this post?')){
          result = await fetch('/post/deleteDiscussion/'+id);
          if(!result.ok) throw new Error("not ok");
          window.location.href = window.location.origin;
        }
      }catch(error){
        console.log(error)
      }
    }catch(error){
      alert("You cannot delete this post because you are not the author")
    }
  }
  
  let cancelButton = document.getElementById("cancel-btn");
  cancelButton.onclick = cancelForm;
  
  let editButton = document.getElementById("edit-btn");
  if (editButton) {
    editButton.onclick = showEdit;
  }
  
  let deleteButton = document.getElementById("delete-btn");
  if (deleteButton) {
    deleteButton.onclick = deleteDiscussion;
  }
  
  async function showEdit(){
    let editBtn = document.getElementById("edit-btn");
    editBtn.disabled = true;
  
    try {
      let post = await fetch('/post/wikipostDetail/'+id);
      if(!post.ok) throw new Error("not ok");
      result = await post.json();
      postContent = result.post_content
      editorId = "#editor" + id;
      console.log("this is editorId: " + editorId)
      editQuill = new Quill(editorId, {
        modules: {
          toolbar: toolbarOptions
        },
        placeholder: 'Enter your message',
        theme: 'snow'
      });
      console.log(editQuill)
      // This pre-sets the quill editors with the previous message from the database
      // that editor corresponds to.
      editQuill.root.innerHTML = postContent;
      let form = document.getElementById(formId);
      form.style.display = "block";
    } catch (error) {
      console.log(error)
    }
  }
  
  let edit_form = document.getElementById(formId);
  edit_form.onsubmit = submit_edit;
  
  function submit_edit() {
    let inputId = "update"+id;
    let hidden_input = document.getElementById(inputId);
    hidden_input.value = editQuill.root.innerHTML;
  }

  async function load (){
    const LOADING = document.getElementById("loading-url").textContent;
    const ERROR = document.getElementById("error-url").textContent;
    //get all like button divs
    like_buttons = document.getElementsByClassName("button_like")
    console.log(like_buttons)
    for (let i = 0; i < like_buttons.length; i++) {
      let like_div = like_buttons[i]; 
      let id = like_div.getAttribute("data-id")
            
      // create an image for status update.
      let image = document.createElement("img")
      image.src = LOADING
      like_div.append(image)
    
      try {    
        // get the like count.
        let result = await fetch('/post/'+id+'/like')
        if(!result.ok) throw new Error("not ok");
        result = await result.json()
        let likes = result.likes
        let you_like = result.you_like
   
        // function for updating display.
        function update() {
          like_div.textContent = likes
          let likeButton = document.getElementById("like_button_" + id)
          if(you_like) {
            likeButton.classList.add('fa-solid')
            likeButton.style['color'] = 'red';
          } else {
            likeButton.classList.remove('fa-solid')
            likeButton.style['color'] = '';
          }
        }
        update();
    
        // on click
        let likeButton = document.getElementById("like_button_" + id)
        likeButton.addEventListener("click", async () => {
    
          // like or unlike
          try {
            let method = "POST"
            if (you_like) {
              method = "DELETE"
            }
            // set the spinner
            like_div.textContent=""
            like_div.append(image);
            // send the reqest
            let result = await fetch('/post/'+id+'/like1', {method})
            if(!result.ok) throw new Error("not ok");
            // process results
            result = await result.json()
            likes = result.likes
            you_like = result.you_like
            update()
          } catch (error) {
            console.log(error)
            like_div.textContent="Please login to like post";
          }
        })
      } catch (error) {
        console.log(error)
        like_div.textContent="";
        image.src = ERROR
        like_div.append(image);
      }
    }
  }
  load();
});