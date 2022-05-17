// script runs after <body> loads

var searchBtn = document.querySelector("#search-btn")
var searchTxt = document.querySelector("#search-text")
var searchCat = document.querySelector("#category")
var dirListNode = document.querySelector(".directory-list")
var dirListItems = document.querySelectorAll(".directory-link")
searchBtn.addEventListener("click", (e)=>{
    var term = searchTxt.value
    if(term.trim()!="" && term!=null){
        if(searchCat.value=="this"){
            searchThisDirectory(term)
        } else if (searchCat.value=="child") {

        } else if (searchCat.value=="all") {

        }
    } else {
        dirListNode.replaceChildren(...dirListItems)
    }
})

function searchThisDirectory(term) {
    var filter = Object.values(dirListItems).filter((f)=>{
        return f.getAttribute("meta-name").includes(term)
    })
    dirListNode.replaceChildren(...filter)
}