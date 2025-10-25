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
