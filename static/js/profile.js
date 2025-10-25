var quill;

var toolbarOptions = [
  [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  [{ 'font': [] }],

  ['bold', 'italic', 'underline'],                  // toggled buttons
  ['blockquote'],

  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent

  ['clean']                                         // remove formatting button
];

window.addEventListener("load", function() {
 
  quill = new Quill('#editor-text', {
    theme: 'snow',
    placeholder: 'Please enter your bio...',
    modules:{
      toolbar: toolbarOptions,
    }
  });


  function update(){
    document.getElementById("update-form").style.display = "block";
    document.getElementById("upload-form").style.display = "block";
    document.getElementById("update-btn").style.display = "none";
  }

  let updatebtn = document.getElementById("update-btn");
  if (updatebtn){
    updatebtn.onclick = update;
  }

  document.getElementById("decline-btn").addEventListener("click", function(event){
    event.preventDefault();
    document.getElementById("update-form").style.display = "none";
    document.getElementById("upload-form").style.display = "none";
    document.getElementById("update-btn").style.display = "block";
  });
    
  let form = document.getElementById('update-form');
  let newbio = document.getElementById('postData');
  form.onsubmit = function () {
    newbio.value = quill.root.innerHTML;
  }

  document.querySelector('#upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const response = await fetch('/profile/upload', {
      method: 'POST',
      body: formData,
    });
    if (response.ok) {
      // Handle successful upload
      this.alert("Successfully updated your profile photo!");
      window.location.href = window.location.origin + "/profile"
    } else {
      // Handle upload failure
      this.alert("Updated failed, please try again.");
    }
  });

  async function removeFollower() {
    remove_buttons = document.getElementsByClassName("remove-btn")
    for (let i = 0; i < remove_buttons.length; i++) {
      removeBtn = remove_buttons[i]
      let following = removeBtn.getAttribute("data-id")
      removeBtn.addEventListener("click", async () => {
        try{
          if (confirm(`Are you sure you want to stop following ${following}?`)){
            let follower = removeBtn.getAttribute("data-id")
            let result = await fetch('/profile/remove/' + following)
            if(!result.ok) throw new Error("not ok");
            window.location.href = window.location.origin + "/profile";
          }
        }catch(error){
          console.log(error)
        }
      })
    }
  }
  removeFollower();

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