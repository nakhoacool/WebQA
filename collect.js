let dd = document.getElementsByTagName("dd") 
let a = document.getElementById("page-main-content")
Array.from(dd).forEach(e => {
    e.style.display = "block"
})
a.innerText
