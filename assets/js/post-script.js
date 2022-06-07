// script runs after <body> loads

var searchBtn = document.querySelector("#search-btn")
var searchTxt = document.querySelector("#search-text")
var searchCat = document.querySelector("#category")
var dirListNode = document.querySelector(".directory-list")
var dirListItems = document.querySelectorAll(".directory-link")
searchTxt.addEventListener("keyup", search)
searchBtn.addEventListener("click", search)

function search () {
    var term = searchTxt.value
    if(term.trim()!="" && term!=null){
        if(searchCat.value=="this"){
            searchThisDirectory(term)
        } else if (searchCat.value=="all") {
            // this will need some work
        }
    } else {
        dirListNode.replaceChildren(...dirListItems)
    }
}

function searchThisDirectory(term) {
    var filter = Object.values(dirListItems).filter((f)=>{
        return f.getAttribute("meta-name").toLowerCase().includes(term.toLowerCase())
    })
    dirListNode.replaceChildren(...filter)
}